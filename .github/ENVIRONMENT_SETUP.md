# GitHub Environment Protection Setup

To enable the security features in the CI/CD workflows, you need to set up GitHub environments with protection rules.

## Required Environments

### 1. `production` Environment
- **Purpose**: For building and pushing Docker images to production
- **Protection Rules**:
  - Required reviewers: Add at least 1 reviewer (yourself or team members)
  - Wait timer: Optional 5-10 minute wait
  - Restrict deployments to: `main` branch only

### 2. `release` Environment  
- **Purpose**: For creating GitHub releases
- **Protection Rules**:
  - Required reviewers: Add at least 1 reviewer
  - Restrict deployments to: Tags matching `v*` pattern only

### 3. `pypi` Environment (Optional)
- **Purpose**: For publishing packages to PyPI
- **Protection Rules**:
  - Required reviewers: Add at least 1 reviewer
  - Restrict deployments to: Tags matching `v*` pattern only
  - Secrets: `PYPI_API_TOKEN`

## Setup Instructions

1. Go to your repository settings
2. Navigate to "Environments" in the left sidebar
3. Click "New environment" for each environment above
4. Configure protection rules as specified
5. Add required secrets to each environment

## Required Secrets

- `GITHUB_TOKEN`: Automatically provided by GitHub
- `PYPI_API_TOKEN`: Create at https://pypi.org/manage/account/token/ (for PyPI publishing)

## Benefits

- **Manual approval required**: No accidental deployments
- **Branch/tag restrictions**: Only deploy from appropriate sources  
- **Audit trail**: Track who approved deployments and when
- **Secret isolation**: Sensitive tokens only available in protected environments