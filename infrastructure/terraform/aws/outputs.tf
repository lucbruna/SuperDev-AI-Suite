output "vpc_id" {
  value = module.vpc.vpc_id
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = module.ecs_service.name
}

output "rds_endpoint" {
  value = module.rds.endpoint
  sensitive = true
}

output "redis_endpoint" {
  value = module.elasticache.endpoint
  sensitive = true
}

output "alb_dns_name" {
  value = module.alb.dns_name
}

output "alb_zone_id" {
  value = module.alb.zone_id
}

output "database_password_secret" {
  value = random_password.rds.result
  sensitive = true
}