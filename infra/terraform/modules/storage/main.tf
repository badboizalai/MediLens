terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.80" }
  }
}

data "aws_caller_identity" "current" {}

locals {
  buckets = toset(["quarantine", "phi", "assets"])
  # The GuardDuty plan role also needs the quarantine key.
  key_users = {
    quarantine = concat(var.quarantine_role_arns, var.enable_malware_protection ? [aws_iam_role.guardduty[0].arn] : [])
    phi        = var.phi_role_arns
    assets     = var.assets_role_arns
  }
}

# ---------- KMS: one CMK per data class ----------
data "aws_iam_policy_document" "key" {
  for_each = local.buckets

  statement {
    sid       = "Administer"
    actions   = ["kms:Create*", "kms:Describe*", "kms:Enable*", "kms:List*", "kms:Put*", "kms:Update*", "kms:Revoke*", "kms:Disable*", "kms:Get*", "kms:ScheduleKeyDeletion", "kms:CancelKeyDeletion", "kms:TagResource", "kms:UntagResource"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = var.kms_admin_role_arns
    }
  }

  dynamic "statement" {
    for_each = length(local.key_users[each.key]) > 0 ? [1] : []
    content {
      sid       = "UseForDataClass"
      actions   = ["kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:DescribeKey"]
      resources = ["*"]
      principals {
        type        = "AWS"
        identifiers = local.key_users[each.key]
      }
    }
  }
}

resource "aws_kms_key" "this" {
  for_each                = local.buckets
  description             = "${var.name} ${each.key} data class"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.key[each.key].json
  tags                    = merge(var.tags, { data_class = each.key })
}

resource "aws_kms_alias" "this" {
  for_each      = local.buckets
  name          = "alias/${var.name}-${each.key}"
  target_key_id = aws_kms_key.this[each.key].key_id
}

# ---------- Log bucket (SSE-S3: S3 log delivery does not support KMS) ----------
resource "aws_s3_bucket" "logs" {
  bucket = "${var.name}-s3-logs-${data.aws_caller_identity.current.account_id}"
  tags   = merge(var.tags, { data_class = "logs" })
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    id     = "expire-logs"
    status = "Enabled"
    filter {}
    expiration { days = var.log_retention_days }
    noncurrent_version_expiration { noncurrent_days = 30 }
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
  depends_on = [aws_s3_bucket_versioning.logs]
}

