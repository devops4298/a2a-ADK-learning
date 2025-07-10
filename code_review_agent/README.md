# TypeScript Playwright Cucumber Code Review Agent

A comprehensive AI-powered code review and linting assistant built with Google's Agent Development Kit (ADK), specifically designed for TypeScript-based Playwright Cucumber automation projects.

## 🚀 Features

### 1. **Comprehensive Code Standards**
- **TypeScript Best Practices**: 13 standards covering naming conventions, type safety, code structure, imports, and error handling
- **Playwright Automation Patterns**: 17 standards for Page Object Model, locator best practices, waiting patterns, test structure, and performance
- **Cucumber BDD Conventions**: 19 standards for Gherkin syntax, scenario quality, step definitions, and documentation
- **Project-Specific Guidelines**: Custom rules for file organization, configuration, and testing strategy

### 2. **Multi-Layer Analysis**
- **Static Code Analysis**: Pattern-based detection of code quality issues
- **Linting Integration**: ESLint for TypeScript, Prettier for formatting, custom project rules
- **File Type Detection**: Automatically applies relevant standards based on file type (.ts, .spec.ts, .feature)
- **Severity Classification**: Issues categorized as error, warning, or info with compliance scoring

### 3. **One-Click Fix Functionality**
- **Automated Fixes**: Instantly fix naming conventions, formatting, imports, and simple code issues
- **Manual Suggestions**: Detailed guidance for complex issues requiring human intervention
- **Before/After Previews**: See exactly what changes will be applied
- **Backup Creation**: Automatic backup of original files before modifications

### 4. **Comprehensive Reporting**
- **Detailed Issue Reports**: Line numbers, descriptions, severity levels, and fix suggestions
- **Compliance Scoring**: 0-100 score based on code quality metrics
- **Category Breakdown**: Issues grouped by type (naming, type-safety, locators, etc.)
- **Progress Tracking**: Track improvements over time

### 5. **Local Operation**
- **No External Dependencies**: Works entirely locally without requiring external API calls for linting
- **Privacy Focused**: Your code never leaves your machine
- **Fast Analysis**: Instant feedback on code quality issues

## 📁 Project Structure

```
code_review_agent/
├── __init__.py
├── agent.py                 # Main ADK agent with tool functions
├── .env                     # Environment configuration
├── README.md               # This file
├── standards/              # Code standards definitions
│   ├── typescript_standards.py
│   ├── playwright_standards.py
│   ├── cucumber_standards.py
│   └── project_standards.py
├── analyzers/              # Code analysis engines
│   ├── base_analyzer.py
│   ├── typescript_analyzer.py
│   ├── playwright_analyzer.py
│   ├── cucumber_analyzer.py
│   └── file_analyzer.py
├── linters/                # Linting tool integrations
│   ├── eslint_linter.py
│   ├── prettier_linter.py
│   ├── custom_linter.py
│   └── linter_manager.py
├── fixers/                 # Automated fixing capabilities
│   ├── auto_fixer.py
│   ├── manual_fixer.py
│   └── fix_manager.py
├── reporters/              # Report generation
│   ├── base_reporter.py
│   └── report_manager.py
└── test_samples/           # Sample files for testing
    ├── typescript/
    ├── playwright/
    └── cucumber/
```

## 🛠 Setup Instructions

### Prerequisites
- Python 3.9+
- Google ADK installed (`pip install google-adk`)
- Valid Google AI API key or Vertex AI setup

### Installation

1. **Navigate to the agent directory**:
   ```bash
   cd code_review_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install google-adk ast-tools pylint autopep8 black isort python-dotenv
   ```

3. **Configure environment**:
   - Edit `.env` file with your Google AI credentials
   - For Google AI Studio: Set `GOOGLE_API_KEY`
   - For Vertex AI: Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`

## 🎯 Usage

### Command Line Interface

```bash
# Start the agent
adk run code_review_agent

