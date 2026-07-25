# E2E Tests

End-to-end tests using Playwright.

## Setup

```bash
npm install
npx playwright install
```

## Running Tests

```bash
npx playwright test
npx playwright test --ui
```

## Writing Tests

```typescript
import { test, expect } from "@playwright/test";

test("homepage loads", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/SuperDev/);
});
```
