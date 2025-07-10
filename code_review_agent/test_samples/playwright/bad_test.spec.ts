// This Playwright test file contains intentional issues for testing

import { test, expect } from '@playwright/test';

test('login test', async ({ page }) => {  // Poor test name
    // Console statements that should be flagged by our custom rule
    console.log('Starting login test');
    console.warn('This is a warning message');
    console.error('This is an error message for debugging');

    // Hard wait instead of explicit wait
    await page.waitForTimeout(5000);

    // Direct page interactions instead of Page Object Model
    await page.goto('https://example.com/login');
    console.info('Navigated to login page');

    await page.click('#username');  // CSS selector instead of semantic locator
    await page.fill('#username', 'testuser');
    console.debug('Filled username field');

    await page.click('.password-field');  // CSS class selector
    await page.fill('.password-field', 'password123');
    await page.click('//button[@type="submit"]');  // XPath locator

    // Generic assertion instead of Playwright assertion
    assert(await page.isVisible('#dashboard'));
    console.log('Login completed successfully');

    // Another hard wait
    await page.waitForTimeout(2000);

    // Direct page interaction
    await page.click('.logout-btn');
});

test('user profile', async ({ page }) => {  // Test depends on previous test state
    // No setup - assumes user is already logged in
    await page.goto('https://example.com/profile');
    
    // Complex locator that should be stored in variable
    await page.click('div.user-menu > ul.dropdown-menu > li:nth-child(3) > a.profile-link');
    
    // Boolean assertion that could be more specific
    expect(await page.locator('#profile-form').isVisible()).toBe(true);
    
    // No error handling
    await page.fill('#email', 'newemail@test.com');
    await page.click('#save-button');
});

// Test without proper isolation
test.beforeAll(async ({ page }) => {
    // Shared login state - bad for test isolation
    await page.goto('https://example.com/login');
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'password123');
    await page.click('#login-btn');
});

// Using browser.newPage() instead of context
test('performance test', async ({ browser }) => {
    const page = await browser.newPage();  // Should use context
    
    await page.goto('https://example.com');
    
    // No screenshot on failure setup
    // No video recording setup
    
    await page.close();
});
