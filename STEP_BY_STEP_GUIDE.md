# Step-by-Step Guide: Complete Setup and Execution

Follow these steps in order to set up and run your Kubernetes CI/CD pipeline.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- ✅ GitLab account and a project created
- ✅ EC2 instance with Docker installed
- ✅ GitLab Runner installed on EC2 with tag `data-core`
- ✅ Kubernetes cluster access
- ✅ Vault access for kubeconfig
- ✅ AWS credentials

---

## Step 1: Build Docker Image on EC2

### 1.1 Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 1.2 Upload Project Files to EC2

**Option A: Using SCP (from your local machine)**
```bash
scp -i your-key.pem -r "C:\Users\ASUS\Downloads\kubernetes cicd gitlab" ec2-user@your-ec2-ip:/home/ec2-user/
```

**Option B: Using Git (recommended)**
```bash
# On EC2
cd /home/ec2-user
git clone <your-gitlab-repo-url>
cd k8s-integration-tests  # or your project name
```

### 1.3 Build the Docker Image

```bash
# Navigate to project directory
cd /home/ec2-user/kubernetes\ cicd\ gitlab
# or
cd /home/ec2-user/k8s-integration-tests

# Build the image
docker build -t devops-tools .

# Wait for build to complete (takes 2-5 minutes)
```

### 1.4 Verify the Image

```bash
# Check if image was created
docker images | grep devops-tools

# Test the image
docker run --rm devops-tools aws --version
docker run --rm devops-tools kubectl version --client
docker run --rm devops-tools python3 --version
docker run --rm devops-tools pytest --version
```

**✅ Expected Output:**
- AWS CLI version
- kubectl version
- Python 3.x.x
- pytest version

---

## Step 2: Push Code to GitLab

### 2.1 Initialize Git Repository (if not already done)

On your **local machine** (Windows):

```bash
cd "C:\Users\ASUS\Downloads\kubernetes cicd gitlab"

# Initialize git (if needed)
git init

# Add GitLab remote (replace with your actual GitLab URL)
git remote add origin https://gitlab.com/your-username/k8s-integration-tests.git
# OR if using SSH:
# git remote add origin git@gitlab.com:your-username/k8s-integration-tests.git
```

### 2.2 Create .gitignore (if needed)

```bash
# Create .gitignore to exclude unnecessary files
echo ".venv/" > .gitignore
echo ".pytest_cache/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".DS_Store" >> .gitignore
```

### 2.3 Add and Commit Files

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: Kubernetes CI/CD setup with tests"

# Push to GitLab
git push -u origin main
# OR if your default branch is master:
# git push -u origin master
```

**✅ Success:** You should see files uploaded to GitLab.

---

## Step 3: Configure GitLab CI/CD Variables

### 3.1 Open GitLab Project

1. Go to your GitLab project: `https://gitlab.com/your-username/k8s-integration-tests`
2. Click on **Settings** (left sidebar)
3. Click on **CI/CD** (under Settings)
4. Expand **Variables** section

### 3.2 Add Required Variables

Click **Add variable** for each of these:

| Variable Name | Value | Type | Protected | Masked |
|--------------|-------|------|-----------|--------|
| `AWS_ACCESS_KEY_ID` | `your-aws-access-key` | Variable | ☐ | ☑ |
| `AWS_SECRET_ACCESS_KEY` | `your-aws-secret-key` | Variable | ☐ | ☑ |
| `AWS_DEFAULT_REGION` | `us-east-1` (or your region) | Variable | ☐ | ☐ |
| `VAULT_ADDR` | `https://your-vault-url:8200` | Variable | ☐ | ☐ |
| `VAULT_TOKEN` | `your-vault-token` | Variable | ☐ | ☑ |

**Important:**
- Check **Masked** for sensitive values (passwords, tokens, keys)
- Click **Add variable** after each entry
- Double-check all values are correct

**✅ Success:** All 5 variables should be listed in the Variables section.

---

## Step 4: Verify GitLab Runner

### 4.1 Check Runner Status in GitLab

1. In your GitLab project, go to **Settings** → **CI/CD**
2. Expand **Runners** section
3. Verify you see a runner with tag `data-core` and status **Active**

### 4.2 Verify Runner on EC2 (Optional)

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Check runner status
sudo gitlab-runner list

