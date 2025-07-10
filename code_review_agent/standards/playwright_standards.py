"""
Playwright automation coding standards and best practices.
"""
from typing import Dict, List
from .typescript_standards import CodeStandard


class PlaywrightStandards:
    """Defines Playwright-specific coding standards and best practices."""
    
    def __init__(self):
        self.standards = self._initialize_standards()
    
    def _initialize_standards(self) -> Dict[str, CodeStandard]:
        """Initialize all Playwright coding standards."""
        return {
            # Page Object Model
            'pw-page-object-pattern': CodeStandard(
                rule_id='pw-page-object-pattern',
                description='Use Page Object Model pattern for page interactions',
                severity='warning',
                category='architecture',
                auto_fixable=False,
                examples={
                    'bad': 'await page.click("#login-button");',
                    'good': 'await loginPage.clickLoginButton();'
                }
            ),
            'pw-page-object-naming': CodeStandard(
                rule_id='pw-page-object-naming',
                description='Page objects should end with "Page" suffix',
                severity='warning',
                category='naming',
                auto_fixable=True,
                examples={
                    'bad': 'class Login {}',
                    'good': 'class LoginPage {}'
                }
            ),
            
            # Locator Best Practices
            'pw-stable-locators': CodeStandard(
                rule_id='pw-stable-locators',
                description='Use stable locators (data-testid, role, text) over CSS selectors',
                severity='error',
                category='locators',
                auto_fixable=False,
                examples={
                    'bad': 'page.locator(".btn-primary")',
                    'good': 'page.getByTestId("submit-button")'
                }
            ),
            'pw-no-xpath': CodeStandard(
                rule_id='pw-no-xpath',
                description='Avoid XPath locators, use Playwright locators instead',
                severity='warning',
                category='locators',
                auto_fixable=False,
                examples={
                    'bad': 'page.locator("//button[@class=\'submit\']")',
                    'good': 'page.getByRole("button", { name: "Submit" })'
                }
            ),
            'pw-locator-variables': CodeStandard(
                rule_id='pw-locator-variables',
                description='Store complex locators in variables for reusability',
                severity='warning',
                category='locators',
                auto_fixable=False
            ),
            
            # Waiting and Assertions
            'pw-explicit-waits': CodeStandard(
                rule_id='pw-explicit-waits',
                description='Use explicit waits instead of hard waits (sleep)',
                severity='error',
                category='waits',
                auto_fixable=False,
                examples={
                    'bad': 'await page.waitForTimeout(5000);',
                    'good': 'await page.waitForSelector("[data-testid=\'result\']");'
                }
            ),
            'pw-auto-waiting': CodeStandard(
                rule_id='pw-auto-waiting',
                description='Leverage Playwright auto-waiting capabilities',
                severity='info',
                category='waits',
                auto_fixable=False
            ),
            'pw-proper-assertions': CodeStandard(
                rule_id='pw-proper-assertions',
                description='Use Playwright assertions (expect) instead of generic assertions',
                severity='warning',
                category='assertions',
                auto_fixable=True,
                examples={
                    'bad': 'assert(await page.isVisible("#element"));',
                    'good': 'await expect(page.locator("#element")).toBeVisible();'
                }
            ),
            
            # Test Structure
            'pw-test-isolation': CodeStandard(
                rule_id='pw-test-isolation',
                description='Each test should be independent and isolated',
                severity='error',
                category='test-structure',
                auto_fixable=False
            ),
            'pw-setup-teardown': CodeStandard(
                rule_id='pw-setup-teardown',
                description='Use proper setup and teardown in beforeEach/afterEach',
                severity='warning',
                category='test-structure',
                auto_fixable=False
            ),
            'pw-descriptive-test-names': CodeStandard(
                rule_id='pw-descriptive-test-names',
                description='Test names should be descriptive and follow Given-When-Then pattern',
                severity='warning',
                category='test-structure',
                auto_fixable=False,
                examples={
                    'bad': 'test("login test", async () => {})',
                    'good': 'test("should login successfully with valid credentials", async () => {})'
                }
            ),
            
            # Performance
            'pw-parallel-execution': CodeStandard(
                rule_id='pw-parallel-execution',
                description='Configure tests for parallel execution when possible',
                severity='info',
                category='performance',
                auto_fixable=False
            ),
            'pw-browser-context': CodeStandard(
                rule_id='pw-browser-context',
                description='Use browser contexts for test isolation instead of new browser instances',
                severity='warning',
                category='performance',
                auto_fixable=False
            ),
            
            # Error Handling
            'pw-screenshot-on-failure': CodeStandard(
                rule_id='pw-screenshot-on-failure',
                description='Capture screenshots on test failures for debugging',
                severity='warning',
                category='debugging',
                auto_fixable=False
            ),
            'pw-video-recording': CodeStandard(
                rule_id='pw-video-recording',
                description='Enable video recording for failed tests',
                severity='info',
                category='debugging',
                auto_fixable=False
            ),
            
            # Configuration
            'pw-config-best-practices': CodeStandard(
                rule_id='pw-config-best-practices',
                description='Follow Playwright configuration best practices',
                severity='warning',
                category='configuration',
                auto_fixable=False
            ),
            'pw-environment-specific-config': CodeStandard(
                rule_id='pw-environment-specific-config',
                description='Use environment-specific configurations',
                severity='warning',
                category='configuration',
                auto_fixable=False
            )
        }
    
    def get_standard(self, rule_id: str) -> CodeStandard:
        """Get a specific Playwright standard by rule ID."""
        return self.standards.get(rule_id)
    
    def get_standards_by_category(self, category: str) -> List[CodeStandard]:
        """Get all standards for a specific category."""
        return [std for std in self.standards.values() if std.category == category]
    
    def get_all_standards(self) -> List[CodeStandard]:
        """Get all Playwright coding standards."""
        return list(self.standards.values())
    
    def get_auto_fixable_standards(self) -> List[CodeStandard]:
        """Get all standards that can be automatically fixed."""
        return [std for std in self.standards.values() if std.auto_fixable]
