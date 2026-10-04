variable "name_prefix" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "aurora_security_group_id" {
  type = string
}

variable "kms_key_arn" {
  type = string
}

variable "database_name" {
  type    = string
  default = "ragchat"
}

variable "master_username" {
  type    = string
  default = "ragadmin"
}

variable "engine_version" {
  type    = string
  default = "15.8"
}

variable "min_capacity" {
  type    = number
  default = 0
}

variable "max_capacity" {
  type    = number
  default = 4
}

variable "deletion_protection" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
