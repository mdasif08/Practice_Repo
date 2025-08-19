# Commit Tracker Service

This service handles all commit-related operations in our microservices architecture.

## What It Does

- ✅ **Track Commits**: Save new commits to the database
- ✅ **Get Commits**: Retrieve commits by hash or repository
- ✅ **Commit Statistics**: Get commit analytics and metrics
- ✅ **Repository Commits**: Get all commits for a specific repository

## API Endpoints

### Health Check
```
GET /health
```

### Get All Commits
```
GET /commits?limit=100
```

### Get Specific Commit
```
GET /commits/{commit_hash}
```

### Add New Commit
```
POST /commits
{
  "commit_hash": "abc123",
  "author": "john_doe",
  "message": "Fix bug in login",
  "repository_name": "my-app"
}
```

### Get Repository Commits
```
GET /commits/repository/{repository_name}?limit=100
```

### Get Statistics
```
GET /commits/statistics
```

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

The service will start on port 8001 by default.

## Environment Variables

- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: newDB)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: root)
- `COMMIT_SERVICE_PORT`: Service port (default: 8001)
