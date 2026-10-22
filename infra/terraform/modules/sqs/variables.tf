variable "name" { type = string }
variable "kms_key_arn" { type = string }
variable "max_receive_count" {
  type    = number
  default = 5
}
variable "visibility_timeout_seconds" {
  type    = number
  default = 300
}
variable "retention_seconds" {
  type    = number
  default = 345600
}
variable "dlq_retention_seconds" {
  type    = number
  default = 1209600
}
variable "tags" {
  type    = map(string)
  default = {}
}
