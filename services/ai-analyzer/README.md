# AI Analyzer Service

This service handles AI analysis operations in our microservices architecture.

## What It Does

- ✅ **Analyze Commits**: Use AI to analyze Git commits
- ✅ **Analyze Code Changes**: Review code changes with AI
- ✅ **AI Insights**: Provide code quality and security insights
- ✅ **Ollama Integration**: Use local AI models for analysis

## API Endpoints

### Health Check
```
GET /health
```

### Analyze Commit
```
GET /analyze/commit/{commit_hash}
```

### Analyze Commit (POST)
```
POST /analyze/commit
{
  "commit_hash": "abc123",
  "repository_name": "my-app"
}
```

### Analyze Code Changes
```
POST /analyze/code
{
  "code_changes": "def new_function():\n    return 'hello world'"
}
```

### Get AI Status
```
GET /status
```

### Get Available Models
```
GET /models
```

### Test AI Analysis
```
POST /test
```

## AI Models Used

### Code Llama
- **Purpose**: Code analysis and review
- **Model**: `codellama:7b`
- **Use Cases**: Code quality, bug detection, security analysis

### Llama 2
- **Purpose**: General commit analysis
- **Model**: `llama2:7b`
- **Use Cases**: Commit message analysis, impact assessment

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

The service will start on port 8004 by default.

## Prerequisites

### Install Ollama
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull codellama:7b
ollama pull llama2:7b

# Start Ollama
ollama serve
```

## Environment Variables

- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: newDB)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: root)
- `OLLAMA_BASE_URL`: Ollama API URL (default: http://localhost:11434)
- `CODE_LLAMA_MODEL`: Code Llama model name (default: codellama:7b)
- `OLLAMA_MODEL`: Llama 2 model name (default: llama2:7b)
- `AI_SERVICE_PORT`: Service port (default: 8004)

## Example Usage

### Analyze a Commit
```bash
curl -X GET http://localhost:8004/analyze/commit/abc123
```

### Analyze Code Changes
```bash
curl -X POST http://localhost:8004/analyze/code \
  -H "Content-Type: application/json" \
  -d '{
    "code_changes": "def login(user, password):\n    return user == \"admin\" and password == \"123456\""
  }'
```

### Check AI Status
```bash
curl http://localhost:8004/status
```
