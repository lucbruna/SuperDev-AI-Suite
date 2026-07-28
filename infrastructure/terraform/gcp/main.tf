terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "superdev-terraform-state"
    prefix = "environments/production"
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# ── VPC ──────────────────────────────────────────────
resource "google_compute_network" "vpc" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "private" {
  name          = "${var.project_name}-private"
  network       = google_compute_network.vpc.id
  region        = var.gcp_region
  ip_cidr_range = var.private_cidr
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "public" {
  name          = "${var.project_name}-public"
  network       = google_compute_network.vpc.id
  region        = var.gcp_region
  ip_cidr_range = var.public_cidr
}

resource "google_compute_router" "nat_router" {
  name    = "${var.project_name}-nat"
  network = google_compute_network.vpc.id
  region  = var.gcp_region
}

resource "google_compute_router_nat" "nat" {
  name                               = "${var.project_name}-nat-gw"
  router                             = google_compute_router.nat_router.name
  region                             = var.gcp_region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
    name                    = google_compute_subnetwork.private.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}

# ── GKE Cluster ──────────────────────────────────────
resource "google_container_cluster" "primary" {
  name     = "${var.project_name}-${var.environment}"
  location = var.gcp_region

  network    = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.private.id

  initial_node_count       = var.gke_min_nodes
  remove_default_node_pool = true

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
    managed_prometheus { enabled = true }
  }

  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  maintenance_policy {
    daily_maintenance_window { start_time = "03:00" }
  }

  ip_allocation_policy { cluster_secondary_range_name = "pods"; services_secondary_range_name = "services" }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  master_authorized_networks_config {
    cidr_blocks { cidr_block = "${data.http.myip.body}/32"; display_name = "admin" }
  }
}

data "http" "myip" {
  url = "https://api.ipify.org"
}

resource "google_container_node_pool" "primary_nodes" {
  name     = "${var.project_name}-nodes"
  cluster  = google_container_cluster.primary.id
  location = var.gcp_region

  initial_node_count = var.gke_min_nodes
  autoscaling {
    min_node_count = var.gke_min_nodes
    max_node_count = var.gke_max_nodes
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    machine_type = var.gke_machine_type
    disk_size_gb = 100
    disk_type    = "pd-ssd"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
    shielded_instance_config {
      enable_secure_boot = true
      enable_integrity_monitoring = true
    }
    labels = var.tags
  }
}

# ── Cloud SQL (PostgreSQL) ───────────────────────────
resource "google_sql_database_instance" "postgres" {
  name             = "${var.project_name}-${var.environment}"
  database_version = "POSTGRES_16"
  region           = var.gcp_region

  settings {
    tier              = var.cloudsql_tier
    disk_size         = var.cloudsql_disk_gb
    disk_autoresize   = true
    disk_type         = "PD_SSD"
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }

    insights_config { query_insights_enabled = true; record_application_tags = true; record_client_address = true }
  }

  deletion_protection = var.environment == "production"
}

resource "google_sql_database" "main" {
  name     = var.cloudsql_db_name
  instance = google_sql_database_instance.postgres.name
}

resource "random_password" "cloudsql" {
  length  = 24
  special = false
}

resource "google_sql_user" "admin" {
  name     = var.cloudsql_username
  instance = google_sql_database_instance.postgres.name
  password = random_password.cloudsql.result
}

# ── Memorystore (Redis) ──────────────────────────────
resource "google_redis_instance" "cache" {
  name           = "${var.project_name}-${var.environment}"
  memory_size_gb = var.redis_memory_gb
  region         = var.gcp_region
  tier           = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  redis_version  = "REDIS_7_0"
  authorized_network = google_compute_network.vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  display_name       = "${var.project_name} Redis"
}

# ── Cloud Armor ──────────────────────────────────────
resource "google_compute_security_policy" "armor" {
  name = "${var.project_name}-waf"
  rule {
    action   = "deny(403)"
    priority = 1000
    match {
      versioned_expr = "SRC_IPS_V1"
      config { src_ip_ranges = ["0.0.0.0/0"] }
    }
    description = "Default deny"
  }
  rule {
    action   = "allow"
    priority = 1
    match {
      expr { expression = "request.path.startsWith('/health') || request.path.startsWith('/api')" }
    }
    description = "Allow API and health"
  }
}

# ── Cloud Monitoring ─────────────────────────────────
resource "google_monitoring_dashboard" "main" {
  dashboard_json = jsonencode({
    displayName = "${var.project_name} Dashboard"
    gridLayout = {
      widgets = [
        {
          title = "GKE CPU"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = { timeSeriesFilter = { filter = "metric.type=\"kubernetes.io/container/cpu/core_usage_time\"" } }
            }]
          }
        },
        {
          title = "Cloud SQL Connections"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = { timeSeriesFilter = { filter = "metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\"" } }
            }]
          }
        }
      ]
    }
  })
}