# CinemaAbyss Helm Chart

This Helm chart deploys the CinemaAbyss microservices platform on Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+

## Quick Start

```bash
# Install the chart
helm install cinemaabyss ./src/kubernetes/helm/cinemaabyss --namespace cinemaabyss --create-namespace

# Check the deployment status
kubectl -n cinemaabyss get pods

# Access the application
kubectl -n cinemaabyss port-forward service/proxy-service 8080:80
curl http://localhost:8080/health
```

## Configuration

### Image Pull Policy

All service images are set to `pullPolicy: Always` to ensure the latest versions are used. The images are publicly available in GitHub Container Registry:

- `ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/monolith:latest`
- `ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/movies-service:latest`
- `ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/events-service:latest`
- `ghcr.io/mnemchinov/yp_software_architect_sprint2_work1/proxy-service:latest`

### Database Configuration

The chart includes PostgreSQL with the following configuration:
- Database: `cinemaabyss`
- User: `postgres`
- Password: `postgres_password` (base64 encoded)

### Strangler Fig Configuration

The proxy service supports gradual migration with the following environment variables:
- `GRADUAL_MIGRATION`: "true" (enables gradual migration mode)
- `MOVIES_MIGRATION_PERCENT`: "100" (percentage of traffic to movies service)

## Services

| Service | Port | Description |
|---------|------|-------------|
| monolith | 8080 | Original monolithic application |
| movies-service | 8081 | Movies microservice |
| events-service | 8082 | Events microservice with Kafka |
| proxy-service | 8000 | API Gateway and proxy |
| postgres | 5432 | PostgreSQL database |
| kafka | 9092 | Kafka message broker |
| zookeeper | 2181 | Zookeeper for Kafka |

## Upgrading

```bash
# Upgrade the release
helm upgrade cinemaabyss ./src/kubernetes/helm/cinemaabyss --namespace cinemaabyss
```

## Uninstalling

```bash
# Uninstall the release
helm uninstall cinemaabyss --namespace cinemaabyss

# Delete the namespace
kubectl delete namespace cinemaabyss
```