variable "name_prefix" { type = string }
variable "aliases" {
  type    = list(string)
  default = []
}
variable "acm_certificate_arn" {
  type    = string
  default = null
}
variable "tags" {
  type    = map(string)
  default = {}
}
