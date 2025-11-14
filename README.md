# Kubernetes CI/CD GitLab Integration Tests

This project implements a complete CI/CD pipeline for deploying and testing Kubernetes applications using GitLab CI/CD.

## Overview

The project includes:
- Custom Docker image (`devops-tools`) with all required tools
- GitLab CI/CD pipeline with deploy and test stages
- Kubernetes manifests for MySQL, Elasticsearch, and Nginx
- Pytest test suites for validating all deployments

## Quick Start

### 1. Build Docker Image

On your EC2 instance (where GitLab Runner is installed):

```bash
docker build -t devops-tools .
```

### 2. Configure GitLab CI/CD Variables

In GitLab project → Settings → CI/CD → Variables, add:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `VAULT_ADDR`
- `VAULT_TOKEN`

### 3. Push to GitLab

```bash
git init
git remote add origin <your-gitlab-repo-url>
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 4. Run Pipeline

The pipeline will automatically run on push, or manually trigger it from GitLab UI.

## Project Structure

```
.
├── Dockerfile                      # Custom devops-tools image
├── .gitlab-ci.yml                 # CI/CD pipeline definition
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── SCENARIO.md                    # Detailed scenario guide
├── deployments/                   # Kubernetes manifests
│   ├── mysql-deployment.yaml
│   ├── elasticsearch-deployment.yaml
│   └── nginx-deployment.yaml
└── tests/                         # Pytest test scripts
    ├── __init__.py
    ├── test_mysql.py
    ├── test_elasticsearch.py
    └── test_nginx.py
```

## Services

### MySQL
- **NodePort**: 30306
- **Database**: testdb
- **Table**: results
- **Test**: Validates database connection and record existence

### Elasticsearch
- **NodePort**: 30200
- **Index**: test-results
- **Test**: Queries for test_id='VAFT-004' and validates status='pass'

### Nginx
- **NodePort**: 30080
- **Test**: Validates default page contains "Welcome to nginx"

## Pipeline Stages

1. **Deploy**: Applies Kubernetes manifests and waits for pods to be ready
2. **Test**: Runs pytest scripts to validate all services

## Requirements

- GitLab Runner with tag `data-core`
- Docker installed on EC2 instance
- Kubernetes cluster access via kubeconfig from Vault
- GitLab CI/CD variables configured

## Documentation

For detailed setup instructions and troubleshooting, see [SCENARIO.md](SCENARIO.md).

