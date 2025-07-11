"""
Data validation utilities for Confluence Knowledge Agent.

Validates data structure and integrity following ADK best practices.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


def validate_data_structure(data_dir: str) -> Tuple[bool, List[str]]:
    """
    Validate the Confluence data directory structure.
    
    Args:
        data_dir: Path to the data directory
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    data_path = Path(data_dir)
    
    # Check if data directory exists
    if not data_path.exists():
        issues.append(f"Data directory does not exist: {data_dir}")
        return False, issues
    
    # Check for index file
    index_file = data_path / "index.json"
    if not index_file.exists():
        issues.append(f"Index file not found: {index_file}")
        return False, issues
    
    # Validate index file
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        if not isinstance(index_data, list):
            issues.append("Index file must contain a JSON array")
            return False, issues
        
        # Validate each entry in index
        for i, entry in enumerate(index_data):
            entry_issues = _validate_index_entry(entry, i)
            issues.extend(entry_issues)
            
            # Check if corresponding data file exists
            if "space_key" in entry and "id" in entry:
                data_file = data_path / entry["space_key"] / f"{entry['id']}.json"
                if not data_file.exists():
                    issues.append(f"Data file not found: {data_file}")
                else:
                    # Validate data file structure
                    file_issues = _validate_data_file(data_file)
                    issues.extend(file_issues)
    
    except json.JSONDecodeError as e:
        issues.append(f"Invalid JSON in index file: {e}")
        return False, issues
    except Exception as e:
        issues.append(f"Error reading index file: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def _validate_index_entry(entry: Dict[str, Any], index: int) -> List[str]:
    """
    Validate a single index entry.
    
    Args:
        entry: Index entry to validate
        index: Entry index for error reporting
        
    Returns:
        List of validation issues
    """
    issues = []
    required_fields = ["id", "space_key"]
    
    for field in required_fields:
        if field not in entry:
            issues.append(f"Index entry {index}: missing required field '{field}'")
        elif not isinstance(entry[field], str) or not entry[field].strip():
            issues.append(f"Index entry {index}: field '{field}' must be a non-empty string")
    
    # Optional fields validation
    if "title" in entry and not isinstance(entry["title"], str):
        issues.append(f"Index entry {index}: 'title' must be a string")
    
    return issues


def _validate_data_file(file_path: Path) -> List[str]:
    """
    Validate a data file structure.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        List of validation issues
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required top-level fields
        if "content" not in data:
            issues.append(f"{file_path}: missing 'content' field")
        elif not isinstance(data["content"], str):
            issues.append(f"{file_path}: 'content' must be a string")
        
        if "metadata" not in data:
            issues.append(f"{file_path}: missing 'metadata' field")
        elif not isinstance(data["metadata"], dict):
            issues.append(f"{file_path}: 'metadata' must be an object")
        else:
            # Validate metadata structure
            metadata = data["metadata"]
            required_metadata = ["title", "url"]
            
            for field in required_metadata:
                if field not in metadata:
                    issues.append(f"{file_path}: metadata missing required field '{field}'")
                elif not isinstance(metadata[field], str):
                    issues.append(f"{file_path}: metadata field '{field}' must be a string")
    
    except json.JSONDecodeError as e:
        issues.append(f"{file_path}: invalid JSON - {e}")
    except Exception as e:
        issues.append(f"{file_path}: error reading file - {e}")
    
    return issues


def validate_confluence_url(url: str) -> bool:
    """
    Validate if a URL looks like a Confluence URL.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL appears to be a Confluence URL
    """
    if not url or not isinstance(url, str):
        return False
    
    # Basic Confluence URL patterns
    confluence_patterns = [
        "/wiki/spaces/",
        "/wiki/pages/",
        ".atlassian.net/wiki/",
        "/confluence/",
    ]
    
    return any(pattern in url.lower() for pattern in confluence_patterns)


def get_data_summary(data_dir: str) -> Dict[str, Any]:
    """
    Get a summary of the data directory.
    
    Args:
        data_dir: Path to the data directory
        
    Returns:
        Dict containing data summary
    """
    summary = {
        "data_directory": data_dir,
        "exists": False,
        "total_files": 0,
        "spaces": [],
        "total_size_bytes": 0,
        "validation_status": "unknown"
    }
    
    data_path = Path(data_dir)
    
    if not data_path.exists():
        return summary
    
    summary["exists"] = True
    
    # Count files and calculate size
    for file_path in data_path.rglob("*.json"):
        summary["total_files"] += 1
        summary["total_size_bytes"] += file_path.stat().st_size
    
    # Get spaces
    for space_dir in data_path.iterdir():
        if space_dir.is_dir() and space_dir.name != "__pycache__":
            summary["spaces"].append(space_dir.name)
    
    # Validate structure
    is_valid, issues = validate_data_structure(data_dir)
    summary["validation_status"] = "valid" if is_valid else "invalid"
    summary["validation_issues"] = issues
    
    return summary
