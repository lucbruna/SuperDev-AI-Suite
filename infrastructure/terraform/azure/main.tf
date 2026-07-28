terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "superdev-terraform"
    storage_account_name = "superdevtfstate"
    container_name       = "tfstate"
    key                  = "environments/production/terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

# ── Resource Group ───────────────────────────────────
resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}"
  location = var.azure_location
  tags     = var.tags
}

# ── AKS Cluster ──────────────────────────────────────
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${var.project_name}-${var.environment}"
  kubernetes_version  = var.aks_version

  default_node_pool {
    name                = "default"
    node_count          = var.aks_min_nodes
    vm_size             = var.aks_vm_size
    enable_auto_scaling = true
    min_count           = var.aks_min_nodes
    max_count           = var.aks_max_nodes
    os_disk_size_gb     = 100
    type                = "VirtualMachineScaleSets"
  }

  identity { type = "SystemAssigned" }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  network_profile {
    network_plugin = "azure"
    network_policy = "calico"
    load_balancer_sku = "standard"
  }

  monitoring {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  azure_policy_enabled = true

  tags = var.tags
}

# ── PostgreSQL (Azure DB) ────────────────────────────
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.project_name}-pg-${var.environment}"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "16"
  administrator_login    = var.pg_admin_username
  administrator_password = random_password.pg.result
  zone                   = "1"
  storage_mb             = var.pg_storage_gb * 1024
  sku_name               = var.pg_sku
  backup_retention_days  = 30
  geo_redundant_backup_enabled = var.environment == "production"
  public_network_access_enabled = false
  delegated_subnet_id    = azurerm_subnet.private.id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres.id
  tags = var.tags
}

resource "random_password" "pg" { length = 24; special = false }

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = var.pg_db_name
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# ── Redis Cache ──────────────────────────────────────
resource "azurerm_redis_cache" "main" {
  name                = "${var.project_name}-redis-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  capacity            = var.redis_capacity
  family              = var.environment == "production" ? "P" : "C"
  sku_name            = var.environment == "production" ? "Premium" : "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  redis_version       = "7"
  subnet_id           = var.environment == "production" ? azurerm_subnet.private.id : null
  tags = var.tags
}

# ── Networking ───────────────────────────────────────
resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = var.vnet_cidr
  tags = var.tags
}

resource "azurerm_subnet" "private" {
  name                 = "private"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = var.private_cidr
}

resource "azurerm_private_dns_zone" "postgres" {
  name                = "${var.project_name}.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "${var.project_name}-pg-link"
  private_dns_zone_id   = azurerm_private_dns_zone.postgres.id
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = false
  resource_group_name   = azurerm_resource_group.main.name
}

# ── Log Analytics ────────────────────────────────────
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.project_name}-logs-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags = var.tags
}

# ── Application Insights ─────────────────────────────
resource "azurerm_application_insights" "main" {
  name                = "${var.project_name}-insights-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  sampling_percentage = 100
  tags = var.tags
}

# ── Front Door / WAF ─────────────────────────────────
resource "azurerm_frontdoor" "main" {
  name                = "${var.project_name}-fd-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name

  routing_rule {
    name               = "default"
    accepted_protocols = ["Http", "Https"]
    patterns_to_match  = ["/*"]
    frontend_endpoints = ["default"]
    forwarding_configuration {
      forwarding_protocol = "HttpsOnly"
      backend_pool_name   = "default"
    }
  }

  backend_pool {
    name = "default"
    backend {
      host_header = "${var.project_name}.azurewebsites.net"
      address     = azurerm_kubernetes_cluster.main.fqdn
      http_port   = 80
      https_port  = 443
    }
    health_probe_name = "default"
  }

  backend_pool_health_probe {
    name                = "default"
    protocol            = "Https"
    path                = "/health"
    interval_in_seconds = 30
  }

  frontend_endpoint {
    name      = "default"
    host_name = "${var.project_name}-fd-${var.environment}.azurefd.net"
  }

  tags = var.tags
}

# ── Dashboard ────────────────────────────────────────
resource "azurerm_dashboard" "main" {
  name                = "${var.project_name}-dashboard-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  tags                = var.tags
  dashboard_properties = jsonencode({
    lenses = [{
      order = 0
      parts = [
        { position = { x = 0, y = 0, rowSpan = 2, colSpan = 2 }
          metadata = { inputs = [], type = "Extension/HubsExtension/PartType/MonitorChartPart"
            settings = { content = { options = { metric = { resourceMetadata = { id = azurerm_kubernetes_cluster.main.id } } } } } } }
      ]
    }]
  })
}