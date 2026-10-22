variable "name" { type = string }
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "kms_key_arn" {
  type        = string
  description = "Customer-managed KMS key for storage, master secret and Performance Insights."
}
variable "instance_class" {
  type    = string
  default = "db.t4g.medium"
}
variable "allocated_storage" {
  type    = number
  default = 50
}
variable "max_allocated_storage" {
  type    = number
  default = 200
}
variable "multi_az" {
  type    = bool
  default = false
}
variable "db_name" {
  type    = string
  default = "medilens"
}
variable "master_username" {
  type    = string
  default = "medilens_admin"
}
variable "backup_retention_days" {
  type    = number
  default = 14
}
variable "deletion_protection" {
  type    = bool
  default = true
}
variable "tags" {
  type    = map(string)
  default = {}
}
