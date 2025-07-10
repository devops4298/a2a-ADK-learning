#!/usr/bin/env python3
"""
A2A-compatible FastAPI Server for TypeScript Playwright Cucumber Code Review Agent.
This allows VS Code Copilot Chat to discover and interact with our agent.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("FastAPI not available. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "fastapi", "uvicorn"])
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn

from pydantic import BaseModel

from .analyzers.file_analyzer import FileAnalyzer
from .fixers.fix_manager import FixManager
from .standards.project_standards import ProjectStandards
from .chat.enhanced_chat_handler import EnhancedChatHandler


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeAnalysisRequest(BaseModel):
    """Request model for code analysis."""
    content: str
    file_path: str
    file_type: Optional[str] = None


class CodeFixRequest(BaseModel):
    """Request model for code fixing."""
    content: str
    file_path: str


class CodeReviewAgent:
    """Code Review Agent for VS Code Copilot Chat integration."""

    def __init__(self):
        # Initialize our components
        self.file_analyzer = FileAnalyzer()
        self.fix_manager = FixManager()
        self.standards = ProjectStandards()
        self.enhanced_chat = EnhancedChatHandler()

        # Agent metadata
        self.agent_id = "ts-playwright-cucumber-reviewer"
        self.name = "TypeScript Playwright Cucumber Code Reviewer"
        self.description = "AI-powered code review assistant for TypeScript, Playwright, and Cucumber projects"
        self.version = "1.0.0"
    
    async def analyze_code(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code content for quality issues.
        
        Args:
            request: Dictionary containing 'content', 'file_path', and optional 'file_type'
            
        Returns:
            Analysis results with issues, summary, and recommendations
        """
        try:
            # Validate request
            analysis_request = CodeAnalysisRequest(**request)
            
            # Analyze the code
            issues = self.file_analyzer.analyze_file(
                analysis_request.file_path, 
                analysis_request.content
            )
            
            # Get summary
            summary = self.file_analyzer.get_analysis_summary()
            
            # Convert issues to serializable format
            issues_data = [issue.to_dict() for issue in issues]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues)
            
            return {
                "success": True,
                "file_path": analysis_request.file_path,
                "total_issues": len(issues),
                "issues": issues_data,
                "summary": summary,
                "recommendations": recommendations,
                "auto_fixable_count": len([i for i in issues if i.auto_fixable])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def fix_code(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply one-click fix to code content.
        
        Args:
            request: Dictionary containing 'content' and 'file_path'
            
        Returns:
            Fix results with original/fixed content and applied changes
        """
        try:
            # Validate request
            fix_request = CodeFixRequest(**request)
            
            # First analyze to get issues
            issues = self.file_analyzer.analyze_file(
                fix_request.file_path,
                fix_request.content
            )
            
            # Apply fixes
            fix_result = self.fix_manager.one_click_fix(
                fix_request.content,
                fix_request.file_path,
                issues
            )
            
            return {
                "success": True,
                "original_content": fix_request.content,
                "fixed_content": fix_result['fixed_content'],
                "content_changed": fix_result['content_changed'],
                "applied_fixes": fix_result['applied_fixes'],
                "manual_suggestions": fix_result['manual_suggestions'],
                "fix_statistics": fix_result['fix_statistics'],
                "next_steps": fix_result['next_steps']
            }
            
        except Exception as e:
            logger.error(f"Error fixing code: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_standards(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get coding standards information.
        
        Args:
            request: Dictionary with optional 'category' and 'auto_fixable' filters
            
        Returns:
            Standards information with rules and categories
        """
        try:
            category = request.get('category')
            auto_fixable = request.get('auto_fixable')
            
            if category:
                standards_list = self.standards.get_standards_by_category(category)
            else:
                standards_list = self.standards.get_all_standards()
            
            if auto_fixable is not None:
                standards_list = [s for s in standards_list if s.auto_fixable == auto_fixable]
            
            standards_data = [
                {
                    'rule_id': std.rule_id,
                    'description': std.description,
                    'severity': std.severity,
                    'category': std.category,
                    'auto_fixable': std.auto_fixable,
                    'examples': std.examples
                }
                for std in standards_list
            ]
            
            return {
                "success": True,
                "standards": standards_data,
                "total_count": len(standards_data),
                "categories": list(self.standards.get_rule_categories())
            }
            
        except Exception as e:
            logger.error(f"Error getting standards: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat_interface(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced chat interface using ADK-powered chat handler.

        Args:
            request: Dictionary containing 'message' and optional 'context'

        Returns:
            Enhanced chat response with comprehensive analysis
        """
        try:
            message = request.get('message', '')
            context = request.get('context', {})

            # Use enhanced chat handler for better responses
            result = await self.enhanced_chat.handle_chat_message(message, context)

            return result

        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request. Please try again or rephrase your question."
            }
    
    async def _process_chat_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a chat message and return a response."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['analyze', 'review', 'check', 'issues']):
            return await self._handle_analyze_chat(context)
        elif any(word in message_lower for word in ['fix', 'repair', 'correct']):
            return await self._handle_fix_chat(context)
        elif any(word in message_lower for word in ['standards', 'rules', 'guidelines']):
            return await self._handle_standards_chat(context)
        elif any(word in message_lower for word in ['help', 'what', 'how']):
            return self._get_help_message()
        else:
            return "I can help you analyze code, apply fixes, or explain coding standards. What would you like me to do?"
    
    async def _handle_analyze_chat(self, context: Dict[str, Any]) -> str:
        """Handle code analysis chat request."""
        content = context.get('content')
        file_path = context.get('file_path', 'unknown.ts')
        
        if not content:
            return "Please provide code content to analyze. You can select code in your editor and ask me to review it."
        
        # Analyze the code
        result = await self.analyze_code({'content': content, 'file_path': file_path})
        
        if not result['success']:
            return f"Sorry, I encountered an error analyzing your code: {result.get('error', 'Unknown error')}"
        
        if result['total_issues'] == 0:
            return "✅ Excellent! Your code looks great with no quality issues found."
        
        # Format response
        total = result['total_issues']
        auto_fixable = result['auto_fixable_count']
        
        response = f"🔍 Found {total} code quality issues:\n\n"
        
        # Show top issues by severity
        issues = result['issues']
        errors = [i for i in issues if i['severity'] == 'error']
        warnings = [i for i in issues if i['severity'] == 'warning']
        
        if errors:
            response += f"🔴 {len(errors)} critical errors:\n"
            for error in errors[:3]:
                response += f"  • Line {error['line_number']}: {error['description']}\n"
        
        if warnings:
            response += f"🟡 {len(warnings)} warnings:\n"
            for warning in warnings[:3]:
                response += f"  • Line {warning['line_number']}: {warning['description']}\n"
        
        if auto_fixable > 0:
            response += f"\n💡 Good news! I can automatically fix {auto_fixable} of these issues. Would you like me to apply the fixes?"
        
        return response
    
    async def _handle_fix_chat(self, context: Dict[str, Any]) -> str:
        """Handle code fix chat request."""
        content = context.get('content')
        file_path = context.get('file_path', 'unknown.ts')
        
        if not content:
            return "Please provide code content to fix. Select the code you'd like me to improve."
        
        # Apply fixes
        result = await self.fix_code({'content': content, 'file_path': file_path})
        
        if not result['success']:
            return f"Sorry, I encountered an error fixing your code: {result.get('error', 'Unknown error')}"
        
        if not result['content_changed']:
            return "✅ Your code is already in great shape! No automated fixes were needed."
        
        applied_count = len(result['applied_fixes'])
        manual_count = len(result['manual_suggestions'])
        
        response = f"🔧 Applied {applied_count} automated fixes to your code!\n\n"
        
        # Show what was fixed
        for fix in result['applied_fixes'][:3]:
            response += f"  ✅ {fix.get('description', 'Applied fix')}\n"
        
        if manual_count > 0:
            response += f"\n💡 {manual_count} additional improvements require manual attention:\n"
            for suggestion in result['manual_suggestions'][:2]:
                response += f"  • {suggestion.get('title', 'Manual improvement needed')}\n"
        
        response += "\nThe fixed code is ready to use!"
        return response
    
    async def _handle_standards_chat(self, context: Dict[str, Any]) -> str:
        """Handle coding standards chat request."""
        file_path = context.get('file_path', '')
        
        # Determine relevant standards based on file type
        if '.spec.ts' in file_path or '.test.ts' in file_path:
            category = 'playwright'
            category_name = 'Playwright Testing'
        elif file_path.endswith('.feature'):
            category = 'cucumber'
            category_name = 'Cucumber BDD'
        elif file_path.endswith(('.ts', '.js')):
            category = 'typescript'
            category_name = 'TypeScript'
        else:
            category = None
            category_name = 'All'
        
        # Get standards
        request_data = {'category': category} if category else {}
        result = await self.get_standards(request_data)
        
        if not result['success']:
            return f"Sorry, I encountered an error getting standards: {result.get('error', 'Unknown error')}"
        
        standards = result['standards']
        response = f"📋 {category_name} Coding Standards ({len(standards)} rules):\n\n"
        
        # Group by severity
        errors = [s for s in standards if s['severity'] == 'error']
        warnings = [s for s in standards if s['severity'] == 'warning']
        
        if errors:
            response += f"🔴 Critical Rules ({len(errors)}):\n"
            for rule in errors[:3]:
                response += f"  • {rule['rule_id']}: {rule['description']}\n"
        
        if warnings:
            response += f"\n🟡 Best Practice Rules ({len(warnings)}):\n"
            for rule in warnings[:3]:
                response += f"  • {rule['rule_id']}: {rule['description']}\n"
        
        auto_fixable = len([s for s in standards if s['auto_fixable']])
        response += f"\n🔧 {auto_fixable} rules can be automatically fixed"
        
        return response
    
    def _get_help_message(self) -> str:
        """Get help message for the chat interface."""
        return """🤖 TypeScript Playwright Cucumber Code Reviewer

I can help you with:

🔍 **Code Analysis**: "Analyze this code" or "Check for issues"
🔧 **Auto-Fix**: "Fix this code" or "Apply automated fixes"  
📋 **Standards**: "Show coding standards" or "What are the rules?"

**How to use:**
1. Select code in your editor
2. Ask me to analyze, fix, or explain standards
3. I'll provide specific feedback and suggestions

**Supported files:**
• TypeScript (.ts, .js)
• Playwright tests (.spec.ts, .test.ts)
• Cucumber features (.feature)

Try asking: "Analyze this TypeScript code" or "What Playwright standards should I follow?"
"""
    
    def _generate_recommendations(self, issues: List) -> List[str]:
        """Generate recommendations based on found issues."""
        if not issues:
            return ["✨ Great job! Your code follows all quality standards."]
        
        recommendations = []
        
        error_count = len([i for i in issues if i.severity == 'error'])
        warning_count = len([i for i in issues if i.severity == 'warning'])
        auto_fixable = len([i for i in issues if i.auto_fixable])
        
        if error_count > 0:
            recommendations.append(f"🔴 Fix {error_count} critical error(s) first")
        
        if auto_fixable > 0:
            recommendations.append(f"🔧 Use auto-fix to resolve {auto_fixable} issue(s) instantly")
        
        if warning_count > 5:
            recommendations.append("⚠️ Consider addressing warnings to improve code quality")
        
        recommendations.append("🧪 Run tests after making changes")
        
        return recommendations
    
    def _generate_chat_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Generate helpful chat suggestions based on context."""
        suggestions = [
            "Analyze this code for quality issues",
            "Apply automated fixes to this code",
            "Show me the coding standards",
            "Help me understand this error"
        ]
        
        file_path = context.get('file_path', '')
        
        if '.spec.ts' in file_path or '.test.ts' in file_path:
            suggestions.extend([
                "Check Playwright best practices",
                "Review test structure and naming",
                "Validate locator usage"
            ])
        elif file_path.endswith('.feature'):
            suggestions.extend([
                "Review Gherkin syntax",
                "Check scenario structure",
                "Validate Given-When-Then flow"
            ])
        
        return suggestions


def create_fastapi_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Create the code review agent
    agent = CodeReviewAgent()

    # Create FastAPI app
    app = FastAPI(
        title=agent.name,
        description=agent.description,
        version=agent.version
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "agent_id": agent.agent_id,
            "name": agent.name,
            "version": agent.version
        }

    # Agent info endpoint for VS Code discovery
    @app.get("/agent")
    async def get_agent_info():
        return {
            "id": agent.agent_id,
            "name": agent.name,
            "description": agent.description,
            "version": agent.version,
            "capabilities": ["analyze_code", "fix_code", "get_standards", "chat"]
        }

    # Analyze code endpoint
    @app.post("/analyze")
    async def analyze_code_endpoint(request: CodeAnalysisRequest):
        try:
            result = await agent.analyze_code(request.model_dump())
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))
            return result
        except Exception as e:
            logger.error(f"Error in analyze endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Fix code endpoint
    @app.post("/fix")
    async def fix_code_endpoint(request: CodeFixRequest):
        try:
            result = await agent.fix_code(request.model_dump())
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Fix failed"))
            return result
        except Exception as e:
            logger.error(f"Error in fix endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Get standards endpoint
    @app.get("/standards")
    async def get_standards_endpoint(category: Optional[str] = None, auto_fixable: Optional[bool] = None):
        try:
            request_data = {}
            if category:
                request_data["category"] = category
            if auto_fixable is not None:
                request_data["auto_fixable"] = auto_fixable

            result = await agent.get_standards(request_data)
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Standards retrieval failed"))
            return result
        except Exception as e:
            logger.error(f"Error in standards endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Chat endpoint for VS Code Copilot Chat
    @app.post("/chat")
    async def chat_endpoint(request: dict):
        try:
            result = await agent.chat_interface(request)
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Chat failed"))
            return result
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    logger.info(f"Created FastAPI app for {agent.name}")
    return app


async def main():
    """Main entry point for the FastAPI server."""
    import argparse

    parser = argparse.ArgumentParser(description="TypeScript Playwright Cucumber Code Review Agent Server")
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create the FastAPI app
    app = create_fastapi_app()

    logger.info(f"Starting TypeScript Playwright Cucumber Code Review Agent Server...")
    logger.info(f"Server will be available at http://{args.host}:{args.port}")
    logger.info("VS Code Copilot Chat can discover and use this agent!")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  /agent - Agent information")
    logger.info("  POST /analyze - Analyze code")
    logger.info("  POST /fix - Fix code")
    logger.info("  GET  /standards - Get coding standards")
    logger.info("  POST /chat - Chat interface")

    try:
        # Start the server
        config = uvicorn.Config(app, host=args.host, port=args.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")


if __name__ == "__main__":
    asyncio.run(main())
