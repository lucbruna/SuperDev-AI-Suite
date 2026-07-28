variable "project_name" { default = "superdev" }
variable "environment" { default = "production" }
variable "azure_subscription_id" { type = string }
variable "azure_location" { default = "eastus" }
variable "aks_version" { default = "1.28" }
variable "aks_vm_size" { default = "Standard_D4s_v3" }
variable "aks_min_nodes" { default = 3 }
variable "aks_max_nodes" { default = 20 }
variable "pg_admin_username" { default = "superdev_admin" }
variable "pg_sku" { default = "GP_Standard_D4ds_v4" }
variable "pg_storage_gb" { default = 100 }
variable "pg_db_name" { default = "superdev" }
variable "redis_capacity" { default = 2 }
variable "vnet_cidr" { default = ["10.0.0.0/16"] }
variable "private_cidr" { default = ["10.0.1.0/24"] }
variable "tags" { default = { Project = "superdev", ManagedBy = "terraform" } }