# Webhook Handler Service

This service handles GitHub webhooks and commit fetching in our microservices architecture.

## What It Does

- ✅ **Handle GitHub Webhooks**: Process push, create, and delete events
- ✅ **Fetch Commits**: Get commits from GitHub repositories
- ✅ **Process Events**: Handle different types of GitHub events
- ✅ **Save Commits**: Store commits in the database

## API Endpoints

### Health Check
```
GET /health
```

### Handle GitHub Webhook
```
POST /webhook/github
```

### Fetch Commits from Repository
```
POST /fetch-commits
{
  "repo_owner": "mdasif08",
  "repo_name": "my-app",
  "max_commits": 10
}
```

### Get Webhook Events
```
GET /webhook/events
```

## GitHub Webhook Events

### Push Event
When code is pushed to a repository:
- Processes all commits in the push
- Saves commits to database
- Tracks file changes

### Create Event
When a new branch or tag is created:
- Logs the creation
- Tracks the new reference

### Delete Event
When a branch or tag is deleted:
- Logs the deletion
- Updates tracking

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

The service will start on port 8003 by default.

## Environment Variables

- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: newDB)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: root)
- `GITHUB_TOKEN`: GitHub API token (optional)
- `WEBHOOK_SERVICE_PORT`: Service port (default: 8003)

## Setting Up GitHub Webhooks

1. Go to your GitHub repository
2. Navigate to Settings > Webhooks
3. Add webhook with URL: `http://your-server:8003/webhook/github`
4. Select events: Push, Create, Delete
5. Save the webhook
