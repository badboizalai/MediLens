output "endpoint" { value = aws_db_instance.this.endpoint }
output "resource_id" {
  value       = aws_db_instance.this.resource_id
  description = "Used for rds-db:connect IAM policy ARNs."
}
output "master_secret_arn" { value = aws_db_instance.this.master_user_secret[0].secret_arn }
