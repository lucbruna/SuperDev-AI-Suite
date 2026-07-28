output "aks_cluster_name" { value = azurerm_kubernetes_cluster.main.name }
output "aks_fqdn" { value = azurerm_kubernetes_cluster.main.fqdn }
output "postgres_server" { value = azurerm_postgresql_flexible_server.main.name }
output "postgres_fqdn" { value = azurerm_postgresql_flexible_server.main.fqdn; sensitive = true }
output "redis_hostname" { value = azurerm_redis_cache.main.hostname; sensitive = true }
output "redis_ssl_port" { value = azurerm_redis_cache.main.ssl_port }
output "application_insights_key" { value = azurerm_application_insights.main.instrumentation_key; sensitive = true }
output "frontdoor_host" { value = azurerm_frontdoor.main.frontend_endpoints[0].host_name }
output "database_password_secret" { value = random_password.pg.result; sensitive = true }