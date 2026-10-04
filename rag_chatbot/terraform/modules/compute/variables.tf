variable "name_prefix" { type = string }
variable "backend_path" {
  type        = string
  description = "Absolute or repo-relative path to backend/"
}
variable "private_subnet_ids" { type = list(string) }
variable "lambda_security_group_id" { type = string }
variable "fargate_security_group_id" { type = string }
variable "docs_bucket_id" { type = string }
variable "docs_bucket_arn" { type = string }
variable "kms_key_arn" { type = string }
variable "kms_key_id" { type = string }
variable "documents_table_name" { type = string }
variable "documents_table_arn" { type = string }
variable "chat_sessions_table_name" { type = string }
variable "chat_sessions_table_arn" { type = string }
variable "chat_messages_table_name" { type = string }
variable "chat_messages_table_arn" { type = string }
variable "semantic_cache_table_name" { type = string }
variable "semantic_cache_table_arn" { type = string }
variable "ws_connections_table_name" { type = string }
variable "ws_connections_table_arn" { type = string }
variable "aurora_secret_arn" { type = string }
variable "ingest_dlq_arn" { type = string }
variable "ingest_dlq_url" { type = string }
variable "cognito_issuer" {
  type    = string
  default = ""
}
variable "cognito_client_id" {
  type    = string
  default = ""
}
variable "claude_model_id" {
  type    = string
  default = "global.anthropic.claude-sonnet-5-5"
}
variable "embed_model_id" {
  type    = string
  default = "amazon.titan-embed-text-v2:0"
}
variable "top_k" {
  type    = number
  default = 5
}
variable "cache_ttl_seconds" {
  type    = number
  default = 3600
}
variable "max_upload_bytes" {
  type    = number
  default = 104857600
}
variable "chat_reserved_concurrency" {
  type    = number
  default = 50
}
variable "tags" {
  type    = map(string)
  default = {}
}
