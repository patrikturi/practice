variable "name_prefix" {
  type = string
}

variable "domain_prefix" {
  type        = string
  description = "Unique Cognito hosted UI domain prefix"
}

variable "callback_urls" {
  type = list(string)
}

variable "logout_urls" {
  type = list(string)
}

variable "tags" {
  type    = map(string)
  default = {}
}
