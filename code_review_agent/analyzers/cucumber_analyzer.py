"""
Cucumber/Gherkin-specific code analyzer.
"""
import re
from typing import List, Dict, Any
from .base_analyzer import BaseAnalyzer, CodeIssue
from ..standards.cucumber_standards import CucumberStandards


class CucumberAnalyzer(BaseAnalyzer):
    """Analyzer for Cucumber feature files and step definitions."""
    
    def __init__(self):
        super().__init__()
        self.standards = CucumberStandards()
    
    def _analyze_content(self, content: str, file_path: str):
        """Analyze Cucumber content for BDD best practices."""
        if file_path.endswith('.feature'):
            self._analyze_feature_file(content, file_path)
        elif 'step' in file_path.lower() or 'steps' in file_path.lower():
            self._analyze_step_definitions(content, file_path)
    
    def _analyze_feature_file(self, content: str, file_path: str):
        """Analyze Gherkin feature files."""
        self._check_feature_structure(content, file_path)
        self._check_scenario_quality(content, file_path)
        self._check_gherkin_syntax(content, file_path)
        self._check_tags_usage(content, file_path)
        self._check_background_usage(content, file_path)
    
    def _analyze_step_definitions(self, content: str, file_path: str):
        """Analyze step definition files."""
        self._check_step_definition_quality(content, file_path)
        self._check_step_reusability(content, file_path)
        self._check_step_organization(content, file_path)
    
    def _check_feature_structure(self, content: str, file_path: str):
        """Check feature file structure."""
        lines = content.split('\n')
        
        # Check for proper feature declaration
        feature_found = False
        feature_line = 0
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('Feature:'):
                feature_found = True
                feature_line = line_num
                
                # Check feature description
                feature_text = line.replace('Feature:', '').strip()
                if len(feature_text) < 10:
                    self._add_issue(
                        'cucumber-feature-description',
                        'Feature description should be more descriptive',
                        'warning',
                        line_num,
                        0,
                        file_path,
                        category='documentation'
                    )
                break
        
        if not feature_found:
            self._add_issue(
                'cucumber-feature-structure',
                'Feature file must start with a Feature declaration',
                'error',
                1,
                0,
                file_path,
                category='structure'
            )
        
        # Check for feature description (As a... I want... So that...)
        feature_section = '\n'.join(lines[feature_line:feature_line+10]) if feature_found else content
        if not re.search(r'As a.*I want.*So that', feature_section, re.DOTALL | re.IGNORECASE):
            self._add_issue(
                'cucumber-feature-structure',
                'Feature should include user story format (As a... I want... So that...)',
                'warning',
                feature_line + 1 if feature_found else 1,
                0,
                file_path,
                suggested_fix='Add: As a [user] I want [goal] So that [benefit]',
                category='structure'
            )
    
    def _check_scenario_quality(self, content: str, file_path: str):
        """Check scenario quality and naming."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('Scenario:'):
                scenario_name = line.replace('Scenario:', '').strip()
                
                # Check scenario naming
                if len(scenario_name) < 15:
                    self._add_issue(
                        'cucumber-scenario-naming',
                        'Scenario names should be more descriptive',
                        'warning',
                        line_num,
                        0,
                        file_path,
                        suggested_fix='Use business language to describe the scenario',
                        category='naming'
                    )
                
                # Check for technical details in scenario name
                if any(tech_word in scenario_name.lower() for tech_word in ['click', 'button', 'field', 'input']):
                    self._add_issue(
                        'cucumber-no-ui-details',
                        'Scenario names should avoid UI implementation details',
                        'warning',
                        line_num,
                        0,
                        file_path,
                        suggested_fix='Focus on business behavior, not UI elements',
                        category='gherkin'
                    )
    
    def _check_gherkin_syntax(self, content: str, file_path: str):
        """Check Gherkin syntax and best practices."""
        lines = content.split('\n')
        
        scenario_steps = []
        current_scenario_line = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('Scenario:'):
                # Analyze previous scenario if exists
                if scenario_steps:
                    self._analyze_scenario_steps(scenario_steps, current_scenario_line, file_path)
                scenario_steps = []
                current_scenario_line = line_num
            
            elif stripped.startswith(('Given ', 'When ', 'Then ', 'And ', 'But ')):
                scenario_steps.append((line_num, stripped))
                
                # Check for imperative mood
                if not self._is_imperative_mood(stripped):
                    self._add_issue(
                        'cucumber-imperative-mood',
                        'Steps should be written in imperative mood from user perspective',
                        'warning',
                        line_num,
                        0,
                        file_path,
                        suggested_fix='Start with "I" or use active voice',
                        category='gherkin'
                    )
                
                # Check for UI details in steps
                if any(ui_word in stripped.lower() for ui_word in ['click', 'button', 'field', 'input', 'dropdown']):
                    self._add_issue(
                        'cucumber-no-ui-details',
                        'Steps should avoid UI implementation details',
                        'warning',
                        line_num,
                        0,
                        file_path,
                        suggested_fix='Focus on business actions, not UI interactions',
                        category='gherkin'
                    )
        
        # Analyze last scenario
        if scenario_steps:
            self._analyze_scenario_steps(scenario_steps, current_scenario_line, file_path)
    
    def _analyze_scenario_steps(self, steps: List[tuple], scenario_line: int, file_path: str):
        """Analyze the structure of scenario steps."""
        if not steps:
            return
        
        # Check Given-When-Then structure
        step_types = [self._get_step_type(step[1]) for step in steps]
        
        # Should start with Given
        if step_types[0] != 'Given':
            self._add_issue(
                'cucumber-given-when-then',
                'Scenario should start with Given step',
                'error',
                steps[0][0],
                0,
                file_path,
                category='gherkin'
            )
        
        # Check for proper flow
        given_phase = True
        when_phase = False
        then_phase = False
        
        for i, step_type in enumerate(step_types):
            if step_type == 'When':
                given_phase = False
                when_phase = True
            elif step_type == 'Then':
                when_phase = False
                then_phase = True
            elif step_type == 'Given' and (when_phase or then_phase):
                self._add_issue(
                    'cucumber-given-when-then',
                    'Given steps should not appear after When or Then',
                    'error',
                    steps[i][0],
                    0,
                    file_path,
                    category='gherkin'
                )
    
    def _get_step_type(self, step: str) -> str:
        """Get the type of a Gherkin step."""
        if step.startswith('Given '):
            return 'Given'
        elif step.startswith('When '):
            return 'When'
        elif step.startswith('Then '):
            return 'Then'
        elif step.startswith(('And ', 'But ')):
            return 'And/But'
        return 'Unknown'
    
    def _is_imperative_mood(self, step: str) -> bool:
        """Check if a step is written in imperative mood."""
        # Remove step keywords
        step_text = re.sub(r'^(Given|When|Then|And|But)\s+', '', step)
        
        # Check if it starts with "I" or common imperative patterns
        imperative_patterns = [
            r'^I\s+',
            r'^The\s+user\s+',
            r'^User\s+',
            r'^A\s+user\s+'
        ]
        
        return any(re.match(pattern, step_text, re.IGNORECASE) for pattern in imperative_patterns)
    
    def _check_tags_usage(self, content: str, file_path: str):
        """Check tag usage and conventions."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('@'):
                tags = re.findall(r'@(\w+)', line)
                
                for tag in tags:
                    # Check for meaningful tag names
                    if tag.lower() in ['test', 'temp', 'todo', 'wip']:
                        self._add_issue(
                            'cucumber-meaningful-tags',
                            f'Tag "@{tag}" is not meaningful, use descriptive tags',
                            'warning',
                            line_num,
                            0,
                            file_path,
                            suggested_fix='Use tags like @smoke, @regression, @critical',
                            category='organization'
                        )
                    
                    # Check tag naming convention
                    if not tag.islower():
                        self._add_issue(
                            'cucumber-tag-conventions',
                            f'Tag "@{tag}" should use lowercase naming convention',
                            'warning',
                            line_num,
                            0,
                            file_path,
                            suggested_fix=f'@{tag.lower()}',
                            auto_fixable=True,
                            category='organization'
                        )
    
    def _check_background_usage(self, content: str, file_path: str):
        """Check Background usage."""
        if 'Background:' in content:
            background_steps = re.findall(r'Background:.*?(?=Scenario:|$)', content, re.DOTALL)
            
            if background_steps:
                step_count = len(re.findall(r'^\s*(Given|When|Then|And|But)', background_steps[0], re.MULTILINE))
                
                if step_count > 5:
                    self._add_issue(
                        'cucumber-background-limit',
                        'Background has too many steps, keep it minimal',
                        'warning',
                        1,
                        0,
                        file_path,
                        suggested_fix='Move non-essential steps to individual scenarios',
                        category='structure'
                    )
    
    def _check_step_definition_quality(self, content: str, file_path: str):
        """Check step definition quality."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for parameterized step definitions
            if re.search(r'(Given|When|Then)\s*\(\s*["\'][^"\']*["\']', line):
                step_text = re.search(r'["\']([^"\']*)["\']', line)
                if step_text and '{' not in step_text.group(1) and 'string' not in step_text.group(1):
                    # Check if step could be parameterized
                    if any(word in step_text.group(1).lower() for word in ['john', 'test', 'example', '123']):
                        self._add_issue(
                            'cucumber-step-parameters',
                            'Consider parameterizing step definition for reusability',
                            'warning',
                            line_num,
                            0,
                            file_path,
                            suggested_fix='Use {string} or {int} parameters',
                            category='step-definitions'
                        )
    
    def _check_step_reusability(self, content: str, file_path: str):
        """Check for step reusability patterns."""
        # This would typically involve cross-file analysis
        # For now, we'll do basic checks within the file
        step_definitions = re.findall(r'(Given|When|Then)\s*\([^)]+\)', content)
        
        if len(set(step_definitions)) != len(step_definitions):
            self._add_issue(
                'cucumber-step-reusability',
                'Duplicate step definitions found, ensure reusability',
                'warning',
                1,
                0,
                file_path,
                category='step-definitions'
            )
    
    def _check_step_organization(self, content: str, file_path: str):
        """Check step definition organization."""
        # Check if file follows domain organization
        if not any(domain in file_path.lower() for domain in ['auth', 'user', 'product', 'order', 'common']):
            self._add_issue(
                'cucumber-step-organization',
                'Consider organizing step definitions by domain/feature',
                'warning',
                1,
                0,
                file_path,
                suggested_fix='Group steps by business domain',
                category='step-definitions'
            )
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the Cucumber analysis results."""
        return {
            'total_issues': len(self.issues),
            'errors': len([i for i in self.issues if i.severity == 'error']),
            'warnings': len([i for i in self.issues if i.severity == 'warning']),
            'info': len([i for i in self.issues if i.severity == 'info']),
            'auto_fixable': len([i for i in self.issues if i.auto_fixable]),
            'categories': list(set(i.category for i in self.issues)),
            'gherkin_issues': len([i for i in self.issues if i.category == 'gherkin']),
            'structure_issues': len([i for i in self.issues if i.category == 'structure'])
        }
