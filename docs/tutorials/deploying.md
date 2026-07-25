# Deploying

## Local Deployment

```bash
superdev deploy --env local
```

## Docker Deployment

```bash
superdev deploy --env docker
```

## Kubernetes Deployment

```bash
superdev deploy --env kubernetes --cluster my-cluster
```

## Cloud Deployment

```bash
# AWS
superdev deploy --env aws --region us-east-1

# Azure
superdev deploy --env azure --resource-group my-rg

# GCP
superdev deploy --env gcp --project my-project
```

## Rollback

```bash
superdev deploy --rollback
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPERDEV_ENV` | Target environment |
| `SUPERDEV_REGION` | Cloud region |
| `SUPERDEV_CLUSTER` | Kubernetes cluster |
| `SUPERDEV_REGISTRY` | Container registry |
