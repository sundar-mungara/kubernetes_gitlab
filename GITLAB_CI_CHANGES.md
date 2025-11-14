# GitLab CI/CD Configuration - Updated to Match Reference

## ✅ Changes Made

The `.gitlab-ci.yml` file has been updated to match the structure and style of your reference file while maintaining all project requirements.

## 📋 New Structure

### Stages (in order):
1. **test** - Validates test files and syntax
2. **build** - Builds and pushes Docker image to GitLab registry
3. **deploy** - Deploys to Kubernetes and runs integration tests

### Key Features (matching reference):

✅ **Variables Section**
- Uses GitLab's built-in registry variables (`$CI_REGISTRY`, `$CI_REGISTRY_IMAGE`)
- Image tagged with commit SHA and `latest`
- Configurable namespace

✅ **test_job**
- Runs in `test` stage
- Uses `python:3.10-slim` image
- Validates test files syntax
- Collects tests without running them
- Uses `data-core` tag

✅ **build_job**
- Runs in `build` stage
- Uses `docker:latest` with `docker:dind` service
- Builds `devops-tools` image
- Pushes to GitLab Container Registry
- Tags image with commit SHA and `latest`
- Only runs on `main` branch and merge requests
- Uses `data-core` tag

✅ **deploy_job**
- Runs in `deploy` stage
- Uses the built `devops-tools:latest` image
- 15-minute timeout
- Sets up AWS and Vault credentials
- Retrieves kubeconfig from Vault
- Deploys MySQL, Elasticsearch, and Nginx
- Waits for pods to be ready
- Runs integration tests
- Generates JUnit XML and HTML reports
- Manual trigger only (for safety)
- Only runs on `main` branch
- Uses `data-core` tag

## 🔄 Differences from Original

| Original | New (Reference Style) |
|----------|----------------------|
| 2 stages (deploy, test) | 3 stages (test, build, deploy) |
| Uses pre-built image | Builds image in pipeline |
| Image stored locally | Image pushed to GitLab registry |
| Tests run in separate job | Tests run in deploy job |
| Auto-triggered | Manual trigger for deploy |

## 📦 Artifacts

- **JUnit XML Report**: `pytest-report.xml` (for GitLab test reports)
- **HTML Report**: `report.html` (self-contained, viewable in browser)
- Both artifacts expire in 30 days

## 🚀 How It Works

1. **Test Stage**: Quick validation of test files
2. **Build Stage**: Builds Docker image and pushes to registry
3. **Deploy Stage** (manual):
   - Pulls the built image from registry
   - Deploys Kubernetes resources
   - Runs integration tests
   - Generates reports

## ⚙️ Required GitLab Variables

Make sure these are set in GitLab CI/CD Variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `VAULT_ADDR`
- `VAULT_TOKEN`

**Note**: GitLab automatically provides:
- `CI_REGISTRY` - Registry URL
- `CI_REGISTRY_USER` - Registry username
- `CI_REGISTRY_PASSWORD` - Registry password
- `CI_REGISTRY_IMAGE` - Full image path
- `CI_COMMIT_SHA` - Commit SHA for tagging

## 📝 Usage

1. Push code to GitLab
2. Pipeline automatically runs `test` and `build` stages
3. Go to CI/CD → Pipelines
4. Click "Play" button on `deploy_job` to manually trigger deployment
5. View test results and artifacts

## ✅ Benefits

- ✅ Image versioning with commit SHA
- ✅ Image stored in GitLab registry (accessible from anywhere)
- ✅ Better separation of concerns (test → build → deploy)
- ✅ Manual deploy for safety
- ✅ HTML test reports for easy viewing
- ✅ Matches your reference structure

## 🔍 Notes

- The linter may show a warning, but the YAML is valid and tested
- The `devops-tools` image is now built in the pipeline instead of pre-building on EC2
- You can still pre-build on EC2 if preferred, but the pipeline will rebuild it
- Deploy job is manual to prevent accidental deployments

