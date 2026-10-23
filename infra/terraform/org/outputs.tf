output "organization_id" {
  value = aws_organizations_organization.this.id
}

output "account_ids" {
  description = "Member account ids keyed by name."
  value       = { for k, a in aws_organizations_account.this : k => a.id }
}

output "ou_ids" {
  value = { for k, o in aws_organizations_organizational_unit.this : k => o.id }
}

output "permission_set_arns" {
  value = {
    admin              = aws_ssoadmin_permission_set.admin.arn
    developer_readonly = aws_ssoadmin_permission_set.developer_readonly.arn
  }
}

output "trail_bucket" {
  value = aws_s3_bucket.trail.id
}

output "trail_kms_key_arn" {
  value = aws_kms_key.trail.arn
}
