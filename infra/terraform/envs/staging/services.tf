locals {
  tags = {
    project       = "medilens"
    env           = "staging"
    owner         = "platform"
    "cost-center" = "medilens-nonprod"
    managed_by    = "terraform"
  }
  name = "medilens-staging"
}

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "data" {
  description             = "${local.name} data (RDS, SQS, logs)"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AccountAdmin"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid       = "CloudWatchLogs"
        Effect    = "Allow"
        Principal = { Service = "logs.ap-southeast-1.amazonaws.com" }
        Action    = ["kms:Encrypt*", "kms:Decrypt*", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:Describe*"]
        Resource  = "*"
      }
    ]
  })
  tags = local.tags
}

resource "aws_ecr_repository" "svc" {
  for_each             = toset(["api", "worker"])
  name                 = "${local.name}/${each.key}"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.data.arn
  }
  tags = local.tags
}

resource "aws_ecs_cluster" "this" {
  name = local.name
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = local.tags
}

# ---------- Security groups (rules the network module leaves to the env) ----------
resource "aws_security_group" "alb" {
  name_prefix = "${local.name}-alb-"
  description = "Public ALB: 443/80 in, app out"
  vpc_id      = module.network.vpc_id
  tags        = merge(local.tags, { Name = "${local.name}-alb" })
  lifecycle { create_before_destroy = true }
}

resource "aws_security_group" "db" {
  name_prefix = "${local.name}-db-"
  description = "RDS: 5432 from app and worker only"
  vpc_id      = module.network.vpc_id
  tags        = merge(local.tags, { Name = "${local.name}-db" })
  lifecycle { create_before_destroy = true }
}

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb.id
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  security_group_id = aws_security_group.alb.id
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0" # redirect-only listener
}

resource "aws_vpc_security_group_egress_rule" "alb_to_app" {
  security_group_id            = aws_security_group.alb.id
  ip_protocol                  = "tcp"
  from_port                    = 8000
  to_port                      = 8000
  referenced_security_group_id = module.network.app_security_group_id
}

resource "aws_vpc_security_group_ingress_rule" "app_from_alb" {
  security_group_id            = module.network.app_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 8000
  to_port                      = 8000
  referenced_security_group_id = aws_security_group.alb.id
}

resource "aws_vpc_security_group_ingress_rule" "db_from_client" {
  for_each                     = { app = module.network.app_security_group_id, worker = module.network.worker_security_group_id }
  security_group_id            = aws_security_group.db.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = each.value
}

resource "aws_vpc_security_group_egress_rule" "client_to_db" {
  for_each                     = { app = module.network.app_security_group_id, worker = module.network.worker_security_group_id }
  security_group_id            = each.value
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = aws_security_group.db.id
}

resource "aws_vpc_security_group_egress_rule" "client_https" {
  for_each          = { app = module.network.app_security_group_id, worker = module.network.worker_security_group_id }
  security_group_id = each.value
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "10.20.0.0/16" # VPC endpoints only (no internet from tasks)
}

# ---------- Data plane ----------
module "rds" {
  source = "../../modules/rds-postgres"

  name               = local.name
  subnet_ids         = module.network.worker_subnet_ids
  security_group_ids = [aws_security_group.db.id]
  kms_key_arn        = aws_kms_key.data.arn
  multi_az           = var.rds_multi_az
  tags               = local.tags
}

module "jobs_queue" {
  source = "../../modules/sqs"

  name        = "${local.name}-jobs"
  kms_key_arn = aws_kms_key.data.arn
  tags        = local.tags
}

# ADR-0005: worker -> API status/result events (ids only, no PHI in messages).
module "api_events_queue" {
  source = "../../modules/sqs"

  name        = "${local.name}-api-events"
  kms_key_arn = aws_kms_key.data.arn
  tags        = local.tags
}

module "alb" {
  source = "../../modules/alb"

  name               = local.name
  vpc_id             = module.network.vpc_id
  subnet_ids         = module.network.public_subnet_ids
  security_group_ids = [aws_security_group.alb.id]
  certificate_arn    = var.certificate_arn
  waf_web_acl_arn    = var.waf_web_acl_arn
  tags               = local.tags
}

