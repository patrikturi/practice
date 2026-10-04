output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "lambda_security_group_id" {
  value = aws_security_group.lambda.id
}

output "fargate_security_group_id" {
  value = aws_security_group.fargate.id
}

output "aurora_security_group_id" {
  value = aws_security_group.aurora.id
}
