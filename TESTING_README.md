# Automated Testing Overview for MealPlan Pal

## Test Files and Locations

- `tests.py` (root): Django unit/integration tests for models and views
  - Location: `mealplan_pal/tests.py`
  - Covers: PantryItem model, Recipe views (dashboard, create)
- `playwright_tests/test_user_flows.spec.js`: Playwright end-to-end browser tests
  - Location: `mealplan_pal/playwright_tests/test_user_flows.spec.js`
  - Covers: User signup, login, add pantry item, create recipe

## How They Work

### Django Tests (`tests.py`)
- Use Django’s `TestCase` to test backend logic
- Run with: `python manage.py test`
- Example: Checks PantryItem creation, Recipe dashboard access, Recipe creation

### Playwright Tests (`playwright_tests/test_user_flows.spec.js`)
- Use Playwright to simulate real user actions in the browser
- Run with: `npx playwright test` (after installing Playwright)
- Example: Signs up a user, logs in, adds a pantry item, creates a recipe, and checks UI

## How to Run

1. **Django tests:**
   ```bash
   python manage.py test
   ```
2. **Playwright tests:**
   ```bash
   npm install -D @playwright/test
   npx playwright install
   npx playwright test
   ```

## Notes
- No changes are made to your main website code—tests are separate.
- You can add more tests for additional features as needed.
- See each test file for details and expand as your project grows.
