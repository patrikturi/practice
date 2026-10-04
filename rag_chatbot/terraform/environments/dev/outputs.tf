output "http_api_endpoint" {
  value = module.api.http_api_endpoint
}

output "websocket_api_endpoint" {
  value = module.api.websocket_api_endpoint
}

output "website_url" {
  value = module.frontend.website_url
}

output "frontend_bucket_id" {
  value = module.frontend.bucket_id
}

output "cloudfront_distribution_id" {
  value = module.frontend.cloudfront_distribution_id
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "cognito_client_id" {
  value = module.cognito.client_id
}

output "cognito_domain" {
  value = module.cognito.domain
}

output "docs_bucket_id" {
  value = module.storage.docs_bucket_id
}

output "ecr_repository_url" {
  value = module.compute.ecr_repository_url
}

output "aurora_secret_arn" {
  value     = module.data.secret_arn
  sensitive = true
}

output "aurora_endpoint" {
  value = module.data.cluster_endpoint
}
