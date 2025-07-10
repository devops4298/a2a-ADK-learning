"""
Project-specific coding standards that combine TypeScript, Playwright, and Cucumber standards.
"""
from typing import Dict, List, Set
from .typescript_standards import TypeScriptStandards, CodeStandard
from .playwright_standards import PlaywrightStandards
from .cucumber_standards import CucumberStandards


class ProjectStandards:
    """Manages all coding standards for the TypeScript/Playwright/Cucumber project."""
    
    def __init__(self):
        self.typescript_standards = TypeScriptStandards()
        self.playwright_standards = PlaywrightStandards()
        self.cucumber_standards = CucumberStandards()
        self.project_specific_standards = self._initialize_project_standards()
    
    def _initialize_project_standards(self) -> Dict[str, CodeStandard]:
        """Initialize project-specific standards that don't fit into other categories."""
        return {
            # File Organization
            'project-file-structure': CodeStandard(
                rule_id='project-file-structure',
                description='Follow consistent file and folder structure',
                severity='warning',
                category='organization',
                auto_fixable=False,
                examples={
                    'bad': 'tests/login.spec.ts, pages/login.ts',
                    'good': 'tests/auth/login.spec.ts, pages/auth/LoginPage.ts'
                }
            ),
            'project-naming-conventions': CodeStandard(
                rule_id='project-naming-conventions',
                description='Follow consistent naming conventions across all file types',
                severity='warning',
                category='naming',
                auto_fixable=True
            ),
            
            # Documentation
            'project-readme-updated': CodeStandard(
                rule_id='project-readme-updated',
                description='Keep README.md updated with current setup instructions',
                severity='info',
                category='documentation',
                auto_fixable=False
            ),
            'project-code-comments': CodeStandard(
                rule_id='project-code-comments',
                description='Add meaningful comments for complex business logic',
                severity='warning',
                category='documentation',
                auto_fixable=False
            ),
            
            # Configuration
            'project-config-consistency': CodeStandard(
                rule_id='project-config-consistency',
                description='Maintain consistent configuration across environments',
                severity='error',
                category='configuration',
                auto_fixable=False
            ),
            'project-env-variables': CodeStandard(
                rule_id='project-env-variables',
                description='Use environment variables for configuration',
                severity='warning',
                category='configuration',
                auto_fixable=False
            ),
            
            # Testing Strategy
            'project-test-coverage': CodeStandard(
                rule_id='project-test-coverage',
                description='Maintain adequate test coverage for critical paths',
                severity='warning',
                category='testing',
                auto_fixable=False
            ),
            'project-test-data-management': CodeStandard(
                rule_id='project-test-data-management',
                description='Implement proper test data management strategy',
                severity='warning',
                category='testing',
                auto_fixable=False
            )
        }
    
    def get_all_standards(self) -> List[CodeStandard]:
        """Get all coding standards from all categories."""
        all_standards = []
        all_standards.extend(self.typescript_standards.get_all_standards())
        all_standards.extend(self.playwright_standards.get_all_standards())
        all_standards.extend(self.cucumber_standards.get_all_standards())
        all_standards.extend(list(self.project_specific_standards.values()))
        return all_standards
    
    def get_standards_for_file_type(self, file_extension: str) -> List[CodeStandard]:
        """Get relevant standards based on file type."""
        standards = []
        
        if file_extension in ['.ts', '.js']:
            standards.extend(self.typescript_standards.get_all_standards())
            
        if file_extension in ['.spec.ts', '.test.ts'] or 'playwright' in file_extension:
            standards.extend(self.playwright_standards.get_all_standards())
            
        if file_extension == '.feature':
            standards.extend(self.cucumber_standards.get_all_standards())
            
        # Always include project-specific standards
        standards.extend(list(self.project_specific_standards.values()))
        
        return standards
    
    def get_standards_by_severity(self, severity: str) -> List[CodeStandard]:
        """Get all standards with a specific severity level."""
        all_standards = self.get_all_standards()
        return [std for std in all_standards if std.severity == severity]
    
    def get_auto_fixable_standards(self) -> List[CodeStandard]:
        """Get all standards that can be automatically fixed."""
        all_standards = self.get_all_standards()
        return [std for std in all_standards if std.auto_fixable]
    
    def get_standards_by_category(self, category: str) -> List[CodeStandard]:
        """Get all standards for a specific category."""
        all_standards = self.get_all_standards()
        return [std for std in all_standards if std.category == category]
    
    def get_rule_categories(self) -> Set[str]:
        """Get all available rule categories."""
        all_standards = self.get_all_standards()
        return set(std.category for std in all_standards)
    
    def get_standard_by_id(self, rule_id: str) -> CodeStandard:
        """Get a specific standard by its rule ID."""
        # Check TypeScript standards
        standard = self.typescript_standards.get_standard(rule_id)
        if standard:
            return standard
            
        # Check Playwright standards
        standard = self.playwright_standards.get_standard(rule_id)
        if standard:
            return standard
            
        # Check Cucumber standards
        standard = self.cucumber_standards.get_standard(rule_id)
        if standard:
            return standard
            
        # Check project-specific standards
        return self.project_specific_standards.get(rule_id)
