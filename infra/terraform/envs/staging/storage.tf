# Scan verdicts reach the worker as object tags; this queue only receives the EventBridge copy.
# TODO(S6-T58): queue policy for events.amazonaws.com (modules/sqs owns the policy) before relying on it.
module "scan_results_queue" {
  source = "../../modules/sqs"

  name        = "${local.name}-scan-results"
  kms_key_arn = aws_kms_key.data.arn
  tags        = local.tags
}

module "storage" {
  source = "../../modules/storage"

  name                = local.name
  kms_admin_role_arns = var.kms_admin_role_arns
  # Task roles are created by modules/ecs-service; CMK use is granted to them only.
  quarantine_role_arns = [module.api.task_role_arn, module.worker.task_role_arn]
  phi_role_arns        = [module.api.task_role_arn, module.worker.task_role_arn]

  quarantine_expiration_days = 1 # U-08: rejected files gone in 24 h
  scan_result_queue_arn      = module.scan_results_queue.queue_arn
  tags                       = local.tags
}

locals {
  quarantine_arn = module.storage.bucket_arns["quarantine"]
  phi_arn        = module.storage.bucket_arns["phi"]
}
