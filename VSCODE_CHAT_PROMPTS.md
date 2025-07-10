# VS Code Chat Prompts for Code Review Agent

## 🎯 **Extended Prompts for Comprehensive Code Reviews**

These prompts will help your agent understand the ADK server context and perform thorough code reviews from VS Code chat.

### 🔍 **Code Analysis Prompts**

#### **Basic Analysis**
```
Analyze this TypeScript code for quality issues and best practices
```

#### **Comprehensive Analysis**
```
Perform a comprehensive code review of this file including:
- Type safety and TypeScript best practices
- Performance and security considerations  
- Code organization and maintainability
- Framework-specific patterns (React/Node.js/etc.)
- Auto-fixable issues and manual improvements
```

#### **Framework-Specific Analysis**
```
Review this Playwright test file for:
- Test structure and naming conventions
- Locator strategies and wait patterns
- Console statement removal
- Page Object Model usage
- Assertion quality and test reliability
```

```
Analyze this Cucumber feature file for:
- Gherkin syntax and BDD best practices
- Scenario structure and Given-When-Then flow
- Step definition clarity and reusability
- Business language vs technical implementation
- Data table and scenario outline usage
```

### 🔧 **Auto-Fix Prompts**

#### **General Fixes**
```
Fix all auto-fixable issues in this code including:
- Console statement removal from test files
- Import organization and cleanup
- Basic type annotation additions
- Formatting and style corrections
- Unused variable removal
```

#### **Specific Fixes**
```
Clean up this Playwright test by:
- Removing all console.log/warn/error statements
- Converting CSS selectors to semantic locators
- Replacing hard waits with explicit waits
- Improving test structure and naming
```

### 📋 **Standards and Best Practices Prompts**

#### **Framework Standards**
```
Show me the complete TypeScript coding standards including:
- Type safety requirements
- Modern syntax preferences
- Code organization patterns
- Performance considerations
- Security best practices
```

```
What are the Playwright testing standards for:
- Test structure and organization
- Locator strategies and element selection
- Wait patterns and timing
- Assertion patterns and reliability
- Page Object Model implementation
```

### 💡 **Educational and Guidance Prompts**

#### **Learning-Focused**
```
Explain the issues in this code and teach me:
- Why each issue is problematic
- How to fix them properly
- Best practices to prevent similar issues
- Modern alternatives and patterns
- Framework-specific recommendations
```

#### **Architecture Guidance**
```
Help me improve the architecture of this code by:
- Suggesting better organization patterns
- Identifying separation of concerns issues
- Recommending design patterns
- Highlighting maintainability concerns
- Proposing scalability improvements
```

### 🎯 **Context-Aware Prompts**

#### **Project Context**
```
As an expert TypeScript/Playwright/Cucumber code reviewer running on an ADK server:
- Analyze this [file_type] file for comprehensive quality issues
- Apply framework-specific best practices and standards
- Identify both auto-fixable and manual improvement opportunities
- Provide educational explanations for each recommendation
- Consider the file's role in the larger project architecture
```

#### **VS Code Integration Context**
```
I'm working in VS Code with this [framework] project. Please:
- Review the selected code for quality and best practices
- Highlight issues that can be automatically fixed
- Suggest improvements specific to [TypeScript/Playwright/Cucumber]
- Provide actionable next steps I can take in my IDE
- Explain any complex issues in beginner-friendly terms
```

### 🚀 **Advanced Analysis Prompts**

#### **Security-Focused**
```
Perform a security-focused code review checking for:
- Input validation and sanitization
- Authentication and authorization issues
- Data exposure and privacy concerns
- Dependency vulnerabilities
- Configuration security
```

#### **Performance-Focused**
```
Analyze this code for performance optimization opportunities:
- Algorithmic efficiency improvements
- Memory usage optimization
- Bundle size and loading performance
- Database query optimization
- Async/await pattern improvements
```

#### **Accessibility-Focused**
```
Review this frontend code for accessibility compliance:
- ARIA attributes and semantic HTML
- Keyboard navigation support
- Screen reader compatibility
- Color contrast and visual accessibility
- Focus management patterns
```

### 🔄 **Iterative Review Prompts**

#### **Follow-up Analysis**
```
I've made the changes you suggested. Please:
- Re-analyze the updated code
- Confirm the issues have been resolved
- Identify any new issues introduced
- Suggest further improvements
- Validate the applied fixes
```

