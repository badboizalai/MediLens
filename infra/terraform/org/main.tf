terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configured by the owner at init time (state bucket in the management account).
  backend "s3" {}
}

provider "aws" {
  region = var.home_region

  default_tags {
    tags = var.tags
  }
}

# Used only for resources that live in the log-archive account.
provider "aws" {
  alias  = "log_archive"
  region = var.home_region

  assume_role {
    role_arn = "arn:aws:iam::${aws_organizations_account.this["log-archive"].id}:role/OrganizationAccountAccessRole"
  }

  default_tags {
    tags = var.tags
  }
}

data "aws_ssoadmin_instances" "this" {}

locals {
  sso_instance_arn = tolist(data.aws_ssoadmin_instances.this.arns)[0]
  account_ou       = { security = "security", log-archive = "security", nonprod = "nonprod", prod = "prod" }
}

# ---------- Organization, OUs, accounts ----------

resource "aws_organizations_organization" "this" {
  feature_set = "ALL"

  aws_service_access_principals = [
    "cloudtrail.amazonaws.com",
    "config.amazonaws.com",
    "guardduty.amazonaws.com",
    "securityhub.amazonaws.com",
    "sso.amazonaws.com",
  ]

  enabled_policy_types = ["SERVICE_CONTROL_POLICY"]
}

resource "aws_organizations_organizational_unit" "this" {
  for_each  = toset(["security", "nonprod", "prod"])
  name      = each.key
  parent_id = aws_organizations_organization.this.roots[0].id
}

resource "aws_organizations_account" "this" {
  for_each  = var.account_emails
  name      = "medilens-${each.key}"
  email     = each.value
  parent_id = aws_organizations_organizational_unit.this[local.account_ou[each.key]].id
  role_name = "OrganizationAccountAccessRole"

  # Terraform never closes accounts; closing is a manual, audited action.
  close_on_deletion = false

  lifecycle {
    ignore_changes = [role_name, iam_user_access_to_billing]
  }
}

# ---------- Service control policies ----------

resource "aws_organizations_policy" "deny_leave_org" {
  name    = "medilens-deny-leave-org"
  type    = "SERVICE_CONTROL_POLICY"
  content = file("${path.module}/scp/deny-leave-org.json")
}

resource "aws_organizations_policy" "deny_disable_security" {
  name    = "medilens-deny-disable-security-services"
  type    = "SERVICE_CONTROL_POLICY"
  content = file("${path.module}/scp/deny-disable-security-services.json")
}

resource "aws_organizations_policy" "deny_root" {
  name    = "medilens-deny-root"
  type    = "SERVICE_CONTROL_POLICY"
  content = file("${path.module}/scp/deny-root.json")
}

resource "aws_organizations_policy" "region_allowlist" {
  name    = "medilens-region-allowlist"
  type    = "SERVICE_CONTROL_POLICY"
  content = templatefile("${path.module}/scp/region-allowlist.json.tftpl", { regions = jsonencode(var.allowed_regions) })
}

# Attached to the three OUs (member accounts). SCPs do not apply to the
# management account; protect it with Identity Center and MFA instead.
locals {
  scp_ids = {
    deny_leave_org        = aws_organizations_policy.deny_leave_org.id
    deny_disable_security = aws_organizations_policy.deny_disable_security.id
    deny_root             = aws_organizations_policy.deny_root.id
    region_allowlist      = aws_organizations_policy.region_allowlist.id
  }
  scp_attachments = {
    for pair in setproduct(keys(local.scp_ids), ["security", "nonprod", "prod"]) :
    "${pair[0]}-${pair[1]}" => { policy = pair[0], ou = pair[1] }
  }
}

resource "aws_organizations_policy_attachment" "this" {
  for_each  = local.scp_attachments
  policy_id = local.scp_ids[each.value.policy]
  target_id = aws_organizations_organizational_unit.this[each.value.ou].id
}

# ---------- IAM Identity Center permission sets ----------
# Group-to-account assignment is done by the owner once groups exist (see README).

resource "aws_ssoadmin_permission_set" "admin" {
  name             = "MediLensAdmin"
  description      = "Administrator for nonprod accounts; prod only via break-glass approval."
  instance_arn     = local.sso_instance_arn
  session_duration = var.sso_session_duration
}

