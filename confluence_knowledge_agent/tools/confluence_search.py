"""
Confluence Search Tool

ADK function tool for searching Confluence knowledge base.
"""

import logging
from typing import Optional
from .knowledge_base import ConfluenceKnowledgeBase
from ..config.settings import get_data_config

logger = logging.getLogger(__name__)

# Global knowledge base instance
_knowledge_base: Optional[ConfluenceKnowledgeBase] = None


def get_knowledge_base() -> ConfluenceKnowledgeBase:
    """
    Get or create the global knowledge base instance.
    
    Returns:
        ConfluenceKnowledgeBase: The knowledge base instance
    """
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = ConfluenceKnowledgeBase()
    return _knowledge_base


def search_confluence_knowledge(query: str, limit: int = 5) -> str:
    """
    Search the Confluence knowledge base for relevant information.
    
    This function tool searches through Confluence documentation to find
    relevant pages and content based on the user's query.
    
    Args:
        query (str): The search query to find relevant documentation
        limit (int): Maximum number of results to return (default: 5, max: 10)
        
    Returns:
        str: Formatted search results with citations and content previews
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            return "Please provide a search query to find relevant information."
        
        # Limit the number of results
        limit = min(max(1, limit), 10)
        
        # Get knowledge base and perform search
        kb = get_knowledge_base()
        results = kb.search(query.strip(), limit)
        
        if not results:
            return f"""No relevant information found in the Confluence knowledge base for: "{query}"

Suggestions:
- Try using different keywords
- Check spelling and try broader terms
- Ask about general topics that might be covered in the documentation"""
        
        # Format results
        config = get_data_config()
        preview_length = config["content_preview_length"]
        
        response = f"Found {len(results)} relevant document(s) for: \"{query}\"\n\n"
        
        for i, doc in enumerate(results, 1):
            # Create content preview
            content_preview = doc.content[:preview_length]
            if len(doc.content) > preview_length:
                content_preview += "..."
            
            # Format document entry
            response += f"**{i}. {doc.title}**\n"
            response += f"Space: {doc.space_key}"
            if doc.space_name:
                response += f" ({doc.space_name})"
            response += "\n"
            
            if content_preview:
                response += f"Content: {content_preview}\n"
            
            response += f"Source: [{doc.title}]({doc.url})"
            if doc.last_updated:
                response += f" - Last updated: {doc.last_updated}"
            response += "\n"
            
            if doc.author:
                response += f"Author: {doc.author}\n"
            
            if doc.labels:
                response += f"Labels: {', '.join(doc.labels)}\n"
            
            response += "\n"
        
        # Add helpful footer
        response += "💡 **Tip**: Click on the source links above to view the complete documentation."
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching Confluence knowledge base: {e}")
        return f"""An error occurred while searching the knowledge base: {str(e)}

Please try again or contact support if the issue persists."""


def get_knowledge_base_stats() -> str:
    """
    Get statistics about the knowledge base.
    
    Returns:
        str: Formatted statistics about the knowledge base
    """
    try:
        kb = get_knowledge_base()
        stats = kb.get_stats()
        
        response = "📊 **Confluence Knowledge Base Statistics**\n\n"
        response += f"• Total Documents: {stats['total_documents']}\n"
        response += f"• Total Spaces: {stats['total_spaces']}\n"
        response += f"• Average Content Length: {stats['average_content_length']:.0f} characters\n"
        
        if stats['spaces']:
            response += f"\n**Available Spaces:**\n"
            for space in sorted(stats['spaces']):
                space_docs = kb.get_documents_by_space(space)
                response += f"• {space}: {len(space_docs)} documents\n"
        
        response += f"\n**Data Location:** {stats['data_directory']}"
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {e}")
        return f"Error retrieving knowledge base statistics: {str(e)}"
