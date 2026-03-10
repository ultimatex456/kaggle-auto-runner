# Kaggle Auto Runner

Automated Kaggle notebook runner with usage limits and n8n scheduling.

## Limits
- Session    : 6 hours
- Per Week   : 4 runs / 24 hours
- Per Month  : 15 runs / 90 hours
- Interval   : Every 2 days (Day 1,3,5,7...)

## GitHub Secrets Required
| Secret           | Value                    |
|------------------|--------------------------|
| KAGGLE_USERNAME  | Your Kaggle username     |
| KAGGLE_KEY       | Your Kaggle API key      |
| KERNEL_NAME      | kaggle-auto-runner       |
| GH_PAT           | GitHub Personal Token    |

## Setup
1. Fork/clone this repo
2. Add secrets in GitHub Settings
3. Update kernel-metadata.json with your username
4. Import n8n workflow JSON
5. Set your webhook URL in n8n

## Trigger via API
curl -X POST \
  -H "Authorization: token YOUR_GH_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/YOUR_USERNAME/kaggle-auto-runner/dispatches \
  -d '{"event_type":"trigger-kaggle"}'
