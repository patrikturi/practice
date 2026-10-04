output "cluster_endpoint" {
  value = aws_rds_cluster.main.endpoint
}

output "cluster_arn" {
  value = aws_rds_cluster.main.arn
}

output "cluster_id" {
  value = aws_rds_cluster.main.id
}

output "database_name" {
  value = var.database_name
}

output "secret_arn" {
  value = aws_secretsmanager_secret.aurora.arn
}

output "master_username" {
  value = var.master_username
}
