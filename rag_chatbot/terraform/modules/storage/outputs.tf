output "docs_bucket_id" {
  value = aws_s3_bucket.docs.id
}

output "docs_bucket_arn" {
  value = aws_s3_bucket.docs.arn
}

output "logs_bucket_id" {
  value = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  value = aws_s3_bucket.logs.arn
}

output "kms_key_arn" {
  value = aws_kms_key.docs.arn
}

output "kms_key_id" {
  value = aws_kms_key.docs.key_id
}

output "documents_table_name" {
  value = aws_dynamodb_table.documents.name
}

output "documents_table_arn" {
  value = aws_dynamodb_table.documents.arn
}

output "chat_sessions_table_name" {
  value = aws_dynamodb_table.chat_sessions.name
}

output "chat_sessions_table_arn" {
  value = aws_dynamodb_table.chat_sessions.arn
}

output "chat_messages_table_name" {
  value = aws_dynamodb_table.chat_messages.name
}

output "chat_messages_table_arn" {
  value = aws_dynamodb_table.chat_messages.arn
}

output "semantic_cache_table_name" {
  value = aws_dynamodb_table.semantic_cache.name
}

output "semantic_cache_table_arn" {
  value = aws_dynamodb_table.semantic_cache.arn
}

output "ws_connections_table_name" {
  value = aws_dynamodb_table.ws_connections.name
}

output "ws_connections_table_arn" {
  value = aws_dynamodb_table.ws_connections.arn
}

output "ingest_dlq_arn" {
  value = aws_sqs_queue.ingest_dlq.arn
}

output "ingest_dlq_url" {
  value = aws_sqs_queue.ingest_dlq.url
}
