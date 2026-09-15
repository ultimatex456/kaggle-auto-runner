# Kaggle Auto Runner
Automated Daily Kaggle notebook runner with n8n scheduling.

## Daily Runtime Settings
- **Session Duration**: 4 Hours
- **Schedule**: Every day at 8:00 PM IST (14:30 UTC)
- **Weekly Total**: 28 Hours (Safely under Kaggle's 30h limit)

## GitHub Secrets Required
| Secret | Value |
| --- | --- |
| `KAGGLE_USERNAME` | Your Kaggle username |
| `KAGGLE_KEY` | Your Kaggle API key |
| `KERNEL_NAME` | kaggle-auto-runner |
| `GH_PAT` | GitHub Personal Token |

## Setup Instructions
1. Fork/clone this repo.
2. Add secrets in **GitHub Settings > Secrets and variables > Actions**.
3. Import the updated, simplified n8n workflow.
4. It will trigger smoothly and alert you via Telegram automatically!
