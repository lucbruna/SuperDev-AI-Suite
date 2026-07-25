# SuperDev Infrastructure

Infrastructure-as-Code and DevOps configurations.

## Components

| Component | Description |
|-----------|-------------|
| [Terraform](terraform/) | Cloud infrastructure provisioning |
| [Ansible](ansible/) | Server configuration management |
| [Docker](compose/) | Container orchestration |
| [Kubernetes](kubernetes/) | Container orchestration |
| [Monitoring](monitoring/) | Prometheus + Grafana |
| [Logging](logging/) | Fluentd + Filebeat |
| [CI/CD](cd/) | GitHub Actions |
| [Security](security/) | OPA + Vault |
| [Network](network/) | Traefik reverse proxy |

## Quick Start

```bash
# Local development
docker-compose up -d

# Production (Terraform)
cd terraform
terraform init
terraform plan
terraform apply
```

## Directory Structure

```
infrastructure/
├── terraform/          # IaC for AWS/Azure/GCP
├── ansible/            # Configuration management
├── compose/            # Docker Compose files
├── kubernetes/         # K8s manifests
├── helm/               # Helm charts
├── monitoring/         # Prometheus + Grafana
├── logging/            # Fluentd + Filebeat
├── security/           # OPA policies + Vault
├── network/            # Traefik config
├── cloud/              # Cloud-specific configs
├── certificates/       # TLS certificates
├── backups/            # Backup scripts
├── cd/                 # CI/CD pipelines
├── observability/      # OpenTelemetry
├── scripts/            # Utility scripts
├── templates/          # Config templates
└── tests/              # Infrastructure tests
```