# ---------- Services ----------
data "aws_iam_policy_document" "api_task" {
  statement {
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:ChangeMessageVisibility", "sqs:GetQueueAttributes"]
    resources = [module.api_events_queue.queue_arn]
  }
  dynamic "statement" {
    for_each = var.phi_bucket_arn == null ? [] : [1]
    content {
      actions   = ["s3:GetObject"]
      resources = ["${var.phi_bucket_arn}/extractions/*"]
    }
  }
  dynamic "statement" {
    for_each = var.phi_kms_key_arn == null ? [] : [1]
    content {
      actions   = ["kms:GenerateDataKey", "kms:Decrypt"]
      resources = [var.phi_kms_key_arn]
    }
  }
  statement {
    actions   = ["sqs:SendMessage", "sqs:GetQueueAttributes"]
    resources = [module.jobs_queue.queue_arn]
  }
  statement {
    actions   = ["rds-db:connect"]
    resources = ["arn:aws:rds-db:ap-southeast-1:${data.aws_caller_identity.current.account_id}:dbuser:${module.rds.resource_id}/medilens_app"]
  }
  statement {
    actions   = ["kms:GenerateDataKey", "kms:Decrypt"]
    resources = [aws_kms_key.data.arn]
  }
}

data "aws_iam_policy_document" "worker_task" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [module.api_events_queue.queue_arn]
  }
  dynamic "statement" {
    for_each = var.phi_bucket_arn == null ? [] : [1]
    content {
      actions   = ["s3:PutObject"]
      resources = ["${var.phi_bucket_arn}/extractions/*"]
    }
  }
  dynamic "statement" {
    for_each = var.phi_kms_key_arn == null ? [] : [1]
    content {
      actions   = ["kms:GenerateDataKey", "kms:Decrypt"]
      resources = [var.phi_kms_key_arn]
    }
  }
  statement {
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:ChangeMessageVisibility", "sqs:GetQueueAttributes"]
    resources = [module.jobs_queue.queue_arn]
  }
  statement {
    actions   = ["rds-db:connect"]
    resources = ["arn:aws:rds-db:ap-southeast-1:${data.aws_caller_identity.current.account_id}:dbuser:${module.rds.resource_id}/medilens_worker"]
  }
  statement {
    actions   = ["kms:GenerateDataKey", "kms:Decrypt"]
    resources = [aws_kms_key.data.arn]
  }
}

module "api" {
  source = "../../modules/ecs-service"

  name               = "${local.name}-api"
  cluster_arn        = aws_ecs_cluster.this.arn
  image              = var.api_image
  container_port     = 8000
  subnet_ids         = module.network.app_subnet_ids
  security_group_ids = [module.network.app_security_group_id]
  target_group_arn   = module.alb.target_group_arn
  task_policy_json   = data.aws_iam_policy_document.api_task.json
  log_kms_key_arn    = aws_kms_key.data.arn
  desired_count      = 2
  min_capacity       = 2
  environment = {
    APP_ENV              = "staging"
    DB_HOST              = split(":", module.rds.endpoint)[0]
    WORKER_QUEUE_URL     = module.jobs_queue.queue_url
    API_EVENTS_QUEUE_URL = module.api_events_queue.queue_url
  }
  tags = local.tags
}

module "worker" {
  source = "../../modules/ecs-service"

  name               = "${local.name}-worker"
  cluster_arn        = aws_ecs_cluster.this.arn
  image              = var.worker_image
  subnet_ids         = module.network.worker_subnet_ids
  security_group_ids = [module.network.worker_security_group_id]
  task_policy_json   = data.aws_iam_policy_document.worker_task.json
  log_kms_key_arn    = aws_kms_key.data.arn
  environment = {
    APP_ENV              = "staging"
    DB_HOST              = split(":", module.rds.endpoint)[0]
    WORKER_QUEUE_URL     = module.jobs_queue.queue_url
    API_EVENTS_QUEUE_URL = module.api_events_queue.queue_url
  }
  tags = local.tags
}
