/**
 * VS Code Extension Integration for One-Click Fixes
 * This enables direct code replacement and UI integration
 */

const vscode = require('vscode');
const axios = require('axios');

class CodeReviewFixProvider {
    constructor() {
        this.agentUrl = 'http://localhost:8080';
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('ts-code-reviewer');
    }

    /**
     * Register the fix provider with VS Code
     */
    register() {
        // Register code action provider for quick fixes
        const codeActionProvider = vscode.languages.registerCodeActionsProvider(
            ['typescript', 'javascript'],
            this,
            {
                providedCodeActionKinds: [
                    vscode.CodeActionKind.QuickFix,
                    vscode.CodeActionKind.Refactor
                ]
            }
        );

        // Register command for one-click fix all
        const fixAllCommand = vscode.commands.registerCommand(
            'tsReviewer.fixAll',
            () => this.fixAllIssues()
        );

        // Register command for analyze and show fixes
        const analyzeCommand = vscode.commands.registerCommand(
            'tsReviewer.analyzeAndFix',
            () => this.analyzeAndShowFixes()
        );

        return [codeActionProvider, fixAllCommand, analyzeCommand];
    }

    /**
     * Provide code actions (quick fixes) for the current document
     */
    async provideCodeActions(document, range, context) {
        const actions = [];

        // Get current document content
        const content = document.getText();
        const filePath = document.fileName;

        try {
            // Analyze code to get fixable issues
            const issues = await this.analyzeCode(content, filePath);
            const fixableIssues = issues.filter(issue => issue.auto_fixable);

            if (fixableIssues.length > 0) {
                // Create "Fix All Auto-Fixable Issues" action
                const fixAllAction = new vscode.CodeAction(
                    `🔧 Fix ${fixableIssues.length} auto-fixable issues`,
                    vscode.CodeActionKind.QuickFix
                );
                fixAllAction.command = {
                    command: 'tsReviewer.fixAll',
                    title: 'Fix All Issues',
                    arguments: [document]
                };
                actions.push(fixAllAction);

                // Create individual fix actions for each issue
                for (const issue of fixableIssues.slice(0, 5)) { // Limit to 5 for UI
                    const fixAction = new vscode.CodeAction(
                        `🔧 ${issue.description}`,
                        vscode.CodeActionKind.QuickFix
                    );
                    fixAction.command = {
                        command: 'tsReviewer.fixSpecific',
                        title: `Fix: ${issue.rule_id}`,
                        arguments: [document, issue]
                    };
                    actions.push(fixAction);
                }
            }

            // Always provide "Analyze with Code Reviewer" action
            const analyzeAction = new vscode.CodeAction(
                '🔍 Analyze with Code Reviewer',
                vscode.CodeActionKind.Refactor
            );
            analyzeAction.command = {
                command: 'tsReviewer.analyzeAndFix',
                title: 'Analyze Code',
                arguments: [document]
            };
            actions.push(analyzeAction);

        } catch (error) {
            console.error('Error providing code actions:', error);
        }

        return actions;
    }

    /**
     * Fix all auto-fixable issues in the current document
     */
    async fixAllIssues() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        const document = editor.document;
        const content = document.getText();
        const filePath = document.fileName;

