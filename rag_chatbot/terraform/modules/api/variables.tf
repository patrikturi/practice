variable "name_prefix" { type = string }
variable "stage_name" {
  type    = string
  default = "prod"
}
variable "cognito_client_id" { type = string }
variable "cognito_issuer" { type = string }
variable "lambda_invoke_arns" { type = map(string) }
variable "lambda_function_names" { type = map(string) }
variable "cors_allow_origins" {
  type    = list(string)
  default = ["*"]
}
variable "waf_rate_limit" {
  type        = number
  default     = 2000
  description = "Requests per 5-minute window per IP"
}
variable "tags" {
  type    = map(string)
  default = {}
}
