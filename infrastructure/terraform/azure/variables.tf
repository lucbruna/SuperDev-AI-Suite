variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "azure_location" {
  type    = string
  default = "East US"
}

variable "node_count" {
  type    = number
  default = 3
}
