# Repository Manager Service

This service handles all repository-related operations in our microservices architecture.

## What It Does

- ✅ **Manage Repositories**: Track and manage Git repositories
- ✅ **Repository Statistics**: Get analytics for repositories
- ✅ **Repository Commits**: Get commits for specific repositories
- ✅ **Repository Details**: Get detailed information about repositories

## API Endpoints

### Health Check
```
GET /health
```

### Get All Repositories
```
GET /repos
```

### Get Specific Repository
```
GET /repos/{repository_name}
```

### Get Repository Commits
```
GET /repos/{repository_name}/commits?limit=100
```

### Add New Repository
```
POST /repos
{
  "repository_name": "my-app",
  "commit_hash": "abc123",
  "author": "john_doe",
  "message": "Initial commit"
}
```

### Get Repository Statistics
```
GET /repos/statistics
```

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

The service will start on port 8002 by default.

## Environment Variables

- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: newDB)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: root)
- `REPO_SERVICE_PORT`: Service port (default: 8002)
