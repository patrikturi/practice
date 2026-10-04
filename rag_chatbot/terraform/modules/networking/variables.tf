variable "name_prefix" {
  type        = string
  description = "Prefix for resource names"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC CIDR block"
}

variable "enable_nat_gateway" {
  type        = bool
  default     = true
  description = "Create a NAT gateway for private subnet egress (needed for ECR pulls unless using VPC endpoints for ECR)"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Common tags"
}