resource "aws_ssoadmin_managed_policy_attachment" "admin" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.admin.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_ssoadmin_permission_set" "developer_readonly" {
  name             = "MediLensDeveloperReadOnly"
  description      = "Read-only access for developers, intended for prod."
  instance_arn     = local.sso_instance_arn
  session_duration = var.sso_session_duration
}

resource "aws_ssoadmin_managed_policy_attachment" "developer_readonly" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.developer_readonly.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# Block reading object contents and secrets even with ReadOnlyAccess.
resource "aws_ssoadmin_permission_set_inline_policy" "developer_readonly" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.developer_readonly.arn
  inline_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "DenyDataPlaneReads"
      Effect = "Deny"
      Action = [
        "s3:GetObject",
        "secretsmanager:GetSecretValue",
        "kms:Decrypt",
        "ssm:GetParameter*",
        "rds-data:*",
      ]
      Resource = "*"
    }]
  })
}

# ---------- Organization CloudTrail -> log-archive bucket with KMS ----------

data "aws_iam_policy_document" "trail_key" {
  statement {
    sid       = "AccountAdmin"
    actions   = ["kms:*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${aws_organizations_account.this["log-archive"].id}:root"]
    }
  }

  statement {
    sid       = "CloudTrailEncrypt"
    actions   = ["kms:GenerateDataKey*", "kms:DescribeKey"]
    resources = ["*"]
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values   = ["arn:aws:cloudtrail:${var.home_region}:${var.management_account_id}:trail/${var.org_trail_name}"]
    }
  }
}

resource "aws_kms_key" "trail" {
  provider                = aws.log_archive
  description             = "medilens org CloudTrail logs"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.trail_key.json
}

resource "aws_kms_alias" "trail" {
  provider      = aws.log_archive
  name          = "alias/medilens-org-cloudtrail"
  target_key_id = aws_kms_key.trail.key_id
}

resource "aws_s3_bucket" "trail" {
  provider            = aws.log_archive
  bucket              = var.trail_bucket_name
  object_lock_enabled = true
  force_destroy       = false
}

resource "aws_s3_bucket_public_access_block" "trail" {
  provider                = aws.log_archive
  bucket                  = aws_s3_bucket.trail.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "trail" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.trail.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "trail" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.trail.id
  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.trail.arn
    }
  }
}

resource "aws_s3_bucket_object_lock_configuration" "trail" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.trail.id
  rule {
    default_retention {
      mode = "GOVERNANCE" # Move to COMPLIANCE only after retention is signed off.
      days = 365
    }
  }
  depends_on = [aws_s3_bucket_versioning.trail]
}

resource "aws_s3_bucket_lifecycle_configuration" "trail" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.trail.id
  rule {
    id     = "expire"
    status = "Enabled"
    filter {}
    expiration {
      days = var.trail_retention_days
    }
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

data "aws_iam_policy_document" "trail_bucket" {
  statement {
    sid       = "AclCheck"
    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.trail.arn]
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
  }

  statement {
    sid     = "Write"
    actions = ["s3:PutObject"]
    resources = [
      "${aws_s3_bucket.trail.arn}/AWSLogs/${var.management_account_id}/*",
      "${aws_s3_bucket.trail.arn}/AWSLogs/${aws_organizations_organization.this.id}/*",
    ]
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }

  statement {
    sid       = "DenyInsecureTransport"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.trail.arn, "${aws_s3_bucket.trail.arn}/*"]
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
}

resource "aws_s3_bucket_policy" "trail" {
  provider = aws.log_archive
  bucket   = aws_s3_bucket.trail.id
  policy   = data.aws_iam_policy_document.trail_bucket.json

  depends_on = [aws_s3_bucket_public_access_block.trail]
}

resource "aws_cloudtrail" "org" {
  name                          = var.org_trail_name
  s3_bucket_name                = aws_s3_bucket.trail.id
  kms_key_id                    = aws_kms_key.trail.arn
  is_organization_trail         = true
  is_multi_region_trail         = true
  include_global_service_events = true
  enable_log_file_validation    = true

  depends_on = [aws_s3_bucket_policy.trail]
}
