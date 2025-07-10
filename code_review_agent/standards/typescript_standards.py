"""
TypeScript coding standards and best practices for code review.
"""
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CodeStandard:
    """Represents a single coding standard rule."""
    rule_id: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    category: str
    auto_fixable: bool = False
    examples: Dict[str, str] = None  # 'bad' and 'good' examples


class TypeScriptStandards:
    """Defines TypeScript coding standards and best practices."""
    
    def __init__(self):
        self.standards = self._initialize_standards()
    
    def _initialize_standards(self) -> Dict[str, CodeStandard]:
        """Initialize all TypeScript coding standards."""
        return {
            # Naming Conventions
            'ts-naming-camelcase': CodeStandard(
                rule_id='ts-naming-camelcase',
                description='Variables and functions should use camelCase',
                severity='warning',
                category='naming',
                auto_fixable=True,
                examples={
                    'bad': 'const user_name = "john";',
                    'good': 'const userName = "john";'
                }
            ),
            'ts-naming-pascalcase-classes': CodeStandard(
                rule_id='ts-naming-pascalcase-classes',
                description='Classes and interfaces should use PascalCase',
                severity='warning',
                category='naming',
                auto_fixable=True,
                examples={
                    'bad': 'class userService {}',
                    'good': 'class UserService {}'
                }
            ),
            'ts-naming-constants': CodeStandard(
                rule_id='ts-naming-constants',
                description='Constants should use UPPER_SNAKE_CASE',
                severity='warning',
                category='naming',
                auto_fixable=True,
                examples={
                    'bad': 'const maxRetries = 3;',
                    'good': 'const MAX_RETRIES = 3;'
                }
            ),
            
            # Type Safety
            'ts-explicit-types': CodeStandard(
                rule_id='ts-explicit-types',
                description='Function parameters and return types should be explicitly typed',
                severity='error',
                category='type-safety',
                auto_fixable=False,
                examples={
                    'bad': 'function processUser(user) { return user.name; }',
                    'good': 'function processUser(user: User): string { return user.name; }'
                }
            ),
            'ts-no-any': CodeStandard(
                rule_id='ts-no-any',
                description='Avoid using "any" type, use specific types instead',
                severity='warning',
                category='type-safety',
                auto_fixable=False,
                examples={
                    'bad': 'const data: any = response.data;',
                    'good': 'const data: UserData = response.data;'
                }
            ),
            'ts-strict-null-checks': CodeStandard(
                rule_id='ts-strict-null-checks',
                description='Handle null and undefined values explicitly',
                severity='error',
                category='type-safety',
                auto_fixable=False,
                examples={
                    'bad': 'const name = user.name.toUpperCase();',
                    'good': 'const name = user.name?.toUpperCase() ?? "";'
                }
            ),
            
            # Code Structure
            'ts-single-responsibility': CodeStandard(
                rule_id='ts-single-responsibility',
                description='Functions should have a single responsibility',
                severity='warning',
                category='structure',
                auto_fixable=False
            ),
            'ts-max-function-length': CodeStandard(
                rule_id='ts-max-function-length',
                description='Functions should not exceed 50 lines',
                severity='warning',
                category='structure',
                auto_fixable=False
            ),
            'ts-prefer-const': CodeStandard(
                rule_id='ts-prefer-const',
                description='Use const for variables that are never reassigned',
                severity='warning',
                category='structure',
                auto_fixable=True,
                examples={
                    'bad': 'let userName = "john";',
                    'good': 'const userName = "john";'
                }
            ),
            
            # Import/Export
            'ts-import-order': CodeStandard(
                rule_id='ts-import-order',
                description='Imports should be ordered: external libraries, internal modules, relative imports',
                severity='warning',
                category='imports',
                auto_fixable=True
            ),
            'ts-no-unused-imports': CodeStandard(
                rule_id='ts-no-unused-imports',
                description='Remove unused imports',
                severity='warning',
                category='imports',
                auto_fixable=True
            ),
            
            # Error Handling
            'ts-proper-error-handling': CodeStandard(
                rule_id='ts-proper-error-handling',
                description='Use proper error handling with try-catch blocks',
                severity='error',
                category='error-handling',
                auto_fixable=False
            ),
            'ts-custom-error-types': CodeStandard(
                rule_id='ts-custom-error-types',
                description='Use custom error types instead of generic Error',
                severity='warning',
                category='error-handling',
                auto_fixable=False
            )
        }
    
    def get_standard(self, rule_id: str) -> CodeStandard:
        """Get a specific coding standard by rule ID."""
        return self.standards.get(rule_id)
    
    def get_standards_by_category(self, category: str) -> List[CodeStandard]:
        """Get all standards for a specific category."""
        return [std for std in self.standards.values() if std.category == category]
    
    def get_all_standards(self) -> List[CodeStandard]:
        """Get all TypeScript coding standards."""
        return list(self.standards.values())
    
    def get_auto_fixable_standards(self) -> List[CodeStandard]:
        """Get all standards that can be automatically fixed."""
        return [std for std in self.standards.values() if std.auto_fixable]
