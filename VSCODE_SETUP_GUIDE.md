# VS Code Setup & Usage Guide

## 🚀 **Step-by-Step VS Code Configuration**

### Prerequisites
- ✅ VS Code installed with GitHub Copilot extension
- ✅ Your code review agent server running on `localhost:8080`

### Step 1: Start Your Agent Server

```bash
# Navigate to your project
cd /Users/chetanchauhan/Agentic/a2a-ADK-learning

# Start the server
python3 start_a2a_server.py --host localhost --port 8080

# Verify it's running
curl http://localhost:8080/health
# Should return: {"status":"healthy","agent_id":"ts-playwright-cucumber-reviewer"...}
```

### Step 2: Configure VS Code

#### Option A: GitHub Copilot Chat Integration

1. **Open VS Code**
2. **Install GitHub Copilot** (if not already installed):
   - Go to Extensions (`Ctrl/Cmd + Shift + X`)
   - Search for "GitHub Copilot"
   - Install both "GitHub Copilot" and "GitHub Copilot Chat"

3. **Open Copilot Chat**:
   - Press `Ctrl/Cmd + Shift + I`
   - Or click the chat icon in the Activity Bar
   - Or use Command Palette: `Ctrl/Cmd + Shift + P` → "Copilot Chat: Open Chat"

#### Option B: REST Client Extension (For Direct API Testing)

1. **Install REST Client Extension**:
   - Extensions → Search "REST Client" → Install

2. **Create API Test File**:
   - Create `test-agent.http` in your project
   - Add the test requests (see examples below)

### Step 3: Using the Agent

#### Method 1: Through Copilot Chat (Recommended)

**✅ Working Commands** (Chat interface is fully functional):

```
# General Help
help
what can you do?
show me your capabilities

# Coding Standards (Working)
show me typescript coding standards
what are playwright best practices?
show cucumber standards
what rules should I follow?

# Code Improvement Guidance
how should I structure my playwright tests?
what are the best practices for typescript?
help me understand cucumber scenarios
```

**Example Chat Session**:
```
You: help
Agent: 🤖 TypeScript Playwright Cucumber Code Reviewer

I can help you with:
🔍 Code Analysis: "Analyze this code" or "Check for issues"
🔧 Auto-Fix: "Fix this code" or "Apply automated fixes"  
📋 Standards: "Show coding standards" or "What are the rules?"
...

You: show me typescript coding standards
Agent: 📋 TypeScript Coding Standards (X rules):
🔴 Critical Rules:
• rule-id: description
...
```

#### Method 2: Direct API Testing with REST Client

Create a file `test-agent.http`:

```http
### Health Check
GET http://localhost:8080/health

### Agent Information
GET http://localhost:8080/agent

### Get Coding Standards
GET http://localhost:8080/standards?category=typescript

### Get Playwright Standards
GET http://localhost:8080/standards?category=playwright

### Chat Interface (Working)
POST http://localhost:8080/chat
Content-Type: application/json

{
  "message": "help",
  "context": {}
}

### Chat with Context
POST http://localhost:8080/chat
Content-Type: application/json

{
  "message": "show me typescript standards",
  "context": {
    "file_path": "src/component.ts"
  }
}

### Chat for Playwright Help
POST http://localhost:8080/chat
Content-Type: application/json

{
  "message": "what are playwright best practices?",
  "context": {
    "file_path": "tests/login.spec.ts"
  }
}
```

#### Method 3: Command Line Testing

```bash
# Test chat interface
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "help", "context": {}}'

# Get standards
curl http://localhost:8080/standards?category=playwright

# Agent info
curl http://localhost:8080/agent
```

## 🎯 **Practical Usage Examples**

### Scenario 1: Getting Help with TypeScript

**In VS Code Copilot Chat**:
```
You: I'm working on a TypeScript project. What coding standards should I follow?

Agent: 📋 TypeScript Coding Standards (25 rules):

🔴 Critical Rules (5):
• ts-no-any: Avoid using 'any' type
• ts-explicit-return-types: Functions should have explicit return types
• ts-no-unused-vars: Remove unused variables

🟡 Best Practice Rules (20):
• ts-prefer-const: Use const for variables that are never reassigned
• ts-naming-convention: Follow consistent naming conventions
...

🔧 15 rules can be automatically fixed
```

