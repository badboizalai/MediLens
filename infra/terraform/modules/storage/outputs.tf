output "bucket_names" {
  description = "Bucket names by data class."
  value       = { for k, b in aws_s3_bucket.this : k => b.id }
}

output "bucket_arns" {
  description = "Bucket ARNs by data class."
  value       = { for k, b in aws_s3_bucket.this : k => b.arn }
}

output "kms_key_arns" {
  description = "CMK ARNs by data class."
  value       = { for k, v in aws_kms_key.this : k => v.arn }
}

output "log_bucket_name" {
  description = "Access-log bucket name."
  value       = aws_s3_bucket.logs.id
}

output "scan_result_rule_arn" {
  description = "Use in the SQS queue policy (events.amazonaws.com, aws:SourceArn)."
  value       = aws_cloudwatch_event_rule.scan_result.arn
}
