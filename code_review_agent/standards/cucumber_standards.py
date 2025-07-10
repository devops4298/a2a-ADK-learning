"""
Cucumber BDD coding standards and best practices.
"""
from typing import Dict, List
from .typescript_standards import CodeStandard


class CucumberStandards:
    """Defines Cucumber/Gherkin coding standards and best practices."""
    
    def __init__(self):
        self.standards = self._initialize_standards()
    
    def _initialize_standards(self) -> Dict[str, CodeStandard]:
        """Initialize all Cucumber coding standards."""
        return {
            # Feature File Structure
            'cucumber-feature-structure': CodeStandard(
                rule_id='cucumber-feature-structure',
                description='Feature files should follow proper Gherkin structure',
                severity='error',
                category='structure',
                auto_fixable=False,
                examples={
                    'bad': 'Feature: Login\nI want to login',
                    'good': 'Feature: User Login\n  As a user\n  I want to login to the system\n  So that I can access my account'
                }
            ),
            'cucumber-scenario-naming': CodeStandard(
                rule_id='cucumber-scenario-naming',
                description='Scenarios should have descriptive names in business language',
                severity='warning',
                category='naming',
                auto_fixable=False,
                examples={
                    'bad': 'Scenario: Test login',
                    'good': 'Scenario: User successfully logs in with valid credentials'
                }
            ),
            
            # Gherkin Best Practices
            'cucumber-given-when-then': CodeStandard(
                rule_id='cucumber-given-when-then',
                description='Use proper Given-When-Then structure in scenarios',
                severity='error',
                category='gherkin',
                auto_fixable=False,
                examples={
                    'bad': 'When I am on login page\nWhen I enter credentials',
                    'good': 'Given I am on the login page\nWhen I enter valid credentials\nThen I should be logged in'
                }
            ),
            'cucumber-imperative-mood': CodeStandard(
                rule_id='cucumber-imperative-mood',
                description='Write steps in imperative mood from user perspective',
                severity='warning',
                category='gherkin',
                auto_fixable=False,
                examples={
                    'bad': 'Given the login page is displayed',
                    'good': 'Given I am on the login page'
                }
            ),
            'cucumber-no-ui-details': CodeStandard(
                rule_id='cucumber-no-ui-details',
                description='Avoid UI implementation details in feature files',
                severity='warning',
                category='gherkin',
                auto_fixable=False,
                examples={
                    'bad': 'When I click the button with id "submit-btn"',
                    'good': 'When I submit the login form'
                }
            ),
            
            # Step Definitions
            'cucumber-step-reusability': CodeStandard(
                rule_id='cucumber-step-reusability',
                description='Create reusable step definitions',
                severity='warning',
                category='step-definitions',
                auto_fixable=False
            ),
            'cucumber-step-parameters': CodeStandard(
                rule_id='cucumber-step-parameters',
                description='Use parameters in step definitions for flexibility',
                severity='warning',
                category='step-definitions',
                auto_fixable=False,
                examples={
                    'bad': 'Given("I enter username john", async () => {})',
                    'good': 'Given("I enter username {string}", async (username) => {})'
                }
            ),
            'cucumber-step-organization': CodeStandard(
                rule_id='cucumber-step-organization',
                description='Organize step definitions by domain/feature',
                severity='warning',
                category='step-definitions',
                auto_fixable=False
            ),
            
            # Data Management
            'cucumber-data-tables': CodeStandard(
                rule_id='cucumber-data-tables',
                description='Use data tables for structured test data',
                severity='info',
                category='data',
                auto_fixable=False,
                examples={
                    'bad': 'Given I have user john with email john@test.com',
                    'good': 'Given I have the following users:\n  | name | email |\n  | john | john@test.com |'
                }
            ),
            'cucumber-scenario-outline': CodeStandard(
                rule_id='cucumber-scenario-outline',
                description='Use Scenario Outline for data-driven tests',
                severity='info',
                category='data',
                auto_fixable=False
            ),
            'cucumber-external-data': CodeStandard(
                rule_id='cucumber-external-data',
                description='Keep test data external to feature files when appropriate',
                severity='warning',
                category='data',
                auto_fixable=False
            ),
            
            # Tags and Organization
            'cucumber-meaningful-tags': CodeStandard(
                rule_id='cucumber-meaningful-tags',
                description='Use meaningful tags for test organization',
                severity='warning',
                category='organization',
                auto_fixable=False,
                examples={
                    'bad': '@test1 @temp',
                    'good': '@smoke @login @critical'
                }
            ),
            'cucumber-tag-conventions': CodeStandard(
                rule_id='cucumber-tag-conventions',
                description='Follow consistent tag naming conventions',
                severity='warning',
                category='organization',
                auto_fixable=False
            ),
            
            # Background Usage
            'cucumber-background-usage': CodeStandard(
                rule_id='cucumber-background-usage',
                description='Use Background for common setup steps',
                severity='info',
                category='structure',
                auto_fixable=False
            ),
            'cucumber-background-limit': CodeStandard(
                rule_id='cucumber-background-limit',
                description='Keep Background steps minimal and relevant to all scenarios',
                severity='warning',
                category='structure',
                auto_fixable=False
            ),
            
            # Documentation
            'cucumber-feature-description': CodeStandard(
                rule_id='cucumber-feature-description',
                description='Provide clear feature descriptions with business value',
                severity='warning',
                category='documentation',
                auto_fixable=False
            ),
            'cucumber-scenario-comments': CodeStandard(
                rule_id='cucumber-scenario-comments',
                description='Add comments for complex business logic',
                severity='info',
                category='documentation',
                auto_fixable=False
            ),
            
            # Maintenance
            'cucumber-no-duplicate-scenarios': CodeStandard(
                rule_id='cucumber-no-duplicate-scenarios',
                description='Avoid duplicate scenarios across feature files',
                severity='warning',
                category='maintenance',
                auto_fixable=False
            ),
            'cucumber-scenario-independence': CodeStandard(
                rule_id='cucumber-scenario-independence',
                description='Scenarios should be independent and not rely on execution order',
                severity='error',
                category='maintenance',
                auto_fixable=False
            )
        }
    
    def get_standard(self, rule_id: str) -> CodeStandard:
        """Get a specific Cucumber standard by rule ID."""
        return self.standards.get(rule_id)
    
    def get_standards_by_category(self, category: str) -> List[CodeStandard]:
        """Get all standards for a specific category."""
        return [std for std in self.standards.values() if std.category == category]
    
    def get_all_standards(self) -> List[CodeStandard]:
        """Get all Cucumber coding standards."""
        return list(self.standards.values())
    
    def get_auto_fixable_standards(self) -> List[CodeStandard]:
        """Get all standards that can be automatically fixed."""
        return [std for std in self.standards.values() if std.auto_fixable]