### Scenario 2: Playwright Test Guidance

**In VS Code Copilot Chat**:
```
You: I'm writing Playwright tests. What are the best practices?

Agent: 📋 Playwright Testing Coding Standards (18 rules):

🔴 Critical Rules (3):
• pw-no-hard-waits: Avoid page.waitForTimeout()
• pw-use-locators: Use semantic locators instead of CSS selectors
• pw-no-console-in-tests: Avoid console statements in tests

🟡 Best Practice Rules (15):
• pw-test-naming: Use descriptive test names
• pw-page-object-model: Use Page Object Model pattern
...
```

### Scenario 3: Cucumber BDD Help

**In VS Code Copilot Chat**:
```
You: How should I structure my Cucumber scenarios?

Agent: 📋 Cucumber BDD Coding Standards (12 rules):

🔴 Critical Rules (2):
• cucumber-scenario-structure: Follow Given-When-Then structure
• cucumber-step-definitions: Keep step definitions simple

🟡 Best Practice Rules (10):
• cucumber-descriptive-scenarios: Write clear scenario descriptions
• cucumber-data-tables: Use data tables for complex data
...
```

## 🔧 **Advanced Configuration**

### Custom VS Code Settings

Add to your VS Code `settings.json`:

```json
{
  "copilot.enable": {
    "*": true,
    "yaml": false,
    "plaintext": false
  },
  "github.copilot.advanced": {
    "debug.overrideEngine": "codex"
  },
  "github.copilot.chat.localeOverride": "en"
}
```

### Workspace Configuration

Create `.vscode/settings.json` in your project:

```json
{
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "typescript.suggest.autoImports": true,
  "playwright.reuseBrowser": true,
  "playwright.showTrace": true,
  "files.associations": {
    "*.feature": "gherkin"
  }
}
```

## 🛠 **Troubleshooting**

### Issue 1: Copilot Chat Not Finding Agent

**Solution**:
1. Verify server is running: `curl http://localhost:8080/health`
2. Check VS Code Copilot Chat settings
3. Try restarting VS Code
4. Use direct API calls to test functionality

### Issue 2: Agent Not Responding

**Solution**:
1. Check server logs for errors
2. Test with simple commands first: "help"
3. Verify network connectivity
4. Try different chat messages

### Issue 3: Standards Not Loading

**Solution**:
1. Test standards endpoint: `curl http://localhost:8080/standards`
2. Check if specific categories work: `?category=typescript`
3. Review server configuration

## 📊 **Current Status & Capabilities**

### ✅ **Working Features**
- **Chat Interface**: Fully functional natural language interaction
- **Standards Retrieval**: Get coding standards by category
- **Help System**: Comprehensive help and guidance
- **Server Health**: Monitoring and status checks
- **Multi-Framework Support**: TypeScript, Playwright, Cucumber

### 🔄 **In Development**
- **File Analysis**: Direct code analysis (has regex issue)
- **Auto-Fix**: Automated code fixing (depends on analysis)

### 🎯 **Best Current Usage**
1. **Use Chat Interface** for guidance and standards
2. **Ask for Best Practices** for your specific framework
3. **Get Coding Standards** for TypeScript/Playwright/Cucumber
4. **Seek Help** with specific development questions

## 🚀 **Quick Start Commands**

```bash
# 1. Start the server
python3 start_a2a_server.py

# 2. Test it's working
curl http://localhost:8080/health

# 3. Open VS Code and try Copilot Chat:
# "help"
# "show me typescript standards"
# "what are playwright best practices?"
```

## 🎉 **Success!**

Your code review agent is now configured and ready to use in VS Code! The chat interface provides excellent guidance on coding standards and best practices for TypeScript, Playwright, and Cucumber development.

**Start with these commands in VS Code Copilot Chat**:
- `help` - Get overview of capabilities
- `show me typescript standards` - TypeScript best practices
- `what are playwright best practices?` - Playwright guidance
- `how should I structure cucumber scenarios?` - BDD guidance
