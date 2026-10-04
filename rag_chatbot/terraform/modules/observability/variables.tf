variable "name_prefix" { type = string }
variable "logs_bucket_id" { type = string }
variable "logs_bucket_arn" { type = string }
variable "chat_function_name" { type = string }
variable "aurora_cluster_id" { type = string }
variable "tags" {
  type    = map(string)
  default = {}
}
