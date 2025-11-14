# Kubernetes CI/CD GitLab Setup - Complete Scenario

This document provides a step-by-step scenario for setting up and executing the Kubernetes CI/CD pipeline with GitLab.

## Prerequisites

### 1. Environment Setup

Ensure the following GitLab CI/CD variables are configured in your GitLab project:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `VAULT_ADDR`
- `VAULT_TOKEN`

### 2. GitLab Runner Setup

- GitLab Runner must be installed on an EC2 instance
- Runner must be registered with the tag `data-core`
- Docker must be installed on the EC2 instance

## Step-by-Step Scenario

### Phase 1: Build Custom Docker Image

#### Step 1.1: Build the devops-tools Image on EC2

SSH into your EC2 instance where GitLab Runner is installed:

```bash
# Navigate to your project directory
cd /path/to/your/project

# Build the Docker image
docker build -t devops-tools .

# Verify the image was created
docker images | grep devops-tools

# Test the image
docker run --rm devops-tools aws --version
docker run --rm devops-tools vault version
docker run --rm devops-tools kubectl version --client
docker run --rm devops-tools python3 --version
docker run --rm devops-tools pytest --version
```

#### Step 1.2: Verify All Tools Work

```bash
# Test AWS CLI
docker run --rm -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
  devops-tools aws s3 ls

# Test Vault CLI
docker run --rm -e VAULT_ADDR=$VAULT_ADDR \
  -e VAULT_TOKEN=$VAULT_TOKEN \
  devops-tools vault status

# Test kubectl (after setting up kubeconfig)
docker run --rm -v $(pwd)/kubeconfig:/root/.kube/config \
  devops-tools kubectl cluster-info
```

### Phase 2: GitLab Project Setup

#### Step 2.1: Create GitLab Project

1. Log into GitLab
2. Create a new project named `k8s-integration-tests`
3. Initialize with a README (optional)

#### Step 2.2: Push Project Files

```bash
# Initialize git repository (if not already done)
git init

# Add remote
git remote add origin <your-gitlab-repo-url>

# Add all files
git add .

# Commit
git commit -m "Initial commit: Kubernetes CI/CD setup"

# Push to GitLab
git push -u origin main
```

### Phase 3: Configure GitLab CI/CD Variables

1. Go to your GitLab project
2. Navigate to **Settings** → **CI/CD** → **Variables**
3. Add the following variables (mark sensitive ones as masked/protected):
   - `AWS_ACCESS_KEY_ID` (masked, protected)
   - `AWS_SECRET_ACCESS_KEY` (masked, protected)
   - `AWS_DEFAULT_REGION` (e.g., `us-east-1`)
   - `VAULT_ADDR` (e.g., `https://vault.example.com:8200`)
   - `VAULT_TOKEN` (masked, protected)

### Phase 4: Verify GitLab Runner

#### Step 4.1: Check Runner Status

```bash
# On EC2 instance, check runner status
gitlab-runner list

# Verify runner is active and has the correct tag
gitlab-runner verify
```

#### Step 4.2: Test Runner Connection

1. Go to GitLab project → **Settings** → **CI/CD** → **Runners**
2. Verify your runner with tag `data-core` is active and available

### Phase 5: Pipeline Execution

#### Step 5.1: Trigger Pipeline

1. Push any commit to trigger the pipeline, or
2. Go to **CI/CD** → **Pipelines** → **Run Pipeline**

#### Step 5.2: Monitor Pipeline Execution

The pipeline will execute in two stages:

**Stage 1: Deploy**
- Uses `devops-tools` Docker image
- Exports environment variables
- Retrieves kubeconfig from Vault
- Applies Kubernetes manifests from `deployments/` directory
- Waits for deployments and pods to be ready
- Shows pod and service status

**Stage 2: Test**
- Uses the same `devops-tools` image
- Runs pytest scripts from `tests/` directory
- Validates all three services (MySQL, Elasticsearch, Nginx)

### Phase 6: Understanding the Tests

#### Test 1: MySQL Database

**What it does:**
1. Connects to MySQL via NodePort (30306)
2. Verifies `testdb` database exists
3. Verifies `results` table exists with correct structure
4. Queries for the record with `test_id='VAFT-001'`
5. Asserts the record has `status='pass'`

**Kubernetes Resources:**
- Deployment with MySQL 8.0
- Service (NodePort on port 30306)
- ConfigMap with initialization SQL script
- emptyDir volume for storage

