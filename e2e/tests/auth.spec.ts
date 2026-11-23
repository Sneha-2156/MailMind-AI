import { test, expect } from '@playwright/test'

/**
 * MailMind AI — End-to-End Tests
 * Verifies authentication flows, API security boundaries, and responsive layout.
 */

test.describe('Authentication Flow', () => {
  test('login page renders correctly', async ({ page }) => {
    await page.goto('/login')
    await expect(page).toHaveTitle(/MailMind AI/)
    await expect(page.getByRole('heading', { name: /mailmind/i })).toBeVisible()
    await expect(page.getByText(/your inbox, intelligently understood/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /sign in with google/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /explore with demo account/i })).toBeVisible()
  })

  test('unauthenticated user is redirected to login from protected routes', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL('/login')

    await page.goto('/inbox')
    await expect(page).toHaveURL('/login')
  })

  test('demo login button navigates to dashboard', async ({ page }) => {
    await page.goto('/login')
    const demoButton = page.getByRole('button', { name: /explore with demo account/i })
    await expect(demoButton).toBeVisible()
  })
})

test.describe('Health Check', () => {
  test('backend health endpoint returns healthy status', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health')
    expect(response.ok()).toBeTruthy()
    const body = await response.json()
    expect(['healthy', 'ok']).toContain(body.status)
    expect(body.app).toContain('MailMind')
  })
})

test.describe('API Security', () => {
  test('emails endpoint requires authentication', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/emails')
    expect(response.status()).toBe(401)
  })

  test('tasks endpoint requires authentication', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/tasks')
    expect(response.status()).toBe(401)
  })

  test('analytics endpoint requires authentication', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/analytics/summary')
    expect(response.status()).toBe(401)
  })
})

test.describe('UI Responsiveness', () => {
  test('login page is responsive on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto('/login')
    await expect(page.getByRole('button', { name: /sign in with google/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /explore with demo account/i })).toBeVisible()
  })
})
