"""
Manual fix suggestions and guidance for complex issues.
"""
from typing import List, Dict, Any, Optional
from ..analyzers.base_analyzer import CodeIssue


class ManualFixer:
    """Provides manual fix suggestions for complex issues that can't be auto-fixed."""
    
    def __init__(self):
        self.fix_suggestions = self._initialize_fix_suggestions()
    
    def _initialize_fix_suggestions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize manual fix suggestions for different rule types."""
        return {
            # TypeScript manual fixes
            'ts-explicit-types': {
                'title': 'Add Explicit Type Annotations',
                'description': 'Function parameters and return types should be explicitly typed',
                'steps': [
                    'Identify the expected parameter types',
                    'Add type annotations to function parameters',
                    'Add return type annotation to the function',
                    'Consider creating interfaces for complex types'
                ],
                'example': {
                    'before': 'function processUser(user) { return user.name; }',
                    'after': 'function processUser(user: User): string { return user.name; }'
                },
                'resources': [
                    'https://www.typescriptlang.org/docs/handbook/2/functions.html',
                    'TypeScript Handbook: Function Types'
                ]
            },
            'ts-no-any': {
                'title': 'Replace "any" with Specific Types',
                'description': 'Avoid using "any" type for better type safety',
                'steps': [
                    'Analyze the actual data structure being used',
                    'Create specific interfaces or types',
                    'Use union types if multiple types are possible',
                    'Consider using generics for reusable components'
                ],
                'example': {
                    'before': 'const data: any = response.data;',
                    'after': 'interface ApiResponse { id: number; name: string; }\nconst data: ApiResponse = response.data;'
                },
                'resources': [
                    'https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#any'
                ]
            },
            'ts-single-responsibility': {
                'title': 'Refactor for Single Responsibility',
                'description': 'Functions should have a single, well-defined responsibility',
                'steps': [
                    'Identify the different responsibilities in the function',
                    'Extract each responsibility into separate functions',
                    'Create clear, descriptive names for each function',
                    'Ensure each function has a single purpose'
                ],
                'example': {
                    'before': '// Function that validates, transforms, and saves user data',
                    'after': '// Split into: validateUser(), transformUserData(), saveUser()'
                }
            },
            
            # Playwright manual fixes
            'pw-page-object-pattern': {
                'title': 'Implement Page Object Model',
                'description': 'Use Page Object Model pattern for better test maintainability',
                'steps': [
                    'Create a page class for each page in your application',
                    'Move locators and page interactions to the page class',
                    'Create methods for common page actions',
                    'Use the page object in your tests'
                ],
                'example': {
                    'before': 'await page.click("#login-button");',
                    'after': 'class LoginPage {\n  async clickLoginButton() {\n    await this.page.click("#login-button");\n  }\n}'
                },
                'resources': [
                    'https://playwright.dev/docs/pom',
                    'Playwright Page Object Model Guide'
                ]
            },
            'pw-stable-locators': {
                'title': 'Use Stable Locators',
                'description': 'Replace CSS selectors with stable, semantic locators',
                'steps': [
                    'Add data-testid attributes to elements',
                    'Use getByRole() for semantic elements',
                    'Use getByText() for text-based selection',
                    'Avoid CSS class and ID selectors'
                ],
                'example': {
                    'before': 'page.locator(".btn-primary")',
                    'after': 'page.getByTestId("submit-button") or page.getByRole("button", { name: "Submit" })'
                }
            },
            'pw-test-isolation': {
                'title': 'Ensure Test Isolation',
                'description': 'Each test should be independent and not rely on other tests',
                'steps': [
                    'Move shared setup to beforeEach hooks',
                    'Clean up test data after each test',
                    'Avoid dependencies between tests',
                    'Use fresh browser contexts for each test'
                ],
                'example': {
                    'before': 'beforeAll(() => { /* shared login */ })',
                    'after': 'beforeEach(() => { /* fresh login for each test */ })'
                }
            },
            
            # Cucumber manual fixes
            'cucumber-given-when-then': {
                'title': 'Fix Given-When-Then Structure',
                'description': 'Scenarios should follow proper Given-When-Then flow',
                'steps': [
                    'Start with Given steps for setup/context',
                    'Use When steps for actions',
                    'Use Then steps for assertions',
                    'Avoid mixing step types inappropriately'
                ],
                'example': {
                    'before': 'When I am on login page\nWhen I enter credentials',
                    'after': 'Given I am on the login page\nWhen I enter valid credentials\nThen I should be logged in'
                }
            },
            'cucumber-imperative-mood': {
                'title': 'Write Steps in Imperative Mood',
                'description': 'Steps should be written from the user\'s perspective',
                'steps': [
                    'Start steps with "I" or "User"',
                    'Use active voice',
                    'Focus on user actions and outcomes',
                    'Avoid passive voice and system perspective'
                ],
                'example': {
                    'before': 'Given the login page is displayed',
                    'after': 'Given I am on the login page'
                }
            },
            'cucumber-no-ui-details': {
                'title': 'Remove UI Implementation Details',
                'description': 'Focus on business behavior, not UI elements',
                'steps': [
                    'Replace UI element references with business actions',
                    'Use business language instead of technical terms',
                    'Focus on what the user wants to achieve',
                    'Keep scenarios technology-agnostic'
                ],
                'example': {
                    'before': 'When I click the submit button',
                    'after': 'When I submit the form'
                }
            },
            
            # Architecture and design fixes
            'pw-performance': {
                'title': 'Optimize Test Performance',
                'description': 'Improve test execution speed and reliability',
                'steps': [
                    'Use browser contexts instead of new browsers',
                    'Configure parallel execution',
                    'Optimize waiting strategies',
                    'Minimize unnecessary actions'
                ],
                'resources': [
                    'https://playwright.dev/docs/test-parallel'
                ]
            },
            'project-test-coverage': {
                'title': 'Improve Test Coverage',
                'description': 'Ensure adequate test coverage for critical paths',
                'steps': [
                    'Identify critical user journeys',
                    'Create test scenarios for edge cases',
                    'Add negative test cases',
                    'Monitor and measure test coverage'
                ]
            }
        }
    
    def get_manual_suggestions(self, issues: List[CodeIssue]) -> List[Dict[str, Any]]:
        """Get manual fix suggestions for issues that can't be auto-fixed."""
        suggestions = []
        
        # Group issues by rule type
        issue_groups = {}
        for issue in issues:
            if not issue.auto_fixable:
                rule_id = issue.rule_id
                if rule_id not in issue_groups:
                    issue_groups[rule_id] = []
                issue_groups[rule_id].append(issue)
        
        # Generate suggestions for each rule type
        for rule_id, rule_issues in issue_groups.items():
            suggestion = self._create_suggestion(rule_id, rule_issues)
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions
    
    def _create_suggestion(self, rule_id: str, issues: List[CodeIssue]) -> Optional[Dict[str, Any]]:
        """Create a manual fix suggestion for a specific rule."""
        if rule_id in self.fix_suggestions:
            template = self.fix_suggestions[rule_id]
            
            return {
                'rule_id': rule_id,
                'title': template['title'],
                'description': template['description'],
                'affected_files': list(set(issue.file_path for issue in issues)),
                'affected_lines': [{'file': issue.file_path, 'line': issue.line_number} for issue in issues],
                'issue_count': len(issues),
                'severity': issues[0].severity if issues else 'warning',
                'steps': template.get('steps', []),
                'example': template.get('example'),
                'resources': template.get('resources', []),
                'estimated_effort': self._estimate_effort(rule_id, len(issues)),
                'priority': self._calculate_priority(issues)
            }
        
        # Generate generic suggestion for unknown rules
        return self._create_generic_suggestion(rule_id, issues)
    
    def _create_generic_suggestion(self, rule_id: str, issues: List[CodeIssue]) -> Dict[str, Any]:
        """Create a generic suggestion for unknown rules."""
        return {
            'rule_id': rule_id,
            'title': f'Address {rule_id} Issues',
            'description': issues[0].description if issues else 'Manual review required',
            'affected_files': list(set(issue.file_path for issue in issues)),
            'affected_lines': [{'file': issue.file_path, 'line': issue.line_number} for issue in issues],
            'issue_count': len(issues),
            'severity': issues[0].severity if issues else 'warning',
            'steps': [
                'Review the specific issue description',
                'Analyze the code context',
                'Apply appropriate fixes based on best practices',
                'Test the changes thoroughly'
            ],
            'estimated_effort': self._estimate_effort(rule_id, len(issues)),
            'priority': self._calculate_priority(issues)
        }
    
    def _estimate_effort(self, rule_id: str, issue_count: int) -> str:
        """Estimate the effort required to fix issues."""
        base_effort = {
            'ts-explicit-types': 'medium',
            'ts-no-any': 'medium',
            'ts-single-responsibility': 'high',
            'pw-page-object-pattern': 'high',
            'pw-stable-locators': 'low',
            'pw-test-isolation': 'medium',
            'cucumber-given-when-then': 'low',
            'cucumber-imperative-mood': 'low',
            'cucumber-no-ui-details': 'medium'
        }.get(rule_id, 'medium')
        
        # Adjust based on issue count
        if issue_count > 10:
            if base_effort == 'low':
                return 'medium'
            elif base_effort == 'medium':
                return 'high'
        
        return base_effort
    
    def _calculate_priority(self, issues: List[CodeIssue]) -> str:
        """Calculate priority based on issue severity and count."""
        error_count = len([i for i in issues if i.severity == 'error'])
        warning_count = len([i for i in issues if i.severity == 'warning'])
        
        if error_count > 0:
            return 'high'
        elif warning_count > 5:
            return 'medium'
        else:
            return 'low'
    
    def generate_fix_plan(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive fix plan from suggestions."""
        # Sort suggestions by priority and effort
        high_priority = [s for s in suggestions if s['priority'] == 'high']
        medium_priority = [s for s in suggestions if s['priority'] == 'medium']
        low_priority = [s for s in suggestions if s['priority'] == 'low']
        
        total_issues = sum(s['issue_count'] for s in suggestions)
        
        return {
            'total_manual_issues': total_issues,
            'total_suggestions': len(suggestions),
            'priority_breakdown': {
                'high': len(high_priority),
                'medium': len(medium_priority),
                'low': len(low_priority)
            },
            'recommended_order': high_priority + medium_priority + low_priority,
            'estimated_total_effort': self._calculate_total_effort(suggestions),
            'quick_wins': [s for s in suggestions if s['estimated_effort'] == 'low'],
            'major_refactoring': [s for s in suggestions if s['estimated_effort'] == 'high']
        }
    
    def _calculate_total_effort(self, suggestions: List[Dict[str, Any]]) -> str:
        """Calculate total effort for all suggestions."""
        effort_scores = {'low': 1, 'medium': 3, 'high': 5}
        total_score = sum(effort_scores.get(s['estimated_effort'], 3) for s in suggestions)
        
        if total_score <= 5:
            return 'low'
        elif total_score <= 15:
            return 'medium'
        else:
            return 'high'
    
    def get_suggestion_by_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get suggestion template for a specific rule."""
        return self.fix_suggestions.get(rule_id)
    
    def add_custom_suggestion(self, rule_id: str, suggestion: Dict[str, Any]):
        """Add a custom fix suggestion."""
        required_fields = ['title', 'description', 'steps']
        if all(field in suggestion for field in required_fields):
            self.fix_suggestions[rule_id] = suggestion
        else:
            raise ValueError(f"Suggestion must contain: {required_fields}")
    
    def get_learning_resources(self, categories: List[str]) -> Dict[str, List[str]]:
        """Get learning resources for specific categories."""
        resources = {
            'typescript': [
                'https://www.typescriptlang.org/docs/',
                'https://basarat.gitbook.io/typescript/',
                'TypeScript Deep Dive'
            ],
            'playwright': [
                'https://playwright.dev/docs/intro',
                'https://playwright.dev/docs/best-practices',
                'Playwright Testing Best Practices'
            ],
            'cucumber': [
                'https://cucumber.io/docs/gherkin/',
                'https://cucumber.io/docs/bdd/',
                'BDD with Cucumber Best Practices'
            ],
            'testing': [
                'https://martinfowler.com/articles/practical-test-pyramid.html',
                'Test Automation Pyramid',
                'Clean Code Testing Principles'
            ]
        }
        
        return {cat: resources.get(cat, []) for cat in categories if cat in resources}
