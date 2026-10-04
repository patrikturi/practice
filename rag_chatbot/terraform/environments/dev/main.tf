terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.0"
    }
  }

  # Uncomment and configure for remote state:
  # backend "s3" {
  #   bucket         = "YOUR_TF_STATE_BUCKET"
  #   key            = "rag-chatbot/dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "YOUR_TF_LOCK_TABLE"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "rag-chatbot"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

locals {
  name_prefix  = "${var.project}-${var.environment}"
  backend_path = abspath("${path.module}/../../../backend")
  tags         = { Component = "rag-chatbot" }
}

module "networking" {
  source             = "../../modules/networking"
  name_prefix        = local.name_prefix
  aws_region         = var.aws_region
  vpc_cidr           = var.vpc_cidr
  enable_nat_gateway = var.enable_nat_gateway
  tags               = local.tags
}

module "storage" {
  source      = "../../modules/storage"
  name_prefix = local.name_prefix
  tags        = local.tags
}

module "data" {
  source                   = "../../modules/data"
  name_prefix              = local.name_prefix
  private_subnet_ids       = module.networking.private_subnet_ids
  aurora_security_group_id = module.networking.aurora_security_group_id
  kms_key_arn              = module.storage.kms_key_arn
  min_capacity             = var.aurora_min_capacity
  max_capacity             = var.aurora_max_capacity
  deletion_protection      = var.deletion_protection
  tags                     = local.tags
}

module "cognito" {
  source        = "../../modules/cognito"
  name_prefix   = local.name_prefix
  domain_prefix = var.cognito_domain_prefix
  callback_urls = var.cognito_callback_urls
  logout_urls   = var.cognito_logout_urls
  tags          = local.tags
}

module "compute" {
  source                      = "../../modules/compute"
  name_prefix                 = local.name_prefix
  backend_path                = local.backend_path
  private_subnet_ids          = module.networking.private_subnet_ids
  lambda_security_group_id    = module.networking.lambda_security_group_id
  fargate_security_group_id   = module.networking.fargate_security_group_id
  docs_bucket_id              = module.storage.docs_bucket_id
  docs_bucket_arn             = module.storage.docs_bucket_arn
  kms_key_arn                 = module.storage.kms_key_arn
  kms_key_id                  = module.storage.kms_key_id
  documents_table_name        = module.storage.documents_table_name
  documents_table_arn         = module.storage.documents_table_arn
  chat_sessions_table_name    = module.storage.chat_sessions_table_name
  chat_sessions_table_arn     = module.storage.chat_sessions_table_arn
  chat_messages_table_name    = module.storage.chat_messages_table_name
  chat_messages_table_arn     = module.storage.chat_messages_table_arn
  semantic_cache_table_name   = module.storage.semantic_cache_table_name
  semantic_cache_table_arn    = module.storage.semantic_cache_table_arn
  ws_connections_table_name   = module.storage.ws_connections_table_name
  ws_connections_table_arn    = module.storage.ws_connections_table_arn
  aurora_secret_arn           = module.data.secret_arn
  ingest_dlq_arn              = module.storage.ingest_dlq_arn
  ingest_dlq_url              = module.storage.ingest_dlq_url
  cognito_issuer    = module.cognito.issuer
  cognito_client_id = module.cognito.client_id
  claude_model_id   = var.claude_model_id
  embed_model_id    = var.embed_model_id
  tags              = local.tags

  depends_on = [module.storage, module.data, module.networking, module.cognito]
}

module "api" {
  source                = "../../modules/api"
  name_prefix           = local.name_prefix
  cognito_client_id     = module.cognito.client_id
  cognito_issuer        = module.cognito.issuer
  lambda_invoke_arns    = module.compute.lambda_invoke_arns
  lambda_function_names = module.compute.lambda_function_names
  cors_allow_origins    = var.cors_allow_origins
  waf_rate_limit        = var.waf_rate_limit
  tags                  = local.tags
}

# Break compute↔API cycle: chat Lambda reads this at runtime for ManageConnections
resource "aws_ssm_parameter" "ws_management_endpoint" {
  name  = "/${local.name_prefix}/websocket-management-endpoint"
  type  = "String"
  value = module.api.websocket_management_endpoint
  tags  = local.tags
}

module "frontend" {
  source      = "../../modules/frontend"
  name_prefix = local.name_prefix
  tags        = local.tags
}

module "observability" {
  source             = "../../modules/observability"
  name_prefix        = local.name_prefix
  logs_bucket_id     = module.storage.logs_bucket_id
  logs_bucket_arn    = module.storage.logs_bucket_arn
  chat_function_name = module.compute.lambda_function_names["chat"]
  aurora_cluster_id  = module.data.cluster_id
  tags               = local.tags
}
