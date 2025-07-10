import { test, expect } from '@playwright/test';

test('login test', async ({ page }) => {
    console.log('Starting login test');
    console.warn('This is a warning message');
    console.error('This is an error message for debugging');
    
    await page.goto('https://example.com/login');
    console.info('Navigated to login page');
    
    await page.click('#username');
    await page.fill('#username', 'testuser');
    console.debug('Filled username field');
    
    expect(page).toHaveTitle('Example');
});