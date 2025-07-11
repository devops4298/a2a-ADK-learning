"""
Tests for Confluence Knowledge Base functionality.
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from ..tools.knowledge_base import ConfluenceKnowledgeBase, ConfluenceDocument
from ..data.validator import validate_data_structure


class TestConfluenceKnowledgeBase:
    """Test cases for ConfluenceKnowledgeBase."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        # Create test data structure
        self._create_test_data()
    
    def _create_test_data(self):
        """Create test data structure."""
        # Create index file
        index_data = [
            {
                "id": "123456",
                "space_key": "TEST",
                "title": "Test Page 1"
            },
            {
                "id": "789012",
                "space_key": "TEST",
                "title": "Test Page 2"
            }
        ]
        
        index_file = self.data_dir / "index.json"
        with open(index_file, 'w') as f:
            json.dump(index_data, f)
        
        # Create space directory
        space_dir = self.data_dir / "TEST"
        space_dir.mkdir()
        
        # Create test documents
        doc1_data = {
            "content": "This is test content about Python programming and API development.",
            "metadata": {
                "title": "Test Page 1",
                "url": "https://example.atlassian.net/wiki/spaces/TEST/pages/123456",
                "last_updated": "2024-01-15",
                "space_key": "TEST",
                "author": "Test Author"
            }
        }
        
        doc2_data = {
            "content": "This is another test document about machine learning and AI.",
            "metadata": {
                "title": "Test Page 2", 
                "url": "https://example.atlassian.net/wiki/spaces/TEST/pages/789012",
                "last_updated": "2024-01-16",
                "space_key": "TEST"
            }
        }
        
        with open(space_dir / "123456.json", 'w') as f:
            json.dump(doc1_data, f)
        
        with open(space_dir / "789012.json", 'w') as f:
            json.dump(doc2_data, f)
    
    def test_initialization(self):
        """Test knowledge base initialization."""
        kb = ConfluenceKnowledgeBase(str(self.data_dir))
        
        assert len(kb.documents) == 2
        assert kb.data_dir == self.data_dir
    
    def test_search_functionality(self):
        """Test search functionality."""
        kb = ConfluenceKnowledgeBase(str(self.data_dir))
        
        # Test search with results
        results = kb.search("Python programming")
        assert len(results) == 1
        assert results[0].title == "Test Page 1"
        
        # Test search with no results
        results = kb.search("nonexistent topic")
        assert len(results) == 0
        
        # Test empty query
        results = kb.search("")
        assert len(results) == 0
    
    def test_get_document_by_id(self):
        """Test getting document by ID."""
        kb = ConfluenceKnowledgeBase(str(self.data_dir))
        
        doc = kb.get_document_by_id("123456")
        assert doc is not None
        assert doc.title == "Test Page 1"
        
        doc = kb.get_document_by_id("nonexistent")
        assert doc is None
    
    def test_get_documents_by_space(self):
        """Test getting documents by space."""
        kb = ConfluenceKnowledgeBase(str(self.data_dir))
        
        docs = kb.get_documents_by_space("TEST")
        assert len(docs) == 2
        
        docs = kb.get_documents_by_space("NONEXISTENT")
        assert len(docs) == 0
    
    def test_get_stats(self):
        """Test getting knowledge base statistics."""
        kb = ConfluenceKnowledgeBase(str(self.data_dir))
        
        stats = kb.get_stats()
        assert stats["total_documents"] == 2
        assert stats["total_spaces"] == 1
        assert "TEST" in stats["spaces"]
        assert stats["total_content_length"] > 0
    
    def test_empty_knowledge_base(self):
        """Test behavior with empty knowledge base."""
        empty_dir = tempfile.mkdtemp()
        kb = ConfluenceKnowledgeBase(empty_dir)
        
        assert len(kb.documents) == 0
        
        results = kb.search("anything")
        assert len(results) == 0
        
        stats = kb.get_stats()
        assert stats["total_documents"] == 0


class TestDataValidation:
    """Test cases for data validation."""
    
    def test_validate_valid_structure(self):
        """Test validation of valid data structure."""
        temp_dir = tempfile.mkdtemp()
        data_dir = Path(temp_dir)
        
        # Create valid structure
        index_data = [{"id": "123", "space_key": "TEST"}]
        with open(data_dir / "index.json", 'w') as f:
            json.dump(index_data, f)
        
        space_dir = data_dir / "TEST"
        space_dir.mkdir()
        
        doc_data = {
            "content": "Test content",
            "metadata": {"title": "Test", "url": "http://example.com"}
        }
        with open(space_dir / "123.json", 'w') as f:
            json.dump(doc_data, f)
        
        is_valid, issues = validate_data_structure(str(data_dir))
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_missing_directory(self):
        """Test validation of missing directory."""
        is_valid, issues = validate_data_structure("/nonexistent/path")
        assert not is_valid
        assert len(issues) > 0
        assert "does not exist" in issues[0]
    
    def test_validate_missing_index(self):
        """Test validation of missing index file."""
        temp_dir = tempfile.mkdtemp()
        is_valid, issues = validate_data_structure(temp_dir)
        assert not is_valid
        assert any("Index file not found" in issue for issue in issues)
