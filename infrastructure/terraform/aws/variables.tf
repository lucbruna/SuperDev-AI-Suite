variable "project_name" {
  description = "Project name"
  type        = string
  default     = "superdev"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "container_repository" {
  description = "ECR repository URL"
  type        = string
  default     = "public.ecr.aws/superdev/app"
}

variable "container_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8000
}

variable "service_cpu" {
  description = "ECS task CPU"
  type        = number
  default     = 1024
}

variable "service_memory" {
  description = "ECS task memory"
  type        = number
  default     = 2048
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
}

variable "rds_storage_gb" {
  description = "RDS allocated storage (GB)"
  type        = number
  default     = 100
}

variable "rds_max_storage_gb" {
  description = "RDS max storage (GB)"
  type        = number
  default     = 500
}

variable "rds_db_name" {
  description = "RDS database name"
  type        = string
  default     = "superdev"
}

variable "rds_username" {
  description = "RDS username"
  type        = string
  default     = "superdev_admin"
}

variable "rds_backup_retention_days" {
  description = "RDS backup retention"
  type        = number
  default     = 30
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_num_nodes" {
  description = "Number of Redis nodes"
  type        = number
  default     = 2
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    Project   = "superdev"
    ManagedBy = "terraform"
  }
}