# Verify runner is running
sudo gitlab-runner status
```

**✅ Success:** Runner should show as active in GitLab.

---

## Step 5: Run the Pipeline

### 5.1 Trigger Pipeline Manually

**Option A: Via GitLab UI (Easiest)**
1. Go to your GitLab project
2. Click **CI/CD** → **Pipelines** (left sidebar)
3. Click **Run pipeline** button (top right)
4. Select branch: `main` (or `master`)
5. Click **Run pipeline**

**Option B: Via Git Push**
```bash
# Make a small change and push
echo "# Pipeline trigger" >> README.md
git add README.md
git commit -m "Trigger pipeline"
git push
```

### 5.2 Monitor Pipeline Execution

1. Click on the pipeline (you'll see it in the Pipelines list)
2. Watch the stages:

   **Stage 1: deploy**
   - ✅ Job starts
   - ✅ Uses `devops-tools` image
   - ✅ Exports environment variables
   - ✅ Gets kubeconfig from Vault
   - ✅ Applies Kubernetes manifests
   - ✅ Waits for pods to be ready
   - ✅ Shows pod and service status

   **Stage 2: test**
   - ✅ Job starts after deploy completes
   - ✅ Gets kubeconfig
   - ✅ Gets Kubernetes node IP
   - ✅ Runs pytest tests
   - ✅ Shows test results

### 5.3 Check Pipeline Status

**Green checkmark (✓)** = Success
**Red X (✗)** = Failed (click to see logs)

**✅ Success:** Both stages should show green checkmarks.

---

## Step 6: View Test Results

### 6.1 View Pipeline Logs

1. Click on the pipeline
2. Click on **test** job
3. Scroll down to see test output
4. You should see:
   ```
   ========================== test session starts ==========================
   tests/test_mysql.py::test_mysql_connection PASSED
   tests/test_mysql.py::test_mysql_database_exists PASSED
   tests/test_mysql.py::test_mysql_table_exists PASSED
   tests/test_mysql.py::test_mysql_table_structure PASSED
   tests/test_mysql.py::test_mysql_record_exists PASSED
   tests/test_elasticsearch.py::test_elasticsearch_connection PASSED
   tests/test_elasticsearch.py::test_elasticsearch_index_exists PASSED
   tests/test_elasticsearch.py::test_elasticsearch_query_vaft_004 PASSED
   tests/test_nginx.py::test_nginx_connection PASSED
   tests/test_nginx.py::test_nginx_default_page PASSED
   ========================== 10 passed ==========================
   ```

### 6.2 Download Artifacts (Optional)

1. In the pipeline view, click on **test** job
2. Look for **Browse** button in the right sidebar
3. Download `pytest-report.xml` if needed

---

## 🔧 Troubleshooting Common Issues

### Issue 1: Docker Image Not Found

**Error:** `pull access denied for devops-tools`

**Solution:**
```bash
# On EC2, verify image exists
docker images | grep devops-tools

# If not found, rebuild
docker build -t devops-tools .
```

### Issue 2: GitLab Runner Not Picking Up Jobs

**Error:** Jobs stuck in "Pending" state

**Solution:**
1. Check runner tags match: `data-core`
2. Verify runner is active in GitLab
3. Check runner logs on EC2:
   ```bash
   sudo gitlab-runner run
   ```

### Issue 3: Vault Connection Failed

**Error:** `Error reading secret/kubeconfig`

**Solution:**
1. Verify `VAULT_ADDR` and `VAULT_TOKEN` are correct
2. Test Vault connection:
   ```bash
   vault kv get secret/kubeconfig
   ```

### Issue 4: Kubernetes Connection Failed

**Error:** `The connection to the server was refused`

**Solution:**
1. Verify kubeconfig is correct
2. Test kubectl access:
   ```bash
   kubectl cluster-info
   ```

### Issue 5: Tests Failing

**Error:** Connection timeouts in tests

**Solution:**
1. Check if pods are running:
   ```bash
   kubectl get pods
   kubectl get services
   ```
2. Verify NodePort services are accessible
3. Check pod logs:
   ```bash
   kubectl logs <pod-name>
   ```

---

## 📝 Quick Reference Commands

### On EC2:
```bash
# Build image
docker build -t devops-tools .

# Check image
docker images | grep devops-tools

# Test image
docker run --rm devops-tools kubectl version --client
```

### On Local Machine:
```bash
# Navigate to project
cd "C:\Users\ASUS\Downloads\kubernetes cicd gitlab"

# Push to GitLab
git add .
git commit -m "Your message"
git push
```

### In GitLab:
- **Pipelines:** CI/CD → Pipelines
- **Variables:** Settings → CI/CD → Variables
- **Runners:** Settings → CI/CD → Runners

---

## ✅ Final Checklist

Before running pipeline, verify:
- [ ] Docker image `devops-tools` built on EC2
- [ ] Code pushed to GitLab
- [ ] All 5 CI/CD variables configured
- [ ] GitLab Runner active with tag `data-core`
- [ ] Kubernetes cluster accessible
- [ ] Vault credentials correct

---

## 🎉 Success!

Once the pipeline completes successfully:
- ✅ All Kubernetes resources deployed
- ✅ All 10 tests passed
- ✅ MySQL, Elasticsearch, and Nginx are running
- ✅ Services accessible via NodePort

**Congratulations! Your CI/CD pipeline is working!** 🚀