#### **Specific Issue Deep-dive**
```
Focus specifically on [issue_type] in this code:
- Provide detailed explanation of the problem
- Show multiple solution approaches
- Explain trade-offs between solutions
- Give examples of best practices
- Suggest preventive measures
```

### 🎨 **Custom Prompt Templates**

#### **Template 1: Comprehensive Review**
```
As a senior TypeScript/Playwright/Cucumber code reviewer with ADK server capabilities:

**Context**: [Describe your project/component]
**Goal**: [What you want to achieve]
**Focus Areas**: [Specific areas of concern]

Please analyze this code and provide:
1. 🔍 **Issue Analysis**: Categorized by severity (Error/Warning/Info)
2. 🔧 **Auto-Fix Opportunities**: What can be automatically corrected
3. 👨‍💻 **Manual Improvements**: What requires developer attention
4. 📚 **Educational Insights**: Why each recommendation matters
5. 🎯 **Next Steps**: Prioritized action items

Code to review:
[Your code here]
```

#### **Template 2: Framework-Specific Review**
```
Expert [Framework] code review with ADK-powered analysis:

**File Type**: [TypeScript Component/Playwright Test/Cucumber Feature]
**Framework Version**: [If relevant]
**Project Context**: [Brief description]

Analyze for:
- ✅ Framework best practices compliance
- 🚫 Anti-patterns and code smells
- 🔧 Auto-fixable issues
- 💡 Optimization opportunities
- 📖 Learning opportunities

Provide structured feedback with examples and explanations.
```

### 🎯 **Quick Action Prompts**

#### **One-Line Prompts for Common Tasks**
```
Quick analysis: What's wrong with this code?
```

```
Auto-fix: Clean up this file automatically
```

```
Standards check: Does this follow [framework] best practices?
```

```
Security review: Any security concerns in this code?
```

```
Performance check: How can I optimize this code?
```

### 📱 **Mobile/Responsive Prompts**

#### **For Frontend Code**
```
Review this component for mobile responsiveness:
- CSS/styling best practices
- Touch interaction patterns
- Performance on mobile devices
- Accessibility on small screens
- Progressive enhancement
```

### 🧪 **Testing-Focused Prompts**

#### **Test Quality Review**
```
Evaluate this test suite for:
- Test coverage and completeness
- Test reliability and stability
- Assertion quality and specificity
- Test organization and maintainability
- Mock usage and test isolation
```

### 💼 **Enterprise/Team Prompts**

#### **Team Standards Compliance**
```
Review this code against our team standards:
- Coding conventions and style guide
- Architecture patterns and principles
- Documentation requirements
- Code review checklist compliance
- Deployment and CI/CD considerations
```

## 🎯 **How to Use These Prompts**

### **In VS Code Copilot Chat:**

1. **Open Copilot Chat** (`Ctrl/Cmd + Shift + I`)
2. **Select your code** or open the file you want to review
3. **Copy and paste** any of the above prompts
4. **Customize** the prompt with your specific context
5. **Send** and get comprehensive analysis

### **Example Usage:**
```
User: Perform a comprehensive code review of this file including:
- Type safety and TypeScript best practices
- Performance and security considerations  
- Code organization and maintainability
- Auto-fixable issues and manual improvements

[Selected TypeScript code]

Agent: 🔍 **Comprehensive Code Review Results**

**File**: `component.ts` (TypeScript)
**Issues Found**: 8 (2 errors, 4 warnings, 2 suggestions)

🔴 **Critical Issues** (2):
1. Line 15: Missing return type annotation for async function
   💡 **Fix**: Add `: Promise<UserData>` to function signature
   📖 **Why**: Explicit return types improve type safety and IDE support

2. Line 23: Using 'any' type defeats TypeScript benefits
   💡 **Fix**: Define proper interface for user object
   📖 **Why**: Specific types catch errors at compile time

[Detailed analysis continues...]
```

## 🚀 **Pro Tips**

1. **Be Specific**: The more context you provide, the better the analysis
2. **Use Templates**: Customize the templates for your specific needs
3. **Iterate**: Use follow-up prompts to dive deeper into specific issues
4. **Learn**: Ask for explanations to improve your coding skills
5. **Automate**: Use the auto-fix capabilities for routine improvements

Your ADK-powered code review agent is ready to provide comprehensive, educational, and actionable code reviews directly in VS Code! 🎉
