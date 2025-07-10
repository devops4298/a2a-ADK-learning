# Production Setup Guide

This guide shows how to deploy the TypeScript Playwright Cucumber Code Review Agent as a production A2A server that integrates with VS Code Copilot Chat.

## 🚀 Quick Start

### Option 1: Direct Python Deployment

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Set Environment Variables**:
   ```bash
   export ENVIRONMENT=production
   export HOST=0.0.0.0
   export PORT=8080
   export GOOGLE_API_KEY=your_api_key_here
   ```

3. **Start the A2A Server**:
   ```bash
   python start_a2a_server.py
   ```

### Option 2: Docker Deployment

1. **Build and Run with Docker**:
   ```bash
   docker build -t ts-code-reviewer .
   docker run -p 8080:8080 \
     -e GOOGLE_API_KEY=your_api_key_here \
     ts-code-reviewer
   ```

2. **Or use Docker Compose**:
   ```bash
   # Create .env file with your API key
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   
   # Start the service
   docker-compose up -d
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment mode (development/production/testing) |
| `HOST` | `localhost` | Server host address |
| `PORT` | `8080` | Server port |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `GOOGLE_API_KEY` | - | Google AI API key (optional) |
| `GOOGLE_CLOUD_PROJECT` | - | Google Cloud project (optional) |
| `MAX_FILE_SIZE` | `1048576` | Maximum file size in bytes (1MB) |
| `ENABLE_ESLINT` | `true` | Enable ESLint integration |
| `ENABLE_PRETTIER` | `true` | Enable Prettier integration |
| `ENABLE_CUSTOM_RULES` | `true` | Enable custom rules |

### Production Configuration

For production deployment, create a `.env` file:

```bash
# Production settings
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8080
DEBUG=false
LOG_LEVEL=INFO

# Google AI (optional - for enhanced features)
GOOGLE_API_KEY=your_google_ai_api_key
GOOGLE_CLOUD_PROJECT=your_project_id

# Feature toggles
ENABLE_ESLINT=true
ENABLE_PRETTIER=true
ENABLE_CUSTOM_RULES=true

# Limits
MAX_FILE_SIZE=2097152  # 2MB
```

## 🔗 VS Code Copilot Chat Integration

### Automatic Discovery

Once your A2A server is running, VS Code Copilot Chat will automatically discover it if:

1. **Local Development**: Server runs on `localhost:8080`
2. **Network Access**: VS Code can reach your server URL
3. **A2A Protocol**: Server implements the A2A protocol correctly

### Manual Configuration

If automatic discovery doesn't work, you can manually configure VS Code:

1. **Open VS Code Settings** (`Cmd/Ctrl + ,`)
2. **Search for "copilot chat agents"**
3. **Add your agent URL**: `http://your-server:8080`

### Usage in VS Code

Once connected, you can use the agent in Copilot Chat:

```
@ts-reviewer analyze this TypeScript code
@ts-reviewer fix issues in this Playwright test
@ts-reviewer show me Cucumber standards
@ts-reviewer help
```

## 🛠 A2A Server Capabilities

The agent exposes these capabilities through the A2A protocol:

### 1. `analyze_code`
Analyzes code content for quality issues.

**Request**:
```json
{
  "content": "your TypeScript code",
  "file_path": "src/component.ts",
  "file_type": "typescript"
}
```

**Response**:
```json
{
  "success": true,
  "total_issues": 5,
  "issues": [...],
  "summary": {...},
  "recommendations": [...]
}
```

### 2. `fix_code`
Applies automated fixes to code.

**Request**:
```json
{
  "content": "your code with issues",
  "file_path": "test.spec.ts"
}
```

**Response**:
```json
{
  "success": true,
  "fixed_content": "corrected code",
  "content_changed": true,
  "applied_fixes": [...],
  "manual_suggestions": [...]
}
```

### 3. `get_standards`
Returns coding standards information.

**Request**:
```json
{
  "category": "typescript",
  "auto_fixable": true
}
```

**Response**:
```json
{
  "success": true,
  "standards": [...],
  "total_count": 25,
  "categories": ["typescript", "playwright", "cucumber"]
}
```

### 4. `chat`
Natural language chat interface.

**Request**:
```json
{
  "message": "analyze this code",
  "context": {
    "content": "code content",
    "file_path": "file.ts"
  }
}
```

**Response**:
```json
{
  "success": true,
  "response": "Found 3 issues in your code...",
  "suggestions": [...]
}
```

## 🔒 Security Considerations

### Production Security

1. **Network Security**:
   - Use HTTPS in production
   - Implement proper firewall rules
   - Consider VPN access for internal use

2. **API Security**:
   - Implement rate limiting
   - Add authentication if needed
   - Validate all inputs

3. **Container Security**:
   - Use non-root user (already configured)
   - Keep base images updated
   - Scan for vulnerabilities

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring and Logging

### Health Check

The server provides a health check endpoint:

```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "service": "ts-playwright-cucumber-reviewer",
  "version": "1.0.0"
}
```

### Logs

Logs are written to:
- **Console**: Real-time output
- **File**: `code_review_agent.log`

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### Monitoring

For production monitoring, consider:
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **ELK Stack**: Log aggregation
- **Uptime monitoring**: Service availability

## 🚀 Deployment Options

### 1. Local Development
```bash
python start_a2a_server.py --host localhost --port 8080 --debug
```

### 2. Docker Container
```bash
docker run -d \
  --name code-reviewer \
  -p 8080:8080 \
  -e ENVIRONMENT=production \
  ts-code-reviewer
```

### 3. Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-review-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: code-review-agent
  template:
    metadata:
      labels:
        app: code-review-agent
    spec:
      containers:
      - name: agent
        image: ts-code-reviewer:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: google-api-secret
              key: api-key
```

### 4. Cloud Platforms

#### Google Cloud Run
```bash
gcloud run deploy code-review-agent \
  --image gcr.io/your-project/ts-code-reviewer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### AWS ECS/Fargate
```bash
aws ecs create-service \
  --cluster your-cluster \
  --service-name code-review-agent \
  --task-definition code-reviewer:1
```

## 🧪 Testing the Integration

### 1. Test A2A Server
```bash
# Check health
curl http://localhost:8080/health

# Test analyze capability
curl -X POST http://localhost:8080/capabilities/analyze_code \
  -H "Content-Type: application/json" \
  -d '{"content": "console.log(\"test\");", "file_path": "test.ts"}'
```

### 2. Test VS Code Integration
1. Start the A2A server
2. Open VS Code
3. Open Copilot Chat
4. Try: `@ts-reviewer help`

### 3. Verify Capabilities
```bash
# List available capabilities
curl http://localhost:8080/capabilities
```

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   lsof -i :8080
   kill -9 <PID>
   ```

2. **VS Code Can't Discover Agent**:
   - Check server is running: `curl http://localhost:8080/health`
   - Verify A2A protocol implementation
   - Check VS Code logs for errors

3. **Permission Errors**:
   - Ensure proper file permissions
   - Check Docker user configuration

4. **Memory Issues**:
   - Monitor memory usage
   - Adjust Docker memory limits
   - Optimize code analysis batch sizes

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python start_a2a_server.py
```

## 📞 Support

For issues and questions:
1. Check the logs: `tail -f code_review_agent.log`
2. Verify configuration: Environment variables and ports
3. Test individual components: Analyzers, linters, fixers
4. Check A2A protocol compliance

---

**🎉 Your TypeScript Playwright Cucumber Code Review Agent is now production-ready and integrated with VS Code Copilot Chat via the A2A protocol!**
