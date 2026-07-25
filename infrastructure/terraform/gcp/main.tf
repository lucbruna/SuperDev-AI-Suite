resource "google_project_service" "main" {
  project = var.gcp_project_id
  service = "container.googleapis.com"
}

resource "google_container_cluster" "main" {
  name     = "${var.project_name}-gke"
  location = var.gcp_region

  initial_node_count = var.node_count

  master_auth {
    client_certificate_config {
      client_certificate_config = ""
    }
  }

  depends_on = [google_project_service.main]
}
