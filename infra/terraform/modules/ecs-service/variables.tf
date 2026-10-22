variable "name" { type = string }
variable "cluster_arn" { type = string }
variable "image" { type = string }
variable "cpu" {
  type    = number
  default = 512
}
variable "memory" {
  type    = number
  default = 1024
}
variable "container_port" {
  type        = number
  default     = null
  description = "Null for services without inbound traffic (workers)."
}
variable "command" {
  type    = list(string)
  default = null
}
variable "environment" {
  type    = map(string)
  default = {}
}
variable "secrets" {
  type        = map(string)
  default     = {}
  description = "Env var name -> Secrets Manager / SSM ARN. Never plain values."
}
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "target_group_arn" {
  type    = string
  default = null
}
variable "task_policy_json" {
  type        = string
  default     = null
  description = "Least-privilege IAM policy JSON for the task role."
}
variable "desired_count" {
  type    = number
  default = 1
}
variable "min_capacity" {
  type    = number
  default = 1
}
variable "max_capacity" {
  type    = number
  default = 4
}
variable "cpu_target_percent" {
  type    = number
  default = 60
}
variable "log_retention_days" {
  type    = number
  default = 30
}
variable "log_kms_key_arn" {
  type    = string
  default = null
}
variable "tags" {
  type    = map(string)
  default = {}
}
