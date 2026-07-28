variable "project_name" { default = "superdev" }
variable "environment" { default = "production" }
variable "gcp_project_id" { type = string }
variable "gcp_region" { default = "us-central1" }
variable "private_cidr" { default = "10.0.1.0/24" }
variable "public_cidr" { default = "10.0.101.0/24" }
variable "gke_min_nodes" { default = 3 }
variable "gke_max_nodes" { default = 20 }
variable "gke_machine_type" { default = "e2-standard-4" }
variable "cloudsql_tier" { default = "db-custom-4-16384" }
variable "cloudsql_disk_gb" { default = 100 }
variable "cloudsql_db_name" { default = "superdev" }
variable "cloudsql_username" { default = "superdev_admin" }
variable "redis_memory_gb" { default = 8 }
variable "tags" { default = { Project = "superdev", ManagedBy = "terraform" } }