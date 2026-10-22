# PLACEHOLDERS: replace role/queue ARNs once iam/messaging modules exist.
module "storage" {
  source = "../../modules/storage"

  name = "medilens-dev"

  kms_admin_role_arns  = ["arn:aws:iam::111111111111:role/PLACEHOLDER-platform-admin"]
  quarantine_role_arns = ["arn:aws:iam::111111111111:role/PLACEHOLDER-api-task"]
  phi_role_arns        = ["arn:aws:iam::111111111111:role/PLACEHOLDER-api-task", "arn:aws:iam::111111111111:role/PLACEHOLDER-worker-task"]
  assets_role_arns     = ["arn:aws:iam::111111111111:role/PLACEHOLDER-api-task"]

  quarantine_expiration_days = 7
  scan_result_queue_arn      = "arn:aws:sqs:ap-southeast-1:111111111111:PLACEHOLDER-scan-results"

  tags = {
    project       = "medilens"
    env           = "dev"
    owner         = "platform"
    "cost-center" = "medilens-nonprod"
    managed_by    = "terraform"
  }
}
