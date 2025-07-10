"""
Enhanced chat handler that integrates with ADK server for comprehensive code reviews.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    from google.adk.core import Agent
    from google.adk.core.llm import LLMClient
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    logging.warning("ADK not available, using fallback chat handler")

from ..prompts.system_prompts import (
    get_system_prompt, 
    get_analysis_prompt,
    FRAMEWORK_SPECIFIC_PROMPTS
)
from ..analyzers.file_analyzer import FileAnalyzer
from ..fixers.fix_manager import FixManager
from ..standards.project_standards import ProjectStandards

logger = logging.getLogger(__name__)


class EnhancedChatHandler:
    """Enhanced chat handler with ADK integration for comprehensive code reviews."""
    
    def __init__(self):
        self.file_analyzer = FileAnalyzer()
        self.fix_manager = FixManager()
        self.standards = ProjectStandards()
        
        # Initialize ADK LLM client if available
        self.llm_client = None
        if ADK_AVAILABLE:
            try:
                self.llm_client = LLMClient()
                logger.info("ADK LLM client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize ADK LLM client: {e}")
    
    async def handle_chat_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle chat messages with enhanced ADK-powered responses.
        
        Args:
            message: User's chat message
            context: Context including file content, path, etc.
            
        Returns:
            Enhanced response with comprehensive code review
        """
        try:
            # Analyze user intent
            intent = self._analyze_user_intent(message)
            
            # Get file context
            file_path = context.get('file_path', '')
            content = context.get('content', '')
            selection = context.get('selection', '')
            
            # Use selection if available, otherwise full content
            code_to_analyze = selection if selection else content
            
            # Generate response based on intent
            if intent == 'analyze':
                response = await self._handle_analysis_request(message, file_path, code_to_analyze)
            elif intent == 'fix':
                response = await self._handle_fix_request(message, file_path, code_to_analyze)
            elif intent == 'standards':
                response = await self._handle_standards_request(message, file_path)
            elif intent == 'explain':
                response = await self._handle_explanation_request(message, file_path, code_to_analyze)
            elif intent == 'help':
                response = self._get_help_response(context)
            else:
                response = await self._handle_general_request(message, context)
            
            return {
                "success": True,
                "response": response,
                "intent": intent,
                "suggestions": self._generate_contextual_suggestions(intent, file_path),
                "follow_up_actions": self._get_follow_up_actions(intent, file_path),
                "quick_actions": self._generate_quick_actions(intent, file_path, code_to_analyze),
                "fixed_code": self._get_fixed_code_if_available(intent, file_path, code_to_analyze)
            }
            
        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request. Please try again or rephrase your question."
            }
    
    def _analyze_user_intent(self, message: str) -> str:
        """Analyze user message to determine intent."""
        message_lower = message.lower()
        
        # Analysis intent
        if any(word in message_lower for word in [
            'analyze', 'review', 'check', 'examine', 'look at', 'inspect', 'audit'
        ]):
            return 'analyze'
        
        # Fix intent
        if any(word in message_lower for word in [
            'fix', 'repair', 'correct', 'clean', 'improve', 'optimize'
        ]):
            return 'fix'
        
        # Standards intent
        if any(word in message_lower for word in [
            'standards', 'rules', 'guidelines', 'best practices', 'conventions'
        ]):
            return 'standards'
        
        # Explanation intent
        if any(word in message_lower for word in [
            'explain', 'why', 'how', 'what', 'understand', 'meaning'
        ]):
            return 'explain'
        
        # Help intent
        if any(word in message_lower for word in [
            'help', 'assist', 'guide', 'support', 'capabilities'
        ]):
            return 'help'
        
        return 'general'
    
    async def _handle_analysis_request(self, message: str, file_path: str, content: str) -> str:
        """Handle code analysis requests with contextual fix buttons."""

        if not content:
            return """🔍 **Code Analysis Request**

I'd be happy to analyze your code! Please:
1. Select the code you want me to review in VS Code
2. Or open a file and ask me to "analyze this file"
3. Or paste the code you'd like me to examine

I can analyze:
- 📄 TypeScript/JavaScript files
- 🧪 Playwright test files
- 📋 Cucumber feature files
- 🔧 Configuration files"""
        
        # Determine file type and get appropriate analysis
        file_type = self._get_file_type(file_path)
        
        # Use ADK LLM for enhanced analysis if available
        if self.llm_client and len(content) > 50:
            enhanced_response = await self._get_adk_analysis(file_path, content, file_type)
            if enhanced_response:
                return enhanced_response
        
        # Fallback to rule-based analysis
        return await self._get_rule_based_analysis(file_path, content, file_type)
    
    async def _get_adk_analysis(self, file_path: str, content: str, file_type: str) -> Optional[str]:
        """Get enhanced analysis using ADK LLM client."""
        try:
            # Get appropriate system prompt
            system_prompt = get_system_prompt(file_type)
            
            # Generate analysis prompt
            analysis_prompt = get_analysis_prompt(file_path, content)
            
            # Call ADK LLM
            response = await self.llm_client.generate_text(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            if response and response.text:
                return f"""🔍 **Enhanced Code Analysis** (Powered by ADK)

**File**: `{file_path}` ({file_type})

{response.text}

---
*Analysis powered by Google ADK with TypeScript/Playwright/Cucumber expertise*"""
            
        except Exception as e:
            logger.error(f"ADK analysis failed: {e}")
            return None
    
    async def _get_rule_based_analysis(self, file_path: str, content: str, file_type: str) -> str:
        """Get analysis using rule-based approach."""
        
        # Try to analyze with existing analyzer (may have regex issues)
        try:
            issues = self.file_analyzer.analyze_file(file_path, content)

            if issues:
                return self._format_issues_response_with_buttons(file_path, issues, file_type, content)
            else:
                return f"""✅ **Code Analysis Complete**

**File**: `{file_path}` ({file_type})

🎉 **Excellent!** No issues found in your code.

Your code follows good practices for {file_type} development. Keep up the great work!

💡 **Suggestions for further improvement**:
- Consider adding more comprehensive tests
- Review for accessibility improvements
- Check for performance optimization opportunities
- Ensure proper error handling"""
                
        except Exception as e:
            logger.warning(f"Rule-based analysis failed: {e}")
            return self._get_manual_analysis(file_path, content, file_type)
    
    def _get_manual_analysis(self, file_path: str, content: str, file_type: str) -> str:
        """Provide manual analysis when automated analysis fails."""
        
        issues_found = []
        
        # Check for common issues manually
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Console statements in test files
            if file_type == 'playwright' and 'console.' in line:
                issues_found.append(f"Line {i}: Remove console statement: `{line.strip()}`")
            
            # Missing type annotations
            if file_type == 'typescript' and re.search(r'function\s+\w+\s*\([^)]*\)\s*{', line):
                if ':' not in line:
                    issues_found.append(f"Line {i}: Consider adding return type annotation")
            
            # Hard waits in tests
            if 'waitForTimeout' in line:
                issues_found.append(f"Line {i}: Avoid hard waits, use explicit waits instead")
        
        if issues_found:
            issues_text = '\n'.join([f"   • {issue}" for issue in issues_found[:5]])
            more_text = f"\n   ... and {len(issues_found) - 5} more issues" if len(issues_found) > 5 else ""
            
            return f"""🔍 **Code Analysis Results**

**File**: `{file_path}` ({file_type})
**Issues Found**: {len(issues_found)}

🟡 **Issues Detected**:
{issues_text}{more_text}

💡 **Recommendations**:
- Review the flagged lines for improvements
- Apply {file_type}-specific best practices
- Consider using auto-fix for simple issues

🔧 **Next Steps**: Would you like me to help fix these issues?"""
        
        else:
            return f"""✅ **Code Analysis Complete**

**File**: `{file_path}` ({file_type})

🎉 **Great job!** No obvious issues detected in your code.

💡 **{file_type.title()} Best Practices Reminder**:
{self._get_framework_tips(file_type)}"""
    
    def _format_issues_response(self, file_path: str, issues: List, file_type: str) -> str:
        """Format issues into a comprehensive response."""
        
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']
        auto_fixable = [i for i in issues if i.auto_fixable]
        
        response = f"""🔍 **Code Analysis Results**

**File**: `{file_path}` ({file_type})
**Total Issues**: {len(issues)} ({len(errors)} errors, {len(warnings)} warnings)
**Auto-Fixable**: {len(auto_fixable)} issues

"""
        
        if errors:
            response += "🔴 **Critical Issues**:\n"
            for i, error in enumerate(errors[:3], 1):
                response += f"   {i}. Line {error.line_number}: {error.description}\n"
                if error.suggested_fix:
                    response += f"      💡 **Fix**: {error.suggested_fix}\n"
            if len(errors) > 3:
                response += f"   ... and {len(errors) - 3} more errors\n"
            response += "\n"
        
        if warnings:
            response += "🟡 **Warnings**:\n"
            for i, warning in enumerate(warnings[:3], 1):
                response += f"   {i}. Line {warning.line_number}: {warning.description}\n"
            if len(warnings) > 3:
                response += f"   ... and {len(warnings) - 3} more warnings\n"
            response += "\n"
        
        if auto_fixable:
            response += f"🔧 **Good News**: {len(auto_fixable)} issues can be automatically fixed!\n\n"

            # Add clickable buttons for VS Code Copilot Chat
            response += "**🔘 Quick Actions:**\n"
            response += f"- [**🔧 Apply All Fixes**](command:workbench.action.chat.applyInEditor?{{'text':'fix this code'}})\n"
            response += f"- [**📄 Show Fixed Code**](command:workbench.action.chat.insertIntoNewFile)\n"
            response += f"- [**🔍 Re-analyze After Fix**](command:workbench.action.chat.submit?{{'text':'analyze this code again'}})\n\n"

        response += "💡 **Next Steps**:\n"
        if auto_fixable:
            response += "   • Click 'Apply All Fixes' button above for automatic corrections\n"
            response += "   • Or ask me to 'fix this code' for automatic corrections\n"
        response += "   • Review the flagged issues for manual improvements\n"
        response += f"   • Apply {file_type}-specific best practices\n"
        
        return response

    def _format_issues_response_with_buttons(self, file_path: str, issues: List, file_type: str, content: str) -> str:
        """Format issues response with contextual clickable buttons."""

        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']
        auto_fixable = [i for i in issues if i.auto_fixable]

        response = f"""🔍 **Code Analysis Results**

**File**: `{file_path}` ({file_type})
**Total Issues**: {len(issues)} ({len(errors)} errors, {len(warnings)} warnings)
**Auto-Fixable**: {len(auto_fixable)} issues

"""

        if errors:
            response += "🔴 **Critical Issues**:\n"
            for i, error in enumerate(errors[:3], 1):
                response += f"   {i}. Line {error.line_number}: {error.description}\n"
                if error.suggested_fix:
                    response += f"      💡 **Fix**: {error.suggested_fix}\n"
            if len(errors) > 3:
                response += f"   ... and {len(errors) - 3} more errors\n"
            response += "\n"

        if warnings:
            response += "🟡 **Warnings**:\n"
            for i, warning in enumerate(warnings[:3], 1):
                response += f"   {i}. Line {warning.line_number}: {warning.description}\n"
            if len(warnings) > 3:
                response += f"   ... and {len(warnings) - 3} more warnings\n"
            response += "\n"

        # Add contextual buttons ONLY when there are auto-fixable issues AND code content
        if auto_fixable and content.strip():
            response += f"🔧 **Good News**: {len(auto_fixable)} issues can be automatically fixed!\n\n"

            # Add clickable buttons for VS Code Copilot Chat
            response += "**🔘 One-Click Actions:**\n"
            response += "```\n"
            response += "Click any button below to apply fixes:\n"
            response += "```\n"
            response += f"[🔧 **Apply All {len(auto_fixable)} Fixes**](command:workbench.action.chat.applyInEditor) "
            response += f"[📄 **Show Fixed Code**](command:workbench.action.chat.insertIntoNewFile) "
            response += f"[🔍 **Re-analyze**](command:workbench.action.chat.submit)\n\n"

            # Show what will be fixed
            response += "**Will be fixed automatically:**\n"
            for fix in auto_fixable[:3]:
                response += f"   ✅ Line {fix.line_number}: {fix.description}\n"
            if len(auto_fixable) > 3:
                response += f"   ✅ ... and {len(auto_fixable) - 3} more fixes\n"
            response += "\n"

        response += "💡 **Next Steps**:\n"
        if auto_fixable and content.strip():
            response += "   • **Click the 'Apply All Fixes' button above** for instant corrections\n"
            response += "   • Or type: 'fix this code' to apply all automatic fixes\n"
        else:
            response += "   • Review the flagged issues for manual improvements\n"
        response += "   • Apply framework-specific best practices\n"
        response += f"   • Consider {file_type} optimization opportunities\n"

        return response

    async def _handle_fix_request(self, message: str, file_path: str, content: str) -> str:
        """Handle code fix requests."""
        
        if not content:
            return """🔧 **Code Fix Request**
            
I can help fix your code! Please:
1. Select the code you want me to fix
2. Or open a file and ask me to "fix this file"

I can automatically fix:
- 🚫 Console statements in test files
- 📝 Basic formatting issues
- 📦 Import organization
- 🔤 Simple type annotations"""
        
        try:
            # First analyze to get issues
            issues = self.file_analyzer.analyze_file(file_path, content)
            
            # Apply fixes
            fix_result = self.fix_manager.one_click_fix(content, file_path, issues)
            
            if fix_result['content_changed']:
                applied_count = len(fix_result['applied_fixes'])
                manual_count = len(fix_result['manual_suggestions'])
                
                response = f"""🔧 **Auto-Fix Results**

**File**: `{file_path}`
**Changes Applied**: {applied_count} automatic fixes

✅ **Fixed Automatically**:
"""
                for fix in fix_result['applied_fixes']:
                    response += f"   • {fix.get('description', 'Applied fix')}\n"

                if manual_count > 0:
                    response += f"\n👨‍💻 **Manual Attention Required** ({manual_count} items):\n"
                    for suggestion in fix_result['manual_suggestions'][:3]:
                        response += f"   • {suggestion.get('title', 'Manual improvement needed')}\n"

                response += f"\n📊 **Summary**: Code quality improved! {applied_count} issues resolved automatically.\n\n"

                # Add buttons for the fixed code
                if 'fixed_content' in fix_result and fix_result['fixed_content'].strip():
                    response += "**🔘 Apply Fixed Code:**\n"
                    response += "[📝 **Replace Current Code**](command:workbench.action.chat.applyInEditor) "
                    response += "[📄 **Insert in New File**](command:workbench.action.chat.insertIntoNewFile) "
                    response += "[🔍 **Analyze Fixed Code**](command:workbench.action.chat.submit)\n\n"

                    response += "📄 **Fixed Code**:\n```typescript\n" + fix_result['fixed_content'][:500]
                    if len(fix_result['fixed_content']) > 500:
                        response += "\n... (truncated)\n```"
                    else:
                        response += "\n```"
                
                return response
            else:
                return """✅ **Code Review Complete**
                
Your code is already in great shape! No automatic fixes were needed.

💡 **Suggestions**:
- Your code follows good practices
- Consider reviewing for performance optimizations
- Ensure comprehensive test coverage"""
                
        except Exception as e:
            logger.error(f"Fix request failed: {e}")
            return f"""❌ **Fix Request Error**
            
I encountered an issue while trying to fix your code: {str(e)}

💡 **Alternative approaches**:
- Try analyzing the code first to identify specific issues
- Ask for specific fixes (e.g., "remove console statements")
- Request manual guidance for complex improvements"""
    
    async def _handle_standards_request(self, message: str, file_path: str) -> str:
        """Handle coding standards requests."""
        
        # Determine relevant standards based on file type or message
        file_type = self._get_file_type(file_path)
        
        if 'typescript' in message.lower() or file_type == 'typescript':
            category = 'typescript'
        elif 'playwright' in message.lower() or file_type == 'playwright':
            category = 'playwright'
        elif 'cucumber' in message.lower() or file_type == 'cucumber':
            category = 'cucumber'
        else:
            category = None
        
        try:
            if category:
                standards_list = self.standards.get_standards_by_category(category)
                category_name = category.title()
            else:
                standards_list = self.standards.get_all_standards()
                category_name = "All"
            
            if not standards_list:
                return f"""📋 **{category_name} Coding Standards**

I have comprehensive coding standards for:
- 📘 **TypeScript**: Type safety, modern syntax, best practices
- 🧪 **Playwright**: Test structure, locators, wait strategies
- 📋 **Cucumber**: Gherkin syntax, scenario structure, BDD patterns

{self._get_framework_tips(category or 'general')}

💡 **Ask me**: "show me [framework] standards" for specific guidelines!"""
            
            # Group standards by severity
            errors = [s for s in standards_list if s.severity == 'error']
            warnings = [s for s in standards_list if s.severity == 'warning']
            auto_fixable = [s for s in standards_list if s.auto_fixable]
            
            response = f"""📋 **{category_name} Coding Standards**

**Total Rules**: {len(standards_list)}
**Auto-Fixable**: {len(auto_fixable)} rules

"""
            
            if errors:
                response += f"🔴 **Critical Rules** ({len(errors)}):\n"
                for rule in errors[:3]:
                    response += f"   • **{rule.rule_id}**: {rule.description}\n"
                if len(errors) > 3:
                    response += f"   ... and {len(errors) - 3} more critical rules\n"
                response += "\n"
            
            if warnings:
                response += f"🟡 **Best Practice Rules** ({len(warnings)}):\n"
                for rule in warnings[:3]:
                    response += f"   • **{rule.rule_id}**: {rule.description}\n"
                if len(warnings) > 3:
                    response += f"   ... and {len(warnings) - 3} more best practices\n"
                response += "\n"
            
            response += f"🔧 **{len(auto_fixable)} rules can be automatically enforced**\n\n"
            response += self._get_framework_tips(category or 'general')
            
            return response
            
        except Exception as e:
            logger.error(f"Standards request failed: {e}")
            return self._get_fallback_standards(category)
    
    def _get_framework_tips(self, framework: str) -> str:
        """Get framework-specific tips."""
        
        tips = {
            'typescript': """💡 **TypeScript Tips**:
   • Use explicit type annotations for function returns
   • Prefer `const` over `let` when possible
   • Avoid `any` type, use specific types or `unknown`
   • Use optional chaining (`?.`) for safer property access""",
            
            'playwright': """💡 **Playwright Tips**:
   • Use semantic locators: `page.getByRole()`, `page.getByText()`
   • Avoid `waitForTimeout()`, use explicit waits
   • Remove console statements from test files
   • Structure tests with clear Given-When-Then flow""",
            
            'cucumber': """💡 **Cucumber Tips**:
   • Write scenarios in business language, not technical terms
   • Keep steps simple and reusable
   • Use Background for common setup
   • Organize features by business capability""",
            
            'general': """💡 **General Tips**:
   • Write self-documenting code with clear names
   • Keep functions small and focused
   • Handle errors gracefully
   • Write tests for critical functionality"""
        }
        
        return tips.get(framework, tips['general'])
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from path."""
        if file_path.endswith(('.spec.ts', '.test.ts')):
            return 'playwright'
        elif file_path.endswith('.feature'):
            return 'cucumber'
        elif file_path.endswith(('.ts', '.tsx')):
            return 'typescript'
        elif file_path.endswith(('.js', '.jsx')):
            return 'javascript'
        else:
            return 'general'
    
    async def _handle_explanation_request(self, message: str, file_path: str, content: str) -> str:
        """Handle explanation requests."""
        return """💡 **Code Explanation**

I'd be happy to explain code concepts, errors, or best practices!

**What I can explain**:
- 🐛 Error messages and how to fix them
- 📚 TypeScript concepts and syntax
- 🧪 Playwright testing patterns
- 📋 Cucumber BDD principles
- 🏗️ Code architecture decisions

**Try asking**:
- "Why is this error happening?"
- "Explain this TypeScript syntax"
- "How does this Playwright test work?"
- "What's the best way to structure this?"

Feel free to share specific code or error messages you'd like me to explain!"""
    
    async def _handle_general_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle general requests."""
        return """🤖 **TypeScript Playwright Cucumber Code Reviewer**

I'm here to help with your development workflow!

**What I can do**:
🔍 **Analyze**: Review your code for issues and improvements
🔧 **Fix**: Automatically correct common problems
📋 **Standards**: Share coding best practices and guidelines
💡 **Explain**: Help you understand code concepts and errors

**Supported Technologies**:
- 📘 TypeScript/JavaScript
- 🧪 Playwright Testing
- 📋 Cucumber BDD
- ⚙️ Configuration files

**Try saying**:
- "Analyze this TypeScript component"
- "Fix issues in this test file"
- "Show me Playwright best practices"
- "Explain this error message"

How can I help you today?"""
    
    def _get_help_response(self, context: Dict[str, Any]) -> str:
        """Generate help response based on context."""
        file_path = context.get('file_path', '')
        file_type = self._get_file_type(file_path)
        
        base_help = """🤖 **Code Review Agent Help**

**Core Capabilities**:
🔍 **Code Analysis**: "analyze this code", "check for issues"
🔧 **Auto-Fix**: "fix this code", "clean up this file"
📋 **Standards**: "show me best practices", "typescript guidelines"
💡 **Guidance**: "how should I structure this?", "explain this error"

"""
        
        if file_type != 'general':
            base_help += f"**{file_type.title()}-Specific Help**:\n"
            base_help += self._get_framework_tips(file_type) + "\n\n"
        
        base_help += """**Quick Commands**:
- "help" - Show this help
- "analyze" - Review current code
- "fix" - Apply automatic fixes
- "standards" - Show coding guidelines

**Integration**: I'm running as an ADK server and integrated with VS Code Copilot Chat for seamless development workflow assistance."""
        
        return base_help
    
    def _generate_contextual_suggestions(self, intent: str, file_path: str) -> List[str]:
        """Generate contextual suggestions based on intent and file type."""
        
        file_type = self._get_file_type(file_path)
        
        base_suggestions = [
            "Analyze this code for quality issues",
            "Apply automated fixes to this file",
            "Show me coding standards",
            "Help me understand this error"
        ]
        
        if file_type == 'playwright':
            base_suggestions.extend([
                "Check for Playwright best practices",
                "Remove console statements from tests",
                "Review test structure and naming",
                "Validate locator usage"
            ])
        elif file_type == 'typescript':
            base_suggestions.extend([
                "Check TypeScript type safety",
                "Review import/export patterns",
                "Validate function signatures",
                "Check for modern TS features"
            ])
        elif file_type == 'cucumber':
            base_suggestions.extend([
                "Review Gherkin syntax",
                "Check scenario structure",
                "Validate Given-When-Then flow",
                "Review step definitions"
            ])
        
        return base_suggestions
    
    def _get_follow_up_actions(self, intent: str, file_path: str) -> List[str]:
        """Get follow-up actions based on intent."""
        
        actions = []
        
        if intent == 'analyze':
            actions = [
                "Apply auto-fixes for detected issues",
                "Get detailed explanation of specific problems",
                "Review coding standards for this file type",
                "Ask for improvement suggestions"
            ]
        elif intent == 'fix':
            actions = [
                "Analyze the fixed code for remaining issues",
                "Review the changes that were applied",
                "Get guidance on manual improvements",
                "Check if code follows best practices"
            ]
        elif intent == 'standards':
            actions = [
                "Analyze current code against these standards",
                "Get specific examples of rule applications",
                "Learn about auto-fixable rules",
                "Ask about framework-specific patterns"
            ]
        
        return actions
    
    def _get_fallback_standards(self, category: Optional[str]) -> str:
        """Get fallback standards when database query fails."""
        
        if category == 'typescript':
            return """📋 **TypeScript Coding Standards**

🔴 **Critical Rules**:
• **ts-no-any**: Avoid using 'any' type
• **ts-explicit-return-types**: Functions should have explicit return types
• **ts-no-unused-vars**: Remove unused variables

🟡 **Best Practices**:
• **ts-prefer-const**: Use const for variables that are never reassigned
• **ts-naming-convention**: Follow consistent naming conventions
• **ts-strict-mode**: Enable strict TypeScript compiler options

💡 **TypeScript Tips**:
- Use type annotations for better code documentation
- Leverage TypeScript's type system for safer code
- Prefer interfaces over type aliases for object shapes"""
        
        elif category == 'playwright':
            return """📋 **Playwright Testing Standards**

🔴 **Critical Rules**:
• **pw-no-console-in-tests**: Remove console statements from tests
• **pw-no-hard-waits**: Avoid page.waitForTimeout()
• **pw-use-semantic-locators**: Use getByRole, getByText instead of CSS

🟡 **Best Practices**:
• **pw-test-naming**: Use descriptive test names
• **pw-page-object-model**: Organize tests with Page Object Model
• **pw-proper-assertions**: Use Playwright's expect assertions

💡 **Playwright Tips**:
- Structure tests with clear Given-When-Then flow
- Use stable, semantic locators
- Implement proper wait strategies"""
        
        else:
            return """📋 **General Coding Standards**

🔴 **Critical Rules**:
• Write clean, readable code
• Handle errors appropriately
• Follow consistent naming conventions

🟡 **Best Practices**:
• Keep functions small and focused
• Write meaningful comments
• Use version control effectively

💡 **General Tips**:
- Prioritize code readability
- Write tests for critical functionality
- Follow established team conventions"""
