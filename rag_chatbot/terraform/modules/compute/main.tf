terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.0"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  lambda_env = {
    AWS_NODEJS_CONNECTION_REUSE_ENABLED = "1"
    DOCUMENTS_TABLE                     = var.documents_table_name
    CHAT_SESSIONS_TABLE                 = var.chat_sessions_table_name
    CHAT_MESSAGES_TABLE                 = var.chat_messages_table_name
    SEMANTIC_CACHE_TABLE                = var.semantic_cache_table_name
    WS_CONNECTIONS_TABLE                = var.ws_connections_table_name
    DOCS_BUCKET                         = var.docs_bucket_id
    KMS_KEY_ID                          = var.kms_key_id
    AURORA_SECRET_ARN                   = var.aurora_secret_arn
    CLAUDE_MODEL_ID                     = var.claude_model_id
    EMBED_MODEL_ID                      = var.embed_model_id
    TOP_K                               = tostring(var.top_k)
    CACHE_TTL_SECONDS                   = tostring(var.cache_ttl_seconds)
    MAX_UPLOAD_BYTES                    = tostring(var.max_upload_bytes)
    NAME_PREFIX                         = var.name_prefix
    WS_ENDPOINT_PARAM                   = "/${var.name_prefix}/websocket-management-endpoint"
  }

  lambda_functions = {
    chat       = { handler = "handler.handler", timeout = 60, memory = 1024, vpc = true }
    upload     = { handler = "handler.handler", timeout = 30, memory = 256, vpc = false }
    history    = { handler = "handler.handler", timeout = 30, memory = 256, vpc = false }
    connect    = { handler = "handler.handler", timeout = 10, memory = 128, vpc = false }
    disconnect = { handler = "handler.handler", timeout = 10, memory = 128, vpc = false }
  }
}

data "archive_file" "lambda" {
  for_each    = local.lambda_functions
  type        = "zip"
  # Bundled TypeScript output from `npm run build` in backend/lambdas
  source_dir  = "${var.backend_path}/lambdas/dist/${each.key}"
  output_path = "${path.module}/build/${each.key}.zip"
}

