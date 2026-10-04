variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "ragchat"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  type    = bool
  default = true
}

variable "aurora_min_capacity" {
  type    = number
  default = 0
}

variable "aurora_max_capacity" {
  type    = number
  default = 4
}

variable "deletion_protection" {
  type    = bool
  default = false
}

variable "cognito_domain_prefix" {
  type        = string
  description = "Globally unique Cognito domain prefix"
}

variable "cognito_callback_urls" {
  type    = list(string)
  default = ["http://localhost:5173/callback"]
}

variable "cognito_logout_urls" {
  type    = list(string)
  default = ["http://localhost:5173/"]
}

variable "cors_allow_origins" {
  type    = list(string)
  default = ["http://localhost:5173"]
}

variable "waf_rate_limit" {
  type    = number
  default = 2000
}

variable "claude_model_id" {
  type    = string
  default = "global.anthropic.claude-sonnet-5-5"
}

variable "embed_model_id" {
  type    = string
  default = "amazon.titan-embed-text-v2:0"
}
