output "cluster_name" { value = google_container_cluster.primary.name }
output "cluster_endpoint" { value = google_container_cluster.primary.endpoint }
output "sql_instance" { value = google_sql_database_instance.postgres.name }
output "sql_endpoint" { value = google_sql_database_instance.postgres.private_ip_address; sensitive = true }
output "redis_endpoint" { value = google_redis_instance.cache.host; sensitive = true }
output "redis_port" { value = google_redis_instance.cache.port }
output "database_password_secret" { value = random_password.cloudsql.result; sensitive = true }