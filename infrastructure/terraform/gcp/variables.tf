variable "project_name" {
  type = string
}

variable "gcp_project_id" {
  type = string
}

variable "gcp_region" {
  type    = string
  default = "us-central1"
}

variable "node_count" {
  type    = number
  default = 3
}
