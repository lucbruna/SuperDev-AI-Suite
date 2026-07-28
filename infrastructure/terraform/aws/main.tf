terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "superdev-terraform-state"
    key    = "environments/production/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}

# ── VPC ──────────────────────────────────────────────
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway = true
  enable_vpn_gateway = false
  single_nat_gateway = var.environment == "staging"

  tags = var.tags
}

# ── ECS Cluster ───────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}"
  setting { name = "containerInsights"; value = "enabled" }
  tags = var.tags
}

module "ecs_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 5.0"

  name        = "${var.project_name}-service"
  cluster_arn = aws_ecs_cluster.main.arn

  cpu    = var.service_cpu
  memory = var.service_memory

  container_definitions = {
    app = {
      image = "${var.container_repository}:${var.container_tag}"
      port_mappings = [{ containerPort = var.container_port, protocol = "tcp" }]
      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "DATABASE_URL", value = module.rds.endpoint },
        { name = "REDIS_URL", value = module.elasticache.endpoint },
      ]
      log_configuration = {
        log_driver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  }

  subnet_ids = module.vpc.private_subnets
  security_group_ids = [aws_security_group.ecs.id]
  assign_public_ip   = false

  tags = var.tags
}

# ── RDS (PostgreSQL) ──────────────────────────────────
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${var.project_name}-${var.environment}"

  engine               = "postgres"
  engine_version       = "16"
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = var.rds_instance_class

  allocated_storage     = var.rds_storage_gb
  max_allocated_storage = var.rds_max_storage_gb
  storage_encrypted     = true

  db_name  = var.rds_db_name
  username = var.rds_username
  password = random_password.rds.result
  port     = 5432

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = module.vpc.database_subnet_group

  backup_window      = "03:00-04:00"
  maintenance_window = "sun:04:00-sun:05:00"
  backup_retention_period = var.rds_backup_retention_days
  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment != "production"

  tags = var.tags
}

resource "random_password" "rds" {
  length  = 24
  special = false
}

# ── ElastiCache (Redis) ───────────────────────────────
module "elasticache" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "~> 1.0"

  cluster_id = "${var.project_name}-${var.environment}"

  engine         = "redis"
  engine_version = "7.1"
  node_type      = var.redis_node_type
  num_cache_nodes = var.redis_num_nodes

  subnet_ids = module.vpc.private_subnets
  security_group_ids = [aws_security_group.redis.id]

  parameter_group_family = "redis7"

  tags = var.tags
}

# ── ALB ───────────────────────────────────────────────
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

  name = "${var.project_name}-${var.environment}"

  load_balancer_type = "application"
  vpc_id             = module.vpc.vpc_id
  subnets            = module.vpc.public_subnets
  security_groups    = [aws_security_group.alb.id]

  target_groups = [
    {
      name             = "${var.project_name}-tg"
      backend_protocol = "HTTP"
      backend_port     = var.container_port
      target_type      = "ip"
      health_check = {
        path = "/health"
      }
    }
  ]

  http_tcp_listeners = [
    { port = 80, protocol = "HTTP", redirect = { port = "443", protocol = "HTTPS", status_code = "HTTP_301" } },
  ]

  https_listeners = [
    { port = 443, protocol = "HTTPS", certificate_arn = var.certificate_arn },
  ]

  tags = var.tags
}

# ── CloudWatch ───────────────────────────────────────
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-${var.environment}"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", { stat = "Average" }],
            ["AWS/ECS", "MemoryUtilization", { stat = "Average" }],
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "ECS Resource Usage"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/RDS", "DatabaseConnections", { stat = "Average" }],
            ["AWS/RDS", "ReadLatency", { stat = "Average" }],
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "RDS Performance"
        }
      }
    ]
  })
}

# ── Security Groups ───────────────────────────────────
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb"
  description = "ALB security group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

resource "aws_security_group" "ecs" {
  name        = "${var.project_name}-ecs"
  description = "ECS tasks security group"
  vpc_id      = module.vpc.vpc_id
  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds"
  description = "RDS security group"
  vpc_id      = module.vpc.vpc_id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
  tags = var.tags
}

resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis"
  description = "Redis security group"
  vpc_id      = module.vpc.vpc_id
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
  tags = var.tags
}

# ── IAM ───────────────────────────────────────────────
resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-ecs-execution-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
  ]
  tags = var.tags
}

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}