resource "aws_iam_role" "lambda" {
  for_each = local.lambda_functions
  name     = "${var.name_prefix}-${each.key}-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  for_each   = local.lambda_functions
  role       = aws_iam_role.lambda[each.key].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  for_each   = { for k, v in local.lambda_functions : k => v if v.vpc }
  role       = aws_iam_role.lambda[each.key].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "lambda_app" {
  for_each = local.lambda_functions
  name     = "${var.name_prefix}-${each.key}-policy"
  role     = aws_iam_role.lambda[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        {
          Sid    = "DynamoDBAccess"
          Effect = "Allow"
          Action = [
            "dynamodb:GetItem",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:Query",
            "dynamodb:Scan"
          ]
          Resource = [
            var.documents_table_arn,
            var.chat_sessions_table_arn,
            var.chat_messages_table_arn,
            "${var.chat_messages_table_arn}/index/*",
            var.semantic_cache_table_arn,
            var.ws_connections_table_arn
          ]
        },
        {
          Sid      = "Logs"
          Effect   = "Allow"
          Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
          Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
        }
      ],
      each.key == "upload" ? [
        {
          Sid      = "S3Presign"
          Effect   = "Allow"
          Action   = ["s3:PutObject", "s3:AbortMultipartUpload"]
          Resource = "${var.docs_bucket_arn}/uploads/*"
        },
        {
          Sid      = "KMSForUpload"
          Effect   = "Allow"
          Action   = ["kms:Encrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
          Resource = [var.kms_key_arn]
        }
      ] : [],
      each.key == "chat" ? [
        {
          Sid    = "BedrockInvoke"
          Effect = "Allow"
          Action = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
          Resource = [
            "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-5-5",
            "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0",
            "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:inference-profile/global.anthropic.claude-sonnet-5-5"
          ]
        },
        {
          Sid      = "Secrets"
          Effect   = "Allow"
          Action   = ["secretsmanager:GetSecretValue"]
          Resource = [var.aurora_secret_arn]
        },
        {
          Sid      = "ManageConnections"
          Effect   = "Allow"
          Action   = ["execute-api:ManageConnections"]
          Resource = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*/@connections/*"
        },
        {
          Sid      = "ReadWsEndpointParam"
          Effect   = "Allow"
          Action   = ["ssm:GetParameter"]
          Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.name_prefix}/websocket-management-endpoint"
        }
      ] : []
    )
  })
}

resource "aws_cloudwatch_log_group" "lambda" {
  for_each          = local.lambda_functions
  name              = "/aws/lambda/${var.name_prefix}-${each.key}"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_lambda_function" "main" {
  for_each         = local.lambda_functions
  function_name    = "${var.name_prefix}-${each.key}"
  role             = aws_iam_role.lambda[each.key].arn
  handler          = each.value.handler
  runtime          = "nodejs20.x"
  filename         = data.archive_file.lambda[each.key].output_path
  source_code_hash = data.archive_file.lambda[each.key].output_base64sha256
  timeout          = each.value.timeout
  memory_size      = each.value.memory
  layers           = each.key == "chat" ? [aws_lambda_layer_version.pg.arn] : []

  environment {
    variables = merge(
      local.lambda_env,
      each.key == "connect" ? {
        COGNITO_ISSUER    = var.cognito_issuer
        COGNITO_CLIENT_ID = var.cognito_client_id
      } : {}
    )
  }

  dynamic "vpc_config" {
    for_each = each.value.vpc ? [1] : []
    content {
      subnet_ids         = var.private_subnet_ids
      security_group_ids = [var.lambda_security_group_id]
    }
  }

  reserved_concurrent_executions = each.key == "chat" ? var.chat_reserved_concurrency : null

  depends_on = [aws_cloudwatch_log_group.lambda]
  tags       = var.tags
}

# Optional thin layer placeholder; package real pg driver during deploy
resource "aws_lambda_layer_version" "pg" {
  layer_name          = "${var.name_prefix}-pg"
  filename            = data.archive_file.pg_layer.output_path
  source_code_hash    = data.archive_file.pg_layer.output_base64sha256
  compatible_runtimes = ["nodejs20.x"]
  description         = "PostgreSQL client dependencies for chat Lambda"
}

data "archive_file" "pg_layer" {
  type        = "zip"
  source_dir  = "${var.backend_path}/layers/pg"
  output_path = "${path.module}/build/pg-layer.zip"
}

# --- ECR + Fargate Spot ingest ---

resource "aws_ecr_repository" "ingest" {
  name                 = "${var.name_prefix}-pdf-ingest"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
  tags = var.tags
}

resource "aws_ecs_cluster" "ingest" {
  name = "${var.name_prefix}-ingest"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = var.tags
}

resource "aws_ecs_cluster_capacity_providers" "ingest" {
  cluster_name       = aws_ecs_cluster.ingest.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
    base              = 0
  }
}

resource "aws_cloudwatch_log_group" "ingest" {
  name              = "/ecs/${var.name_prefix}-pdf-ingest"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.name_prefix}-ecs-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.name_prefix}-ecs-task"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "ecs_task" {
  name = "${var.name_prefix}-ecs-task-policy"
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "S3ReadDocs"
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${var.docs_bucket_arn}/uploads/*"
      },
      {
        Sid      = "KMSDecrypt"
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:DescribeKey"]
        Resource = [var.kms_key_arn]
      },
      {
        Sid      = "DynamoDocs"
        Effect   = "Allow"
        Action   = ["dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:PutItem"]
        Resource = [var.documents_table_arn]
      },
      {
        Sid      = "Secrets"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [var.aurora_secret_arn]
      },
      {
        Sid    = "BedrockEmbed"
        Effect = "Allow"
        Action = ["bedrock:InvokeModel"]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0"
        ]
      }
    ]
  })
}

resource "aws_ecs_task_definition" "ingest" {
  family                   = "${var.name_prefix}-pdf-ingest"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "2048"
  memory                   = "4096"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "pdf-ingest"
    image     = "${aws_ecr_repository.ingest.repository_url}:latest"
    essential = true
    environment = [
      { name = "DOCUMENTS_TABLE", value = var.documents_table_name },
      { name = "DOCS_BUCKET", value = var.docs_bucket_id },
      { name = "AURORA_SECRET_ARN", value = var.aurora_secret_arn },
      { name = "EMBED_MODEL_ID", value = var.embed_model_id },
      { name = "AWS_REGION", value = data.aws_region.current.name }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ingest.name
        awslogs-region        = data.aws_region.current.name
        awslogs-stream-prefix = "ingest"
      }
    }
  }])

  tags = var.tags
}

resource "aws_iam_role" "sfn" {
  name = "${var.name_prefix}-sfn"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "states.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "sfn" {
  name = "${var.name_prefix}-sfn-policy"
  role = aws_iam_role.sfn.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "RunFargate"
        Effect   = "Allow"
        Action   = ["ecs:RunTask"]
        Resource = [aws_ecs_task_definition.ingest.arn]
      },
      {
        Sid      = "PassRoles"
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource = [aws_iam_role.ecs_task.arn, aws_iam_role.ecs_task_execution.arn]
      },
      {
        Sid      = "Events"
        Effect   = "Allow"
        Action   = ["ecs:StopTask", "ecs:DescribeTasks"]
        Resource = "*"
      },
      {
        Sid      = "EventsManaged"
        Effect   = "Allow"
        Action   = ["events:PutTargets", "events:PutRule", "events:DescribeRule"]
        Resource = "*"
      },
      {
        Sid      = "DLQ"
        Effect   = "Allow"
        Action   = ["sqs:SendMessage"]
        Resource = [var.ingest_dlq_arn]
      },
      {
        Sid    = "SFNLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogDelivery",
          "logs:GetLogDelivery",
          "logs:UpdateLogDelivery",
          "logs:DeleteLogDelivery",
          "logs:ListLogDeliveries",
          "logs:PutResourcePolicy",
          "logs:DescribeResourcePolicies",
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_sfn_state_machine" "ingest" {
  name     = "${var.name_prefix}-pdf-ingest"
  role_arn = aws_iam_role.sfn.arn

  definition = jsonencode({
    Comment = "PDF ingest via Fargate Spot"
    StartAt = "RunIngestTask"
    States = {
      RunIngestTask = {
        Type     = "Task"
        Resource = "arn:aws:states:::ecs:runTask.sync"
        Parameters = {
          Cluster        = aws_ecs_cluster.ingest.arn
          TaskDefinition = aws_ecs_task_definition.ingest.arn
          NetworkConfiguration = {
            AwsvpcConfiguration = {
              Subnets        = var.private_subnet_ids
              SecurityGroups = [var.fargate_security_group_id]
              AssignPublicIp = "DISABLED"
            }
          }
          CapacityProviderStrategy = [{
            CapacityProvider = "FARGATE_SPOT"
            Weight           = 1
            Base             = 0
          }]
          Overrides = {
            ContainerOverrides = [{
              Name            = "pdf-ingest"
              "Environment.$" = "$.containerEnv"
            }]
          }
        }
        Retry = [{
          ErrorEquals     = ["States.TaskFailed"]
          IntervalSeconds = 30
          MaxAttempts     = 2
          BackoffRate     = 2
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next        = "SendToDLQ"
        }]
        End = true
      }
      SendToDLQ = {
        Type     = "Task"
        Resource = "arn:aws:states:::sqs:sendMessage"
        Parameters = {
          QueueUrl = var.ingest_dlq_url
          "MessageBody.$" = "$"
        }
        End = true
      }
    }
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.sfn.arn}:*"
    include_execution_data = true
    level                  = "ERROR"
  }

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "sfn" {
  name              = "/aws/vendedlogs/states/${var.name_prefix}-pdf-ingest"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_iam_role" "sfn_events" {
  name = "${var.name_prefix}-sfn-events"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "sfn_events" {
  name = "${var.name_prefix}-sfn-events-policy"
  role = aws_iam_role.sfn_events.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["states:StartExecution"]
      Resource = [aws_sfn_state_machine.ingest.arn]
    }]
  })
}

resource "aws_cloudwatch_event_rule" "s3_upload" {
  name        = "${var.name_prefix}-docs-created"
  description = "Start ingest when a PDF is uploaded"
  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"]
    detail = {
      bucket = { name = [var.docs_bucket_id] }
      object = { key = [{ prefix = "uploads/" }] }
    }
  })
  tags = var.tags
}

resource "aws_cloudwatch_event_target" "sfn" {
  rule      = aws_cloudwatch_event_rule.s3_upload.name
  target_id = "StartIngest"
  arn       = aws_sfn_state_machine.ingest.arn
  role_arn  = aws_iam_role.sfn_events.arn

  input_transformer {
    input_paths = {
      bucket = "$.detail.bucket.name"
      key    = "$.detail.object.key"
    }
    input_template = <<EOF
{
  "containerEnv": [
    {"Name": "S3_BUCKET", "Value": <bucket>},
    {"Name": "S3_KEY", "Value": <key>}
  ]
}
EOF
  }
}

resource "aws_s3_bucket_notification" "docs_eventbridge" {
  bucket      = var.docs_bucket_id
  eventbridge = true
}