        try {
            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "🔧 Applying auto-fixes...",
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: "Analyzing code..." });

                // Get fixes from agent
                const fixResult = await this.applyFixes(content, filePath);

                if (fixResult.content_changed) {
                    progress.report({ increment: 50, message: "Applying fixes..." });

                    // Replace document content with fixed version
                    const edit = new vscode.WorkspaceEdit();
                    const fullRange = new vscode.Range(
                        document.positionAt(0),
                        document.positionAt(content.length)
                    );
                    edit.replace(document.uri, fullRange, fixResult.fixed_content);
                    
                    await vscode.workspace.applyEdit(edit);

                    progress.report({ increment: 100, message: "Complete!" });

                    // Show success message
                    const appliedCount = fixResult.applied_fixes.length;
                    vscode.window.showInformationMessage(
                        `✅ Applied ${appliedCount} automatic fixes!`,
                        'Show Details'
                    ).then(selection => {
                        if (selection === 'Show Details') {
                            this.showFixDetails(fixResult);
                        }
                    });
                } else {
                    progress.report({ increment: 100, message: "No fixes needed" });
                    vscode.window.showInformationMessage('✅ No auto-fixable issues found!');
                }
            });

        } catch (error) {
            vscode.window.showErrorMessage(`❌ Fix failed: ${error.message}`);
        }
    }

    /**
     * Analyze code and show fixable issues with one-click options
     */
    async analyzeAndShowFixes() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        const document = editor.document;
        const content = document.getText();
        const filePath = document.fileName;

        try {
            // Analyze code
            const issues = await this.analyzeCode(content, filePath);
            
            if (issues.length === 0) {
                vscode.window.showInformationMessage('✅ No issues found! Great code quality.');
                return;
            }

            // Show issues in a quick pick with fix options
            const fixableIssues = issues.filter(issue => issue.auto_fixable);
            const manualIssues = issues.filter(issue => !issue.auto_fixable);

            const quickPickItems = [];

            if (fixableIssues.length > 0) {
                quickPickItems.push({
                    label: `🔧 Fix All (${fixableIssues.length} auto-fixable issues)`,
                    description: 'Apply all automatic fixes',
                    action: 'fixAll',
                    issues: fixableIssues
                });

                // Individual fixable issues
                fixableIssues.forEach(issue => {
                    quickPickItems.push({
                        label: `🔧 Line ${issue.line_number}: ${issue.description}`,
                        description: `Auto-fix: ${issue.rule_id}`,
                        action: 'fixSpecific',
                        issue: issue
                    });
                });
            }

            // Manual issues (for information)
            manualIssues.forEach(issue => {
                quickPickItems.push({
                    label: `👁️ Line ${issue.line_number}: ${issue.description}`,
                    description: `Manual fix needed: ${issue.rule_id}`,
                    action: 'showInfo',
                    issue: issue
                });
            });

            // Show quick pick
            const selected = await vscode.window.showQuickPick(quickPickItems, {
                placeHolder: `Found ${issues.length} issues (${fixableIssues.length} auto-fixable)`,
                canPickMany: false
            });

            if (selected) {
                await this.handleQuickPickAction(selected, document);
            }

        } catch (error) {
            vscode.window.showErrorMessage(`❌ Analysis failed: ${error.message}`);
        }
    }

    /**
     * Handle quick pick action selection
     */
    async handleQuickPickAction(selected, document) {
        switch (selected.action) {
            case 'fixAll':
                await this.fixAllIssues();
                break;
            
            case 'fixSpecific':
                await this.fixSpecificIssue(document, selected.issue);
                break;
            
            case 'showInfo':
                this.showIssueInfo(selected.issue);
                break;
        }
    }

    /**
     * Fix a specific issue
     */
    async fixSpecificIssue(document, issue) {
        // For now, this would apply the same fix-all logic
        // In a more advanced implementation, you could apply fixes selectively
        await this.fixAllIssues();
    }

    /**
     * Show information about a manual issue
     */
    showIssueInfo(issue) {
        const message = `**${issue.rule_id}**\n\n${issue.description}\n\n${issue.suggested_fix || 'Manual fix required'}`;
        vscode.window.showInformationMessage(message, 'Got it');
    }

    /**
     * Show detailed fix results
     */
    showFixDetails(fixResult) {
        const panel = vscode.window.createWebviewPanel(
            'fixResults',
            'Code Review Fix Results',
            vscode.ViewColumn.Beside,
            { enableScripts: true }
        );

        panel.webview.html = this.getFixResultsHtml(fixResult);
    }

    /**
     * Generate HTML for fix results
     */
    getFixResultsHtml(fixResult) {
        const appliedFixes = fixResult.applied_fixes.map(fix => 
            `<li>✅ ${fix.description || 'Applied fix'}</li>`
        ).join('');

        const manualSuggestions = fixResult.manual_suggestions.map(suggestion =>
            `<li>👨‍💻 ${suggestion.title || 'Manual improvement needed'}</li>`
        ).join('');

        return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
                .success { color: #28a745; }
                .manual { color: #ffc107; }
                ul { padding-left: 20px; }
            </style>
        </head>
        <body>
            <h2>🔧 Fix Results</h2>
            
            <h3 class="success">Applied Automatically (${fixResult.applied_fixes.length})</h3>
            <ul>${appliedFixes}</ul>
            
            ${fixResult.manual_suggestions.length > 0 ? `
                <h3 class="manual">Manual Attention Required (${fixResult.manual_suggestions.length})</h3>
                <ul>${manualSuggestions}</ul>
            ` : ''}
            
            <p><strong>Quality Improvement:</strong> ${fixResult.applied_fixes.length} issues resolved</p>
        </body>
        </html>`;
    }

    /**
     * Analyze code using the agent API
     */
    async analyzeCode(content, filePath) {
        const response = await axios.post(`${this.agentUrl}/analyze`, {
            content: content,
            file_path: filePath
        });

        if (response.data.success) {
            return response.data.issues;
        } else {
            throw new Error(response.data.error || 'Analysis failed');
        }
    }

    /**
     * Apply fixes using the agent API
     */
    async applyFixes(content, filePath) {
        const response = await axios.post(`${this.agentUrl}/fix`, {
            content: content,
            file_path: filePath
        });

        if (response.data.success) {
            return response.data;
        } else {
            throw new Error(response.data.error || 'Fix failed');
        }
    }
}

/**
 * Extension activation function
 */
function activate(context) {
    const fixProvider = new CodeReviewFixProvider();
    const disposables = fixProvider.register();
    
    context.subscriptions.push(...disposables);
    
    console.log('TypeScript Code Reviewer extension activated with one-click fixes!');
}

/**
 * Extension deactivation function
 */
function deactivate() {
    console.log('TypeScript Code Reviewer extension deactivated');
}

module.exports = {
    activate,
    deactivate
};
