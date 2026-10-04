output "cloudtrail_arn" {
  value = aws_cloudtrail.main.arn
}

output "dashboard_name" {
  value = aws_cloudwatch_dashboard.main.dashboard_name
}
