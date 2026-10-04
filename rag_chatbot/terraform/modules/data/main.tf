terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
  }
}

resource "random_password" "master" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "aurora" {
  name_prefix             = "${var.name_prefix}-aurora-"
  recovery_window_in_days = 0
  tags                    = merge(var.tags, { Name = "${var.name_prefix}-aurora-secret" })
}

resource "aws_secretsmanager_secret_version" "aurora" {
  secret_id = aws_secretsmanager_secret.aurora.id
  secret_string = jsonencode({
    username = var.master_username
    password = random_password.master.result
    engine   = "postgres"
    host     = aws_rds_cluster.main.endpoint
    port     = 5432
    dbname   = var.database_name
  })
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.name_prefix}-aurora"
  subnet_ids = var.private_subnet_ids
  tags       = merge(var.tags, { Name = "${var.name_prefix}-aurora-subnets" })
}

resource "aws_rds_cluster" "main" {
  cluster_identifier          = "${var.name_prefix}-aurora"
  engine                      = "aurora-postgresql"
  engine_mode                 = "provisioned"
  engine_version              = var.engine_version
  database_name               = var.database_name
  master_username             = var.master_username
  master_password             = random_password.master.result
  db_subnet_group_name        = aws_db_subnet_group.main.name
  vpc_security_group_ids      = [var.aurora_security_group_id]
  storage_encrypted           = true
  kms_key_id                  = var.kms_key_arn
  backup_retention_period     = 7
  preferred_backup_window     = "03:00-04:00"
  deletion_protection         = var.deletion_protection
  skip_final_snapshot         = !var.deletion_protection
  final_snapshot_identifier   = var.deletion_protection ? "${var.name_prefix}-aurora-final" : null
  enable_http_endpoint        = false
  allow_major_version_upgrade = false

  serverlessv2_scaling_configuration {
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
  }

  tags = merge(var.tags, { Name = "${var.name_prefix}-aurora" })
}

resource "aws_rds_cluster_instance" "main" {
  identifier         = "${var.name_prefix}-aurora-1"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version

  tags = merge(var.tags, { Name = "${var.name_prefix}-aurora-instance" })
}
