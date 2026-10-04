output "lambda_function_arns" {
  value = { for k, v in aws_lambda_function.main : k => v.arn }
}

output "lambda_function_names" {
  value = { for k, v in aws_lambda_function.main : k => v.function_name }
}

output "lambda_invoke_arns" {
  value = { for k, v in aws_lambda_function.main : k => v.invoke_arn }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.ingest.repository_url
}

output "ecs_cluster_arn" {
  value = aws_ecs_cluster.ingest.arn
}

output "sfn_state_machine_arn" {
  value = aws_sfn_state_machine.ingest.arn
}

output "ingest_task_definition_arn" {
  value = aws_ecs_task_definition.ingest.arn
}