#### Test 2: Elasticsearch

**What it does:**
1. Connects to Elasticsearch via NodePort (30200)
2. Creates `test-results` index with proper mapping
3. Inserts three test records
4. Queries for `test_id='VAFT-004'`
5. Asserts the status is `'pass'`

**Kubernetes Resources:**
- Deployment with Elasticsearch 8.11.0
- Service (NodePort on port 30200)
- Security disabled (xpack.security.enabled: false)

#### Test 3: Nginx Web Server

**What it does:**
1. Connects to Nginx via NodePort (30080)
2. Fetches the default HTML page
3. Verifies it contains "Welcome to nginx"

**Kubernetes Resources:**
- Deployment with Nginx latest
- Service (NodePort on port 30080)

### Phase 7: Troubleshooting

#### Common Issues and Solutions

**Issue 1: Docker image not found**
```bash
# Solution: Ensure image is built on EC2 instance
docker build -t devops-tools .
```

**Issue 2: kubectl connection failed**
- Verify kubeconfig is correctly retrieved from Vault
- Check Vault token has access to the secret
- Verify Kubernetes cluster is accessible from EC2

**Issue 3: Pods not becoming ready**
```bash
# Check pod status
kubectl get pods

# Check pod logs
kubectl logs <pod-name>

# Check pod events
kubectl describe pod <pod-name>
```

**Issue 4: Tests failing to connect**
- Verify NodePort services are accessible
- Check if `KUBERNETES_NODE_IP` environment variable is set correctly
- Ensure firewall rules allow traffic on NodePorts (30306, 30200, 30080)

**Issue 5: MySQL connection timeout**
- Wait longer for MySQL to initialize (may take 30-60 seconds)
- Check MySQL pod logs for initialization errors

**Issue 6: Elasticsearch not ready**
- Elasticsearch may take 1-2 minutes to start
- Check resource limits (memory/CPU)
- Verify Java heap size settings

### Phase 8: Manual Testing (Optional)

#### Test MySQL Manually

```bash
# Get node IP
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')

# Connect to MySQL
mysql -h $NODE_IP -P 30306 -u root -prootpassword testdb

# Query the table
SELECT * FROM results;
```

#### Test Elasticsearch Manually

```bash
# Query Elasticsearch
curl http://$NODE_IP:30200/test-results/_search?q=test_id:VAFT-004
```

#### Test Nginx Manually

```bash
# Fetch Nginx page
curl http://$NODE_IP:30080
```

### Phase 9: Cleanup (Optional)

To clean up Kubernetes resources:

```bash
# Delete all deployments and services
kubectl delete -f deployments/

# Or delete individually
kubectl delete deployment mysql-deployment
kubectl delete service mysql-service
kubectl delete configmap mysql-initdb
kubectl delete deployment elasticsearch-deployment
kubectl delete service elasticsearch-service
kubectl delete deployment nginx-deployment
kubectl delete service nginx-service
```

## Project Structure

```
k8s-integration-tests/
├── Dockerfile                 # Custom devops-tools image
├── .gitlab-ci.yml            # CI/CD pipeline definition
├── requirements.txt          # Python dependencies
├── SCENARIO.md              # This file
├── deployments/             # Kubernetes manifests
│   ├── mysql-deployment.yaml
│   ├── elasticsearch-deployment.yaml
│   └── nginx-deployment.yaml
└── tests/                   # Pytest test scripts
    ├── __init__.py
    ├── test_mysql.py
    ├── test_elasticsearch.py
    └── test_nginx.py
```

## Key Points

1. **Docker Image**: Must be built on EC2 instance where GitLab Runner runs
2. **GitLab Runner**: Must have tag `data-core` to match pipeline jobs
3. **Environment Variables**: Must be set in GitLab CI/CD variables
4. **Vault Integration**: kubeconfig is retrieved from Vault at runtime
5. **NodePort Services**: Services are exposed on specific ports (30306, 30200, 30080)
6. **Test Retries**: Tests include retry logic to handle service startup delays
7. **Kubernetes Node IP**: May need to be set as environment variable for tests to connect

## Next Steps

1. Build the Docker image on your EC2 instance
2. Push all files to GitLab
3. Configure CI/CD variables
4. Trigger the pipeline
5. Monitor execution and review test results

