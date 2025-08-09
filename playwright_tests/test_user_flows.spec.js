const { test, expect } = require('@playwright/test');

test('User can sign up, login, and add pantry item', async ({ page }) => {
  await page.goto('http://localhost:8000/accounts/signup/');
  await page.fill('input[name="username"]', 'testuser2');
  await page.fill('input[name="email"]', 'testuser2@example.com');
  await page.fill('input[name="password1"]', 'testpass1234');
  await page.fill('input[name="password2"]', 'testpass1234');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/dashboard/);

  await page.goto('http://localhost:8000/pantry/dashboard/');
  await page.click('text=Add Pantry Item');
  await page.fill('input[name="ingredient"]', 'Carrot');
  await page.fill('input[name="amount"]', '3');
  await page.click('button[type="submit"]');
  await expect(page.locator('.card-title')).toContainText('Carrot');
});

test('User can create a recipe', async ({ page }) => {
  await page.goto('http://localhost:8000/accounts/login/');
  await page.fill('input[name="login"]', 'testuser2');
  await page.fill('input[name="password"]', 'testpass1234');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/dashboard/);

  await page.goto('http://localhost:8000/recipes/create/');
  await page.fill('input[name="title"]', 'Playwright Recipe');
  await page.fill('textarea[name="description"]', 'A test recipe created by Playwright.');
  await page.fill('input[name="calories"]', '250');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/recipes/);
  await expect(page.locator('.card-title')).toContainText('Playwright Recipe');
});