# Or use the web interface
adk web
```

### Available Commands

1. **Analyze Single File**:
   ```
   Please analyze the TypeScript file at path/to/your/file.ts
   ```

2. **Analyze Directory**:
   ```
   Can you analyze all files in the src/ directory?
   ```

3. **One-Click Fix**:
   ```
   Apply one-click fix to path/to/your/file.ts
   ```

4. **Get Coding Standards**:
   ```
   What coding standards are available?
   ```

5. **Check Linter Status**:
   ```
   What's the status of the linting tools?
   ```

### Example Interactions

**Analyzing a TypeScript file**:
```
[user]: Please analyze src/utils/userService.ts
[agent]: Found 8 issues in src/utils/userService.ts:
- 3 naming convention violations (auto-fixable)
- 2 type safety issues (manual fix required)
- 1 missing error handling (manual fix required)
- 2 formatting issues (auto-fixable)

Compliance Score: 78/100
```

**Applying one-click fix**:
```
[user]: Apply one-click fix to src/utils/userService.ts
[agent]: ✅ Applied 5 automated fixes:
- Fixed camelCase naming for 3 variables
- Added missing semicolons
- Fixed quote consistency

🔧 3 issues require manual attention:
- Add explicit return type to processUser() function
- Implement proper error handling for async operations
- Consider breaking down validateAndSaveUser() function
```

## 📊 Code Standards Coverage

### TypeScript Standards (13 rules)
- **Naming Conventions**: camelCase variables, PascalCase classes, UPPER_SNAKE_CASE constants
- **Type Safety**: Explicit types, avoid 'any', null checking
- **Code Structure**: Single responsibility, function length, prefer const
- **Imports**: Import order, unused imports
- **Error Handling**: Try-catch blocks, custom error types

### Playwright Standards (17 rules)
- **Page Object Model**: Class naming, interaction patterns
- **Locator Best Practices**: Stable locators, avoid XPath, semantic selectors
- **Waiting Patterns**: Explicit waits, auto-waiting, no hard waits
- **Test Structure**: Descriptive names, test isolation, setup/teardown
- **Assertions**: Playwright assertions, specific matchers
- **Performance**: Browser contexts, parallel execution

### Cucumber Standards (19 rules)
- **Feature Structure**: Proper Gherkin format, user story format
- **Scenario Quality**: Descriptive names, business language
- **Given-When-Then**: Proper flow, imperative mood, no UI details
- **Step Definitions**: Reusability, parameterization, organization
- **Data Management**: Data tables, scenario outlines, external data
- **Tags and Organization**: Meaningful tags, consistent conventions

## 🔧 Customization

### Adding Custom Rules

```python
# Add to custom_linter.py
custom_rule = {
    'id': 'project-specific-rule',
    'pattern': r'your-regex-pattern',
    'message': 'Your rule description',
    'severity': 'warning',
    'category': 'custom',
    'auto_fixable': True,
    'suggestion': 'How to fix this issue'
}

linter.add_custom_rule(custom_rule)
```

### Configuring ESLint Rules

```python
# Update ESLint configuration
eslint_rules = {
    '@typescript-eslint/no-unused-vars': 'error',
    'prefer-const': 'warn',
    'no-console': 'off'  # Allow console in development
}

linter_manager.configure_eslint(eslint_rules)
```

## 📈 Benefits

1. **Consistency**: Enforce consistent coding standards across your team
2. **Quality**: Catch issues early in the development process
3. **Efficiency**: Automated fixes save time on routine code improvements
4. **Learning**: Detailed explanations help developers improve their skills
5. **Maintainability**: Better code structure leads to easier maintenance

## 🧪 Testing

The agent includes sample files with intentional issues for testing:

```bash
# Test with sample files
adk run code_review_agent

# Then try:
"Analyze code_review_agent/test_samples/typescript/bad_example.ts"
"Analyze code_review_agent/test_samples/playwright/bad_test.spec.ts"
"Analyze code_review_agent/test_samples/cucumber/bad_example.feature"
```

## 🤝 Contributing

1. Add new standards to the appropriate standards file
2. Implement analyzers for new patterns
3. Create automated fixes for common issues
4. Add test cases for new functionality

## 📝 License

This project is for educational and development purposes. Please refer to Google's ADK license for usage terms.

---

**Built with ❤️ using Google's Agent Development Kit**