data "aws_iam_policy_document" "logs" {
  statement {
    sid       = "DenyInsecureTransport"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.logs.arn, "${aws_s3_bucket.logs.arn}/*"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
  statement {
    sid       = "S3LogDelivery"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.logs.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["logging.s3.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_s3_bucket_policy" "logs" {
  bucket     = aws_s3_bucket.logs.id
  policy     = data.aws_iam_policy_document.logs.json
  depends_on = [aws_s3_bucket_public_access_block.logs]
}

# ---------- Data buckets ----------
resource "aws_s3_bucket" "this" {
  for_each = local.buckets
  bucket   = "${var.name}-${each.key}-${data.aws_caller_identity.current.account_id}"
  tags     = merge(var.tags, { data_class = each.key })
}

resource "aws_s3_bucket_public_access_block" "this" {
  for_each                = local.buckets
  bucket                  = aws_s3_bucket.this[each.key].id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "this" {
  for_each = local.buckets
  bucket   = aws_s3_bucket.this[each.key].id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_versioning" "this" {
  for_each = local.buckets
  bucket   = aws_s3_bucket.this[each.key].id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  for_each = local.buckets
  bucket   = aws_s3_bucket.this[each.key].id
  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.this[each.key].arn
    }
  }
}

resource "aws_s3_bucket_logging" "this" {
  for_each      = local.buckets
  bucket        = aws_s3_bucket.this[each.key].id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "${each.key}/"
}

data "aws_iam_policy_document" "bucket" {
  for_each = local.buckets

  statement {
    sid       = "DenyInsecureTransport"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.this[each.key].arn, "${aws_s3_bucket.this[each.key].arn}/*"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }

  statement {
    sid       = "DenyWrongKmsKey"
    effect    = "Deny"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.this[each.key].arn}/*"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "StringNotEqualsIfExists"
      variable = "s3:x-amz-server-side-encryption-aws-kms-key-id"
      values   = [aws_kms_key.this[each.key].arn]
    }
  }
}

resource "aws_s3_bucket_policy" "this" {
  for_each   = local.buckets
  bucket     = aws_s3_bucket.this[each.key].id
  policy     = data.aws_iam_policy_document.bucket[each.key].json
  depends_on = [aws_s3_bucket_public_access_block.this]
}

resource "aws_s3_bucket_lifecycle_configuration" "quarantine" {
  bucket = aws_s3_bucket.this["quarantine"].id
  rule {
    id     = "expire-quarantine"
    status = "Enabled"
    filter {}
    expiration { days = var.quarantine_expiration_days }
    noncurrent_version_expiration { noncurrent_days = 1 }
    abort_incomplete_multipart_upload { days_after_initiation = 1 }
  }
  depends_on = [aws_s3_bucket_versioning.this]
}

# phi / assets: keep current objects, bound noncurrent history.
resource "aws_s3_bucket_lifecycle_configuration" "retained" {
  for_each = toset(["phi", "assets"])
  bucket   = aws_s3_bucket.this[each.key].id
  rule {
    id     = "noncurrent-and-multipart"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration { noncurrent_days = 90 }
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
  depends_on = [aws_s3_bucket_versioning.this]
}

# ---------- GuardDuty Malware Protection for S3 (quarantine) ----------
resource "aws_iam_role" "guardduty" {
  count = var.enable_malware_protection ? 1 : 0
  name  = "${var.name}-guardduty-malware-s3"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "malware-protection-plan.guardduty.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = { StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id } }
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "guardduty" {
  count = var.enable_malware_protection ? 1 : 0
  name  = "scan-quarantine"
  role  = aws_iam_role.guardduty[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion", "s3:GetObjectTagging", "s3:PutObjectTagging", "s3:PutObjectVersionTagging"]
        Resource = "${aws_s3_bucket.this["quarantine"].arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetBucketNotification", "s3:PutBucketNotification", "s3:GetBucketLocation", "s3:ListBucket"]
        Resource = aws_s3_bucket.this["quarantine"].arn
      },
      {
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
        Resource = aws_kms_key.this["quarantine"].arn
      },
      {
        Effect   = "Allow"
        Action   = ["events:PutRule", "events:DeleteRule", "events:PutTargets", "events:RemoveTargets", "events:DescribeRule", "events:ListTargetsByRule"]
        Resource = "arn:aws:events:*:${data.aws_caller_identity.current.account_id}:rule/DO-NOT-DELETE-AmazonGuardDutyMalwareProtectionS3*"
      },
    ]
  })
}

# VERIFY: resource needs AWS provider >= ~5.76; confirm in lock file and region support.
resource "aws_guardduty_malware_protection_plan" "quarantine" {
  count = var.enable_malware_protection ? 1 : 0
  role  = aws_iam_role.guardduty[0].arn

  protected_resource {
    s3_bucket {
      bucket_name = aws_s3_bucket.this["quarantine"].id
    }
  }

  actions {
    tagging { status = "ENABLED" }
  }

  tags       = var.tags
  depends_on = [aws_iam_role_policy.guardduty]
}

# ---------- Scan result -> SQS ----------
resource "aws_cloudwatch_event_rule" "scan_result" {
  name        = "${var.name}-malware-scan-result"
  description = "GuardDuty S3 malware scan result for the quarantine bucket"
  event_pattern = jsonencode({
    source        = ["aws.guardduty"]
    "detail-type" = ["GuardDuty Malware Protection Object Scan Result"]
    detail = {
      s3ObjectDetails = { bucketName = [aws_s3_bucket.this["quarantine"].id] }
    }
  })
  tags = var.tags
}

resource "aws_cloudwatch_event_target" "scan_result" {
  rule = aws_cloudwatch_event_rule.scan_result.name
  arn  = var.scan_result_queue_arn
}
