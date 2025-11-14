# 🚀 Quick Start Guide - 5 Simple Steps

## Step 1: Build Docker Image on EC2 ⚙️

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Clone or upload your project
git clone <your-gitlab-repo-url>
cd k8s-integration-tests

# Build the image
docker build -t devops-tools .

# Verify
docker images | grep devops-tools
```

**✅ Done when:** Image `devops-tools` appears in `docker images`

---

## Step 2: Push Code to GitLab 📤

```bash
# On your local Windows machine
cd "C:\Users\ASUS\Downloads\kubernetes cicd gitlab"

# Initialize and push (if first time)
git init
git remote add origin <your-gitlab-repo-url>
git add .
git commit -m "Initial commit"
git push -u origin main
```

**✅ Done when:** Files appear in GitLab project

---

## Step 3: Add GitLab Variables 🔐

1. Go to GitLab project → **Settings** → **CI/CD** → **Variables**
2. Add these 5 variables:

   | Variable | Value | Masked? |
   |----------|-------|---------|
   | `AWS_ACCESS_KEY_ID` | your-key | ✅ Yes |
   | `AWS_SECRET_ACCESS_KEY` | your-secret | ✅ Yes |
   | `AWS_DEFAULT_REGION` | us-east-1 | ❌ No |
   | `VAULT_ADDR` | https://vault-url:8200 | ❌ No |
   | `VAULT_TOKEN` | your-token | ✅ Yes |

**✅ Done when:** All 5 variables show in the list

---

## Step 4: Run Pipeline ▶️

1. Go to GitLab project → **CI/CD** → **Pipelines**
2. Click **Run pipeline** button
3. Select branch: `main`
4. Click **Run pipeline**

**✅ Done when:** Pipeline appears and starts running

---

## Step 5: Check Results ✅

1. Click on the running pipeline
2. Watch both jobs:
   - **deploy** → Should turn green ✓
   - **test** → Should turn green ✓
3. Click **test** job to see:
   ```
   10 passed
   ```

**✅ Done when:** Both jobs show green checkmarks!

---

## 🆘 Need Help?

- **Pipeline stuck?** Check runner is active: Settings → CI/CD → Runners
- **Tests failing?** Click on failed job to see error logs
- **Image not found?** Rebuild on EC2: `docker build -t devops-tools .`

---

**That's it! Your CI/CD pipeline is now running! 🎉**

