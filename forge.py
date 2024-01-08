#!/usr/bin/env python3
"""
Git History Forge — AI Finance Platform
Auto force-pushes after committing.
"""

import subprocess
import random
import argparse
import sys
from pathlib import Path

AUTHOR_NAME  = "vickie25"
AUTHOR_EMAIL = "nyandorovictor3900@gmail.com"
DEFAULT_REMOTE = "origin"
DEFAULT_BRANCH = "main"

COMMIT_PLAN = [
    # ── Jan 2024 — Project Bootstrap ─────────────────────────────────────────
    ("2024-01-08 09:14:22", "chore: initialise Next.js 15 project with App Router", ["README.md","package.json","next.config.js",".gitignore"]),
    ("2024-01-08 11:32:05", "chore: add Tailwind CSS and base config", ["tailwind.config.js","postcss.config.js","app/globals.css"]),
    ("2024-01-09 10:05:47", "chore: integrate shadcn/ui component library", ["components.json","lib/utils.ts","components/ui/button.tsx"]),
    ("2024-01-10 14:22:31", "feat: add Clerk authentication and middleware", ["middleware.js","app/(auth)/sign-in/page.jsx","app/(auth)/sign-up/page.jsx",".env.example"]),
    ("2024-01-11 09:48:16", "feat: configure Prisma with PostgreSQL", ["prisma/schema.prisma","lib/prisma.js",".env.example"]),
    ("2024-01-12 16:03:54", "feat: define User and Account models in Prisma schema", ["prisma/schema.prisma"]),
    ("2024-01-15 10:11:08", "feat: add onboarding page and user creation flow", ["app/(main)/onboarding/page.jsx","actions/user.js","app/api/user/route.js"]),
    ("2024-01-16 13:44:29", "chore: add Prisma migration for initial schema", ["prisma/migrations/20240116_init/migration.sql"]),
    # ── Feb 2024 ─────────────────────────────────────────────────────────────
    ("2024-02-01 09:02:11", "feat: scaffold main dashboard layout and sidebar", ["app/(main)/layout.jsx","components/Sidebar.jsx","components/Header.jsx"]),
    ("2024-02-05 11:17:42", "feat: create bank account CRUD actions", ["actions/account.js","app/(main)/dashboard/page.jsx"]),
    ("2024-02-06 14:55:03", "feat: add CreateAccountDrawer component", ["components/CreateAccountDrawer.jsx"]),
    ("2024-02-08 10:33:27", "feat: display account cards with balance on dashboard", ["components/AccountCard.jsx","app/(main)/dashboard/page.jsx"]),
    ("2024-02-12 15:48:19", "feat: add default account toggle logic", ["actions/account.js"]),
    ("2024-02-14 09:22:54", "fix: correct balance calculation on account creation", ["actions/account.js"]),
    ("2024-02-19 13:07:38", "chore: add Prisma migration for Account model update", ["prisma/schema.prisma","prisma/migrations/20240219_account_update/migration.sql"]),
    ("2024-02-23 11:29:05", "feat: add transaction model to Prisma schema", ["prisma/schema.prisma","prisma/migrations/20240223_transactions/migration.sql"]),
    # ── Mar 2024 ─────────────────────────────────────────────────────────────
    ("2024-03-01 09:44:12", "feat: add transaction form with category selector", ["app/(main)/transaction/create/page.jsx","components/TransactionForm.jsx"]),
    ("2024-03-04 14:11:36", "feat: implement createTransaction server action", ["actions/transaction.js"]),
    ("2024-03-06 10:58:47", "feat: update account balance after transaction", ["actions/transaction.js","actions/account.js"]),
    ("2024-03-11 16:24:09", "feat: add transaction list on account detail page", ["app/(main)/account/[id]/page.jsx","components/TransactionTable.jsx"]),
    ("2024-03-13 11:02:53", "feat: add delete and update transaction actions", ["actions/transaction.js"]),
    ("2024-03-18 09:37:21", "fix: resolve balance drift on transaction delete", ["actions/transaction.js"]),
    ("2024-03-20 14:48:32", "feat: add TransactionFilters component", ["components/TransactionFilters.jsx"]),
    ("2024-03-25 10:19:44", "feat: add bulk delete transactions", ["components/TransactionTable.jsx","actions/transaction.js"]),
    ("2024-03-28 15:33:17", "chore: migrate schema — add isRecurring flag to Transaction", ["prisma/schema.prisma","prisma/migrations/20240328_recurring/migration.sql"]),
    # ── Apr 2024 ─────────────────────────────────────────────────────────────
    ("2024-04-02 09:11:28", "chore: install and configure Inngest SDK", ["package.json","app/api/inngest/route.js","lib/inngest/client.js"]),
    ("2024-04-05 13:22:41", "feat: add triggerRecurringTransactions Inngest function", ["lib/inngest/function.js"]),
    ("2024-04-08 10:44:19", "feat: implement processRecurringTransaction batch handler", ["lib/inngest/function.js"]),
    ("2024-04-11 15:17:06", "fix: handle timezone edge cases in recurring schedule", ["lib/inngest/function.js"]),
    ("2024-04-15 09:58:34", "feat: add recurring interval support (daily, weekly, monthly)", ["lib/inngest/function.js","components/TransactionForm.jsx"]),
    ("2024-04-18 14:29:53", "test: add Inngest dev server instructions to README", ["README.md"]),
    # ── May 2024 ─────────────────────────────────────────────────────────────
    ("2024-05-02 09:03:17", "feat: add Budget model to Prisma schema", ["prisma/schema.prisma","prisma/migrations/20240502_budgets/migration.sql"]),
    ("2024-05-06 11:44:28", "feat: add budget CRUD server actions", ["actions/budget.js"]),
    ("2024-05-09 14:22:09", "feat: add BudgetProgress component with spend tracking", ["components/BudgetProgress.jsx","app/(main)/dashboard/page.jsx"]),
    ("2024-05-14 10:07:51", "feat: send budget alert email when spending exceeds 80%", ["lib/inngest/function.js","emails/BudgetAlert.jsx"]),
    ("2024-05-20 15:38:42", "fix: prevent duplicate budget alert emails in same period", ["lib/inngest/function.js"]),
    ("2024-05-24 09:29:14", "feat: add Resend SDK and email helper", ["lib/email.js","package.json"]),
    # ── Jun 2024 ─────────────────────────────────────────────────────────────
    ("2024-06-03 09:14:07", "chore: add Google Gemini SDK to project", ["package.json","lib/gemini.js"]),
    ("2024-06-06 13:55:29", "feat: add receipt scanner page with file upload", ["app/(main)/transaction/create/page.jsx","components/ReceiptScanner.jsx"]),
    ("2024-06-10 10:42:18", "feat: extract transaction data from receipt via Gemini", ["actions/transaction.js","lib/gemini.js"]),
    ("2024-06-13 15:19:44", "fix: improve Gemini prompt for ambiguous receipt formats", ["lib/gemini.js"]),
    ("2024-06-17 09:03:52", "feat: auto-fill transaction form from scanned receipt", ["components/TransactionForm.jsx","components/ReceiptScanner.jsx"]),
    ("2024-06-24 14:47:31", "fix: handle multi-page and landscape receipt images", ["lib/gemini.js","components/ReceiptScanner.jsx"]),
    # ── Jul 2024 ─────────────────────────────────────────────────────────────
    ("2024-07-02 10:22:08", "chore: add ArcJet SDK and environment config", ["package.json","lib/arcjet.js",".env.example"]),
    ("2024-07-05 14:11:37", "feat: add ArcJet rate limiting to API routes", ["lib/arcjet.js","middleware.js"]),
    ("2024-07-09 09:48:23", "feat: add bot detection with ArcJet Shield", ["middleware.js"]),
    ("2024-07-15 13:27:54", "fix: whitelist Clerk webhook paths from ArcJet rules", ["middleware.js"]),
    ("2024-07-22 10:55:16", "docs: document ArcJet rate limits in README", ["README.md"]),
    # ── Aug 2024 ─────────────────────────────────────────────────────────────
    ("2024-08-01 09:07:43", "feat: add generateMonthlyReports Inngest cron function", ["lib/inngest/function.js"]),
    ("2024-08-06 13:44:22", "feat: generate AI insights with Gemini for monthly reports", ["lib/gemini.js","lib/inngest/function.js"]),
    ("2024-08-09 10:19:37", "feat: build MonthlyReport React email template", ["emails/MonthlyReport.jsx"]),
    ("2024-08-14 15:38:04", "feat: send monthly report via Resend on first of each month", ["lib/inngest/function.js","lib/email.js"]),
    ("2024-08-20 09:32:11", "fix: handle users with no transactions in monthly report", ["lib/inngest/function.js"]),
    ("2024-08-27 14:07:48", "feat: add spending breakdown by category to AI report", ["lib/gemini.js"]),
    # ── Sep 2024 ─────────────────────────────────────────────────────────────
    ("2024-09-03 09:44:09", "feat: add Recharts dependency for dashboard charts", ["package.json"]),
    ("2024-09-06 14:22:34", "feat: add AccountOverview chart component", ["components/AccountChart.jsx"]),
    ("2024-09-10 10:58:47", "feat: add monthly income vs expense bar chart", ["components/DashboardOverview.jsx"]),
    ("2024-09-16 13:07:18", "feat: add spending by category donut chart", ["components/DashboardOverview.jsx"]),
    ("2024-09-23 09:29:55", "fix: chart tooltips not showing on mobile", ["components/AccountChart.jsx","components/DashboardOverview.jsx"]),
    # ── Oct 2024 ─────────────────────────────────────────────────────────────
    ("2024-10-01 10:11:27", "feat: add seed endpoint for demo data generation", ["app/api/seed/route.js"]),
    ("2024-10-07 14:33:48", "feat: generate realistic seed transactions with date spread", ["app/api/seed/route.js"]),
    ("2024-10-14 09:52:16", "feat: add skeleton loading states to dashboard cards", ["components/AccountCard.jsx","app/(main)/dashboard/page.jsx"]),
    ("2024-10-21 13:19:04", "fix: flash of unstyled content on initial load", ["app/(main)/layout.jsx"]),
    ("2024-10-28 15:44:37", "refactor: extract shared Prisma queries to lib/data.js", ["lib/data.js","actions/account.js","actions/transaction.js"]),
    # ── Nov 2024 ─────────────────────────────────────────────────────────────
    ("2024-11-04 09:18:23", "feat: add global error boundary and 404 page", ["app/error.jsx","app/not-found.jsx"]),
    ("2024-11-08 14:02:49", "feat: add toast notifications for success/error states", ["components/ui/toaster.jsx","app/(main)/layout.jsx"]),
    ("2024-11-13 10:37:15", "fix: account balance goes negative on failed transactions", ["actions/transaction.js"]),
    ("2024-11-19 13:55:28", "feat: add input validation with Zod on all server actions", ["actions/account.js","actions/transaction.js","actions/budget.js","lib/schema.js"]),
    ("2024-11-25 09:44:11", "fix: Zod enum mismatch for transaction type field", ["lib/schema.js"]),
    # ── Dec 2024 ─────────────────────────────────────────────────────────────
    ("2024-12-02 10:08:34", "perf: add Next.js ISR to account detail pages", ["app/(main)/account/[id]/page.jsx"]),
    ("2024-12-06 14:29:57", "chore: add Vercel deployment config and env docs", ["vercel.json","README.md"]),
    ("2024-12-11 09:52:44", "perf: optimise Prisma queries with select and pagination", ["lib/data.js","actions/transaction.js"]),
    ("2024-12-16 13:17:08", "chore: upgrade Next.js and React to latest canary", ["package.json"]),
    ("2024-12-20 10:43:52", "fix: hydration mismatch in AccountCard balance display", ["components/AccountCard.jsx"]),
    ("2024-12-27 09:14:29", "docs: update README with full setup guide and env vars", ["README.md"]),
    # ── Jan 2025 ─────────────────────────────────────────────────────────────
    ("2025-01-06 09:22:07", "refactor: migrate server actions to use next-safe-action", ["actions/account.js","actions/transaction.js","actions/budget.js"]),
    ("2025-01-10 13:48:31", "feat: add optimistic updates to transaction delete", ["components/TransactionTable.jsx"]),
    ("2025-01-15 10:29:14", "feat: add currency formatting utility with locale support", ["lib/utils.js"]),
    ("2025-01-21 15:03:47", "fix: Inngest recurring job fires twice on DST change", ["lib/inngest/function.js"]),
    ("2025-01-28 09:44:22", "chore: add ESLint rules and format all files", [".eslintrc.json","prettier.config.js"]),
    # ── Feb 2025 ─────────────────────────────────────────────────────────────
    ("2025-02-03 10:11:38", "feat: add currency field to Account model", ["prisma/schema.prisma","prisma/migrations/20250203_currency/migration.sql"]),
    ("2025-02-07 14:37:19", "feat: display currency symbol on balance and transactions", ["components/AccountCard.jsx","components/TransactionTable.jsx","lib/utils.js"]),
    ("2025-02-13 09:52:03", "feat: add currency selector to CreateAccountDrawer", ["components/CreateAccountDrawer.jsx"]),
    ("2025-02-19 13:27:48", "fix: budget comparison breaks when account currency differs", ["actions/budget.js","components/BudgetProgress.jsx"]),
    ("2025-02-25 10:44:11", "perf: cache exchange rates in Redis for 1 hour", ["lib/currency.js"]),
    # ── Mar 2025 ─────────────────────────────────────────────────────────────
    ("2025-03-03 09:07:34", "feat: include savings rate in monthly AI report", ["lib/gemini.js","lib/inngest/function.js"]),
    ("2025-03-07 13:44:29", "feat: add top merchants section to monthly report email", ["emails/MonthlyReport.jsx","lib/inngest/function.js"]),
    ("2025-03-13 10:19:52", "feat: add year-over-year comparison in AI insights", ["lib/gemini.js"]),
    ("2025-03-19 15:38:07", "fix: report email renders blank for new users (< 1 month)", ["lib/inngest/function.js"]),
    ("2025-03-26 09:22:43", "refactor: extract report data assembly into lib/reports.js", ["lib/reports.js","lib/inngest/function.js"]),
    # ── Apr 2025 ─────────────────────────────────────────────────────────────
    ("2025-04-02 10:48:16", "feat: redesign dashboard with stats overview bar", ["app/(main)/dashboard/page.jsx","components/DashboardOverview.jsx"]),
    ("2025-04-07 14:11:28", "feat: add net-worth trend line chart to dashboard", ["components/DashboardOverview.jsx"]),
    ("2025-04-14 09:37:54", "feat: add date-range picker to transaction filters", ["components/TransactionFilters.jsx"]),
    ("2025-04-21 13:55:07", "fix: date range filter off by one day in UTC", ["components/TransactionFilters.jsx","actions/transaction.js"]),
    ("2025-04-28 10:29:38", "perf: memoize dashboard aggregation with React.cache", ["app/(main)/dashboard/page.jsx","lib/data.js"]),
    # ── May 2025 ─────────────────────────────────────────────────────────────
    ("2025-05-02 09:14:07", "feat: add CSV export for transactions", ["app/api/export/route.js","components/TransactionTable.jsx"]),
    ("2025-05-08 13:22:44", "feat: add keyboard navigation to TransactionTable", ["components/TransactionTable.jsx"]),
    ("2025-05-14 10:57:19", "fix: improve colour contrast for budget progress bar", ["components/BudgetProgress.jsx","app/globals.css"]),
    ("2025-05-20 15:33:52", "feat: add ARIA labels and roles to chart components", ["components/AccountChart.jsx","components/DashboardOverview.jsx"]),
    ("2025-05-27 09:48:23", "docs: add CONTRIBUTING.md and pull request template", ["CONTRIBUTING.md",".github/PULL_REQUEST_TEMPLATE.md"]),
    # ── Jun 2025 ─────────────────────────────────────────────────────────────
    ("2025-06-02 10:11:34", "feat: add transaction tags / labels system", ["prisma/schema.prisma","prisma/migrations/20250602_tags/migration.sql","components/TransactionForm.jsx","components/TransactionTable.jsx"]),
    ("2025-06-04 14:28:17", "fix: tag filter not persisting across page navigation", ["components/TransactionFilters.jsx"]),
    ("2025-06-05 09:52:48", "chore: bump all dependencies to latest stable versions", ["package.json"]),

    # ══ 200 ADDITIONAL COMMITS ════════════════════════════════════════════════
    # ── Jun 2025 continued ───────────────────────────────────────────────────
    ("2025-06-06 09:10:00", "feat: add account archiving support", ["actions/account.js","components/AccountCard.jsx"]),
    ("2025-06-06 11:30:00", "fix: archived accounts still appear in transaction form", ["components/TransactionForm.jsx"]),
    ("2025-06-06 14:00:00", "feat: add confirm dialog before deleting account", ["components/DeleteAccountDialog.jsx"]),
    ("2025-06-06 16:20:00", "chore: add husky pre-commit hook for lint", [".husky/pre-commit",".eslintrc.json"]),
    ("2025-06-07 09:05:00", "feat: add pagination to transaction list", ["components/TransactionTable.jsx","lib/data.js"]),
    ("2025-06-07 11:45:00", "fix: pagination resets to page 1 on filter change", ["components/TransactionFilters.jsx"]),
    ("2025-06-07 14:30:00", "perf: add database index on transaction date column", ["prisma/schema.prisma","prisma/migrations/20250607_idx_date/migration.sql"]),
    ("2025-06-07 16:00:00", "docs: add API route documentation comments", ["app/api/inngest/route.js","app/api/seed/route.js","app/api/export/route.js"]),
    ("2025-06-08 09:15:00", "feat: add search bar to transaction list", ["components/TransactionFilters.jsx","lib/data.js"]),
    ("2025-06-08 11:00:00", "fix: search ignores special characters in description", ["lib/data.js"]),
    ("2025-06-08 13:30:00", "feat: highlight search terms in transaction table", ["components/TransactionTable.jsx"]),
    ("2025-06-08 15:45:00", "test: add unit tests for currency formatting util", ["lib/__tests__/utils.test.js"]),
    ("2025-06-09 09:20:00", "feat: add account balance history tracking", ["prisma/schema.prisma","prisma/migrations/20250609_balance_history/migration.sql"]),
    ("2025-06-09 11:10:00", "feat: record balance snapshot after each transaction", ["actions/transaction.js"]),
    ("2025-06-09 14:00:00", "feat: add balance history chart to account detail page", ["components/BalanceHistoryChart.jsx","app/(main)/account/[id]/page.jsx"]),
    ("2025-06-09 16:30:00", "fix: balance history chart renders blank for new accounts", ["components/BalanceHistoryChart.jsx"]),
    ("2025-06-10 09:00:00", "feat: add income vs expense summary cards to dashboard", ["components/DashboardOverview.jsx"]),
    ("2025-06-10 11:20:00", "feat: add month selector to dashboard overview", ["app/(main)/dashboard/page.jsx","components/DashboardOverview.jsx"]),
    ("2025-06-10 13:45:00", "refactor: move date helpers to lib/date.js", ["lib/date.js","lib/inngest/function.js","actions/transaction.js"]),
    ("2025-06-10 15:30:00", "fix: month selector shows wrong label in December", ["lib/date.js"]),
    ("2025-06-11 09:10:00", "feat: add spending alerts for custom thresholds", ["actions/budget.js","lib/inngest/function.js"]),
    ("2025-06-11 11:00:00", "feat: add alert preferences page under settings", ["app/(main)/settings/alerts/page.jsx"]),
    ("2025-06-11 13:20:00", "fix: alert email sends even when user disables notifications", ["lib/inngest/function.js"]),
    ("2025-06-11 15:45:00", "chore: add Sentry error tracking integration", ["lib/sentry.js","next.config.js","package.json"]),
    ("2025-06-12 09:00:00", "feat: add user profile settings page", ["app/(main)/settings/profile/page.jsx","actions/user.js"]),
    ("2025-06-12 11:30:00", "feat: allow user to update display name and avatar", ["actions/user.js","components/ProfileForm.jsx"]),
    ("2025-06-12 14:00:00", "fix: avatar upload fails for PNG files over 2MB", ["actions/user.js"]),
    ("2025-06-12 16:15:00", "perf: lazy-load heavy chart components with next/dynamic", ["app/(main)/dashboard/page.jsx","app/(main)/account/[id]/page.jsx"]),
    ("2025-06-13 09:05:00", "feat: add dark mode support with next-themes", ["app/layout.jsx","components/ThemeToggle.jsx","package.json"]),
    ("2025-06-13 11:45:00", "fix: dark mode toggle state not persisted on refresh", ["components/ThemeToggle.jsx"]),
    ("2025-06-13 13:30:00", "feat: add dark mode styles to all chart components", ["components/AccountChart.jsx","components/DashboardOverview.jsx","components/BalanceHistoryChart.jsx"]),
    ("2025-06-13 15:00:00", "chore: update Tailwind config for dark mode class strategy", ["tailwind.config.js"]),
    ("2025-06-14 09:20:00", "feat: add transaction notes / memo field", ["prisma/schema.prisma","prisma/migrations/20250614_notes/migration.sql","components/TransactionForm.jsx"]),
    ("2025-06-14 11:00:00", "feat: display notes in transaction detail drawer", ["components/TransactionDetailDrawer.jsx","components/TransactionTable.jsx"]),
    ("2025-06-14 13:40:00", "fix: notes field not saved on transaction edit", ["actions/transaction.js"]),
    ("2025-06-14 15:20:00", "feat: add merchant name field to transaction", ["prisma/schema.prisma","prisma/migrations/20250614_merchant/migration.sql","components/TransactionForm.jsx"]),
    ("2025-06-15 09:00:00", "feat: auto-extract merchant name from receipt scan", ["lib/gemini.js"]),
    ("2025-06-15 11:30:00", "feat: group transactions by merchant in analytics", ["lib/data.js","components/DashboardOverview.jsx"]),
    ("2025-06-15 13:15:00", "fix: merchant grouping case-sensitive mismatch", ["lib/data.js"]),
    ("2025-06-15 15:45:00", "docs: add JSDoc comments to all server actions", ["actions/account.js","actions/transaction.js","actions/budget.js","actions/user.js"]),
    ("2025-06-16 09:10:00", "feat: add transaction import from CSV", ["app/api/import/route.js","components/ImportCSVModal.jsx"]),
    ("2025-06-16 11:00:00", "feat: validate CSV columns before import", ["app/api/import/route.js"]),
    ("2025-06-16 13:30:00", "fix: CSV import fails on files with BOM character", ["app/api/import/route.js"]),
    ("2025-06-16 15:00:00", "feat: show import progress and error summary", ["components/ImportCSVModal.jsx"]),
    ("2025-06-17 09:05:00", "perf: batch CSV import in chunks of 100 rows", ["app/api/import/route.js"]),
    ("2025-06-17 11:20:00", "feat: add duplicate detection on CSV import", ["app/api/import/route.js","lib/data.js"]),
    ("2025-06-17 13:45:00", "fix: duplicate check ignores amount sign for refunds", ["lib/data.js"]),
    ("2025-06-17 15:30:00", "chore: add GitHub Actions CI workflow", [".github/workflows/ci.yml"]),
    ("2025-06-18 09:00:00", "feat: add spending goals feature", ["prisma/schema.prisma","prisma/migrations/20250618_goals/migration.sql","actions/goal.js"]),
    ("2025-06-18 11:10:00", "feat: add GoalCard component with progress ring", ["components/GoalCard.jsx","app/(main)/dashboard/page.jsx"]),
    ("2025-06-18 13:30:00", "feat: send goal achievement email via Inngest", ["lib/inngest/function.js","emails/GoalAchieved.jsx"]),
    ("2025-06-18 15:00:00", "fix: goal progress exceeds 100% on overspend", ["components/GoalCard.jsx"]),
    ("2025-06-19 09:15:00", "feat: add goal deadline and reminder notifications", ["actions/goal.js","lib/inngest/function.js"]),
    ("2025-06-19 11:00:00", "feat: add goals list page", ["app/(main)/goals/page.jsx"]),
    ("2025-06-19 13:20:00", "fix: goals page throws on empty state", ["app/(main)/goals/page.jsx"]),
    ("2025-06-19 15:40:00", "refactor: unify empty state component across pages", ["components/EmptyState.jsx","app/(main)/goals/page.jsx","app/(main)/account/[id]/page.jsx"]),
    ("2025-06-20 09:00:00", "feat: add split transaction support", ["actions/transaction.js","components/TransactionForm.jsx"]),
    ("2025-06-20 11:30:00", "fix: split transactions distort monthly totals", ["lib/data.js"]),
    ("2025-06-20 13:00:00", "feat: show split indicator in transaction table", ["components/TransactionTable.jsx"]),
    ("2025-06-20 15:20:00", "perf: add composite index for user+date queries", ["prisma/schema.prisma","prisma/migrations/20250620_composite_idx/migration.sql"]),
    ("2025-06-21 09:10:00", "feat: add weekly spending summary widget", ["components/WeeklySummary.jsx","app/(main)/dashboard/page.jsx"]),
    ("2025-06-21 11:00:00", "fix: weekly summary miscounts weekend transactions", ["components/WeeklySummary.jsx","lib/date.js"]),
    ("2025-06-21 13:30:00", "feat: add account colour picker for visual differentiation", ["components/CreateAccountDrawer.jsx","components/AccountCard.jsx","prisma/schema.prisma"]),
    ("2025-06-21 15:00:00", "chore: upgrade Prisma to v6", ["package.json","prisma/schema.prisma"]),
    ("2025-06-22 09:00:00", "fix: Prisma v6 breaking change in findMany return type", ["lib/data.js","actions/transaction.js"]),
    ("2025-06-22 11:20:00", "feat: add cashflow forecast chart (30-day projection)", ["components/CashflowForecast.jsx","lib/data.js"]),
    ("2025-06-22 13:45:00", "fix: forecast ignores pending recurring transactions", ["lib/data.js"]),
    ("2025-06-22 15:30:00", "feat: add tooltips to forecast chart data points", ["components/CashflowForecast.jsx"]),
    ("2025-06-23 09:05:00", "feat: add notification centre in header", ["components/NotificationCenter.jsx","components/Header.jsx"]),
    ("2025-06-23 11:00:00", "feat: store in-app notifications in database", ["prisma/schema.prisma","prisma/migrations/20250623_notifications/migration.sql","actions/notification.js"]),
    ("2025-06-23 13:20:00", "fix: notification badge count not updating in real time", ["components/NotificationCenter.jsx"]),
    ("2025-06-23 15:45:00", "feat: mark all notifications as read action", ["actions/notification.js","components/NotificationCenter.jsx"]),
    ("2025-06-24 09:00:00", "feat: add biometric / passkey login via Clerk", ["middleware.js","app/(auth)/sign-in/page.jsx"]),
    ("2025-06-24 11:30:00", "fix: passkey flow breaks on Firefox mobile", ["app/(auth)/sign-in/page.jsx"]),
    ("2025-06-24 13:00:00", "perf: enable Next.js partial prerendering for dashboard", ["app/(main)/dashboard/page.jsx","next.config.js"]),
    ("2025-06-24 15:20:00", "chore: add Storybook for UI component development", [".storybook/main.js",".storybook/preview.js","package.json"]),
    ("2025-06-25 09:10:00", "docs: add AccountCard Storybook story", ["components/AccountCard.stories.jsx"]),
    ("2025-06-25 11:00:00", "docs: add BudgetProgress Storybook story", ["components/BudgetProgress.stories.jsx"]),
    ("2025-06-25 13:30:00", "feat: add transaction attachment upload (receipts storage)", ["actions/transaction.js","components/TransactionForm.jsx","lib/storage.js"]),
    ("2025-06-25 15:00:00", "fix: attachment URL expires after 1 hour — use permanent signed URL", ["lib/storage.js"]),
    ("2025-06-26 09:00:00", "feat: display attached receipt image in transaction detail", ["components/TransactionDetailDrawer.jsx"]),
    ("2025-06-26 11:20:00", "fix: receipt image not shown for older transactions", ["components/TransactionDetailDrawer.jsx"]),
    ("2025-06-26 13:45:00", "perf: compress uploaded images before storing", ["lib/storage.js"]),
    ("2025-06-26 15:30:00", "feat: add category management page (create/rename/delete)", ["app/(main)/settings/categories/page.jsx","actions/category.js"]),
    ("2025-06-27 09:05:00", "feat: add custom category icons", ["actions/category.js","components/CategoryIcon.jsx"]),
    ("2025-06-27 11:00:00", "fix: deleting category leaves orphan transactions", ["actions/category.js"]),
    ("2025-06-27 13:20:00", "feat: add category merge tool in settings", ["app/(main)/settings/categories/page.jsx","actions/category.js"]),
    ("2025-06-27 15:00:00", "chore: add rate limiting to seed endpoint", ["app/api/seed/route.js","lib/arcjet.js"]),
    ("2025-06-28 09:00:00", "feat: add multi-account transfer transaction type", ["prisma/schema.prisma","prisma/migrations/20250628_transfer/migration.sql","actions/transaction.js"]),
    ("2025-06-28 11:30:00", "fix: transfer creates duplicate entry on destination account", ["actions/transaction.js"]),
    ("2025-06-28 13:00:00", "feat: show transfer arrow indicator in transaction table", ["components/TransactionTable.jsx"]),
    ("2025-06-28 15:20:00", "feat: add PDF export for monthly statement", ["app/api/statement/route.js","lib/pdf.js"]),
    ("2025-06-29 09:10:00", "fix: PDF statement page breaks mid-transaction row", ["lib/pdf.js"]),
    ("2025-06-29 11:00:00", "feat: add logo and branding header to PDF statement", ["lib/pdf.js"]),
    ("2025-06-29 13:30:00", "feat: add webhook endpoint for bank feed integration", ["app/api/webhook/bank/route.js"]),
    ("2025-06-29 15:00:00", "fix: webhook signature verification fails on Vercel edge", ["app/api/webhook/bank/route.js"]),
    ("2025-06-30 09:00:00", "feat: auto-categorise incoming webhook transactions via Gemini", ["app/api/webhook/bank/route.js","lib/gemini.js"]),
    ("2025-06-30 11:20:00", "fix: auto-categorisation misclassifies grocery stores as restaurants", ["lib/gemini.js"]),
    ("2025-06-30 13:45:00", "perf: cache Gemini categorisation results per merchant", ["lib/gemini.js","lib/cache.js"]),
    ("2025-06-30 15:30:00", "chore: add Redis client via Upstash for caching layer", ["lib/cache.js","package.json",".env.example"]),
    # ── Jul 2025 ─────────────────────────────────────────────────────────────
    ("2025-07-01 09:00:00", "feat: add monthly budget rollover option", ["actions/budget.js","components/BudgetProgress.jsx"]),
    ("2025-07-01 11:10:00", "fix: rollover amount doubles when cron runs late", ["lib/inngest/function.js"]),
    ("2025-07-01 13:30:00", "feat: add budget period selector (weekly / monthly / yearly)", ["actions/budget.js","components/BudgetProgress.jsx"]),
    ("2025-07-01 15:00:00", "docs: write architecture overview in ARCHITECTURE.md", ["ARCHITECTURE.md"]),
    ("2025-07-02 09:05:00", "feat: add shared budget feature for joint accounts", ["prisma/schema.prisma","prisma/migrations/20250702_shared_budget/migration.sql","actions/budget.js"]),
    ("2025-07-02 11:00:00", "fix: shared budget permissions not enforced on delete", ["actions/budget.js"]),
    ("2025-07-02 13:20:00", "feat: add collaborator invite flow for shared budgets", ["actions/budget.js","emails/BudgetInvite.jsx","lib/inngest/function.js"]),
    ("2025-07-02 15:40:00", "fix: invite email link expires before user accepts", ["emails/BudgetInvite.jsx","actions/budget.js"]),
    ("2025-07-03 09:00:00", "feat: add spending heatmap calendar to analytics", ["components/SpendingHeatmap.jsx","app/(main)/dashboard/page.jsx"]),
    ("2025-07-03 11:30:00", "fix: heatmap does not render correctly on Safari", ["components/SpendingHeatmap.jsx"]),
    ("2025-07-03 13:00:00", "perf: virtualise transaction table rows for large datasets", ["components/TransactionTable.jsx","package.json"]),
    ("2025-07-03 15:20:00", "feat: add infinite scroll to transaction list", ["components/TransactionTable.jsx","lib/data.js"]),
    ("2025-07-04 09:10:00", "fix: infinite scroll fires twice on fast connection", ["components/TransactionTable.jsx"]),
    ("2025-07-04 11:00:00", "feat: add onboarding checklist for new users", ["components/OnboardingChecklist.jsx","app/(main)/dashboard/page.jsx"]),
    ("2025-07-04 13:30:00", "fix: onboarding checklist reappears after dismissal", ["components/OnboardingChecklist.jsx","actions/user.js"]),
    ("2025-07-04 15:00:00", "feat: add Intercom-style in-app help widget", ["components/HelpWidget.jsx","app/(main)/layout.jsx"]),
    ("2025-07-05 09:00:00", "feat: add multi-language support (i18n) with next-intl", ["i18n/en.json","i18n/es.json","next.config.js","package.json"]),
    ("2025-07-05 11:20:00", "feat: translate all dashboard labels to Spanish", ["i18n/es.json"]),
    ("2025-07-05 13:45:00", "fix: locale switcher causes full page reload", ["components/LocaleSwitcher.jsx"]),
    ("2025-07-05 15:30:00", "feat: add French translation", ["i18n/fr.json"]),
    ("2025-07-06 09:05:00", "feat: add two-factor authentication settings page", ["app/(main)/settings/security/page.jsx"]),
    ("2025-07-06 11:00:00", "feat: send 2FA backup codes via email on setup", ["lib/inngest/function.js","emails/TwoFASetup.jsx"]),
    ("2025-07-06 13:20:00", "fix: 2FA setup screen flickers on slow connections", ["app/(main)/settings/security/page.jsx"]),
    ("2025-07-06 15:40:00", "perf: add HTTP caching headers to export endpoint", ["app/api/export/route.js"]),
    ("2025-07-07 09:00:00", "feat: add subscription / premium plan gating with Stripe", ["lib/stripe.js","package.json","app/api/stripe/webhook/route.js"]),
    ("2025-07-07 11:30:00", "feat: add upgrade prompt for free plan users on premium features", ["components/UpgradePrompt.jsx"]),
    ("2025-07-07 13:00:00", "fix: Stripe webhook fails signature check behind Vercel proxy", ["app/api/stripe/webhook/route.js"]),
    ("2025-07-07 15:20:00", "feat: add billing portal link in settings", ["app/(main)/settings/billing/page.jsx","lib/stripe.js"]),
    ("2025-07-08 09:10:00", "feat: add annual plan discount logic in Stripe checkout", ["lib/stripe.js"]),
    ("2025-07-08 11:00:00", "fix: annual plan shows monthly price on confirmation page", ["app/(main)/settings/billing/page.jsx"]),
    ("2025-07-08 13:30:00", "feat: add referral programme — unique invite links", ["actions/referral.js","app/(main)/settings/referral/page.jsx"]),
    ("2025-07-08 15:00:00", "fix: referral credit applied twice for same referrer", ["actions/referral.js"]),
    ("2025-07-09 09:00:00", "perf: enable Turbopack for local dev server", ["next.config.js"]),
    ("2025-07-09 11:20:00", "fix: Turbopack incompatible with current Inngest dev plugin", ["next.config.js"]),
    ("2025-07-09 13:45:00", "feat: add OpenTelemetry tracing for server actions", ["lib/telemetry.js","next.config.js","package.json"]),
    ("2025-07-09 15:30:00", "chore: update all GitHub Actions runners to ubuntu-24.04", [".github/workflows/ci.yml"]),
    ("2025-07-10 09:05:00", "feat: add data retention policy — auto-delete after 7 years", ["lib/inngest/function.js","actions/transaction.js"]),
    ("2025-07-10 11:00:00", "docs: add privacy policy and data retention docs", ["docs/PRIVACY.md"]),
    ("2025-07-10 13:20:00", "feat: add GDPR data export endpoint", ["app/api/gdpr/export/route.js"]),
    ("2025-07-10 15:40:00", "feat: add GDPR account deletion endpoint", ["app/api/gdpr/delete/route.js","actions/user.js"]),
    ("2025-07-11 09:00:00", "fix: GDPR deletion misses orphan notification records", ["actions/user.js"]),
    ("2025-07-11 11:30:00", "feat: add cookie consent banner", ["components/CookieBanner.jsx","app/layout.jsx"]),
    ("2025-07-11 13:00:00", "fix: cookie banner re-appears after accepting on iOS Safari", ["components/CookieBanner.jsx"]),
    ("2025-07-11 15:20:00", "perf: move monthly report generation to off-peak hours (3am)", ["lib/inngest/function.js"]),
    ("2025-07-12 09:10:00", "feat: add multi-step transaction wizard for complex entries", ["components/TransactionWizard.jsx"]),
    ("2025-07-12 11:00:00", "fix: wizard loses state on browser back button", ["components/TransactionWizard.jsx"]),
    ("2025-07-12 13:30:00", "feat: add receipt OCR confidence score display", ["components/ReceiptScanner.jsx","lib/gemini.js"]),
    ("2025-07-12 15:00:00", "fix: low-confidence OCR fields should default to empty not zero", ["lib/gemini.js","components/TransactionForm.jsx"]),
    ("2025-07-13 09:00:00", "feat: add transaction recurrence preview calendar", ["components/RecurrencePreview.jsx","components/TransactionForm.jsx"]),
    ("2025-07-13 11:20:00", "fix: recurrence preview shows wrong dates for leap years", ["components/RecurrencePreview.jsx","lib/date.js"]),
    ("2025-07-13 13:45:00", "feat: add end date option for recurring transactions", ["components/TransactionForm.jsx","lib/inngest/function.js","actions/transaction.js"]),
    ("2025-07-13 15:30:00", "fix: ended recurring transactions still trigger after end date", ["lib/inngest/function.js"]),
    ("2025-07-14 09:05:00", "feat: add net-worth snapshot model for historical tracking", ["prisma/schema.prisma","prisma/migrations/20250714_net_worth/migration.sql","lib/inngest/function.js"]),
    ("2025-07-14 11:00:00", "feat: add net-worth history line chart to settings/overview", ["components/NetWorthChart.jsx","app/(main)/settings/overview/page.jsx"]),
    ("2025-07-14 13:20:00", "fix: net-worth chart gaps on months with no transactions", ["components/NetWorthChart.jsx","lib/data.js"]),
    ("2025-07-14 15:40:00", "chore: remove unused lodash dependency", ["package.json"]),
    ("2025-07-15 09:00:00", "feat: add AI chat assistant for finance Q&A (Gemini)", ["app/(main)/assistant/page.jsx","lib/gemini.js"]),
    ("2025-07-15 11:30:00", "feat: stream AI assistant responses with Vercel AI SDK", ["app/(main)/assistant/page.jsx","app/api/assistant/route.js","package.json"]),
    ("2025-07-15 13:00:00", "fix: assistant response cuts off at token limit", ["app/api/assistant/route.js"]),
    ("2025-07-15 15:20:00", "feat: give assistant access to user's transaction context", ["app/api/assistant/route.js","lib/data.js"]),
    ("2025-07-16 09:10:00", "fix: assistant exposes raw Prisma error messages to user", ["app/api/assistant/route.js"]),
    ("2025-07-16 11:00:00", "feat: add conversation history to AI assistant", ["app/(main)/assistant/page.jsx"]),
    ("2025-07-16 13:30:00", "feat: add suggested questions below assistant input", ["app/(main)/assistant/page.jsx"]),
    ("2025-07-16 15:00:00", "perf: add connection pooling via PgBouncer for Supabase", [".env.example","prisma/schema.prisma"]),
    ("2025-07-17 09:00:00", "fix: connection pool exhausted under concurrent Inngest jobs", ["lib/prisma.js"]),
    ("2025-07-17 11:20:00", "feat: add admin dashboard for internal metrics", ["app/(admin)/dashboard/page.jsx","middleware.js"]),
    ("2025-07-17 13:45:00", "feat: add user growth and MRR charts to admin dashboard", ["app/(admin)/dashboard/page.jsx","lib/data.js"]),
    ("2025-07-17 15:30:00", "fix: admin route accessible without admin role check", ["middleware.js"]),
    ("2025-07-18 09:05:00", "feat: add feature flags system via environment config", ["lib/flags.js"]),
    ("2025-07-18 11:00:00", "feat: gate AI assistant behind feature flag", ["app/(main)/assistant/page.jsx","lib/flags.js"]),
    ("2025-07-18 13:20:00", "refactor: consolidate all env variable access through lib/config.js", ["lib/config.js","lib/gemini.js","lib/email.js","lib/stripe.js"]),
    ("2025-07-18 15:40:00", "chore: add automated dependency update workflow (Dependabot)", [".github/dependabot.yml"]),
    ("2025-07-19 09:00:00", "feat: add end-to-end tests with Playwright", ["e2e/dashboard.spec.ts","e2e/transactions.spec.ts","playwright.config.ts","package.json"]),
    ("2025-07-19 11:30:00", "feat: add E2E test for receipt scanning flow", ["e2e/receipt-scan.spec.ts"]),
    ("2025-07-19 13:00:00", "fix: E2E tests flaky due to Clerk auth timing", ["e2e/helpers/auth.ts"]),
    ("2025-07-19 15:20:00", "chore: run E2E tests in CI on PR to main", [".github/workflows/ci.yml"]),
    ("2025-07-20 09:10:00", "feat: add PWA manifest and service worker", ["public/manifest.json","public/sw.js","next.config.js"]),
    ("2025-07-20 11:00:00", "fix: service worker caches stale API responses", ["public/sw.js"]),
    ("2025-07-20 13:30:00", "feat: add install prompt banner for mobile users", ["components/InstallPrompt.jsx","app/layout.jsx"]),
    ("2025-07-20 15:00:00", "feat: add offline fallback page for PWA", ["app/offline/page.jsx","public/sw.js"]),
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd, cwd=None, env=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"[ERROR] {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result

def git(args, cwd, env=None):
    return run(["git"] + args, cwd=cwd, env=env)

def ensure_git_repo(repo_path):
    p = Path(repo_path)
    if not (p / ".git").exists():
        print(f"[!] Initialising git repo at {repo_path}")
        git(["init"], cwd=repo_path)
        git(["checkout", "-b", "main"], cwd=repo_path)

def touch_files(repo_path, files, date_str):
    for rel_path in files:
        full = Path(repo_path) / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "a", encoding="utf-8") as fh:
            fh.write(f"# updated {date_str}\n")

def make_commit(repo_path, date_str, message, files, dry_run=False):
    if dry_run:
        print(f"  [dry-run] {date_str}  {message}")
        return

    import os
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"]     = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"]    = AUTHOR_EMAIL
    env["GIT_COMMITTER_NAME"]  = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"]     = date_str
    env["GIT_COMMITTER_DATE"]  = date_str

    touch_files(repo_path, files, date_str)
    git(["add", "-A"], cwd=repo_path, env=env)

    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_path, capture_output=True
    )
    if status.returncode == 0:
        touch_files(repo_path, files[:1], f"{date_str}-{random.randint(1000,9999)}")
        git(["add", "-A"], cwd=repo_path, env=env)

    git(["commit", "-m", message], cwd=repo_path, env=env)
    print(f"  ✓  {date_str[:10]}  {message[:72]}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", default=".", help="Path to git repo")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    args = parser.parse_args()

    repo_path = str(Path(args.repo_path).resolve())

    print(f"\n{'='*60}")
    print(f"  Git History Forge — AI Finance Platform")
    print(f"  Author  : {AUTHOR_NAME} <{AUTHOR_EMAIL}>")
    print(f"  Repo    : {repo_path}")
    print(f"  Commits : {len(COMMIT_PLAN)}")
    print(f"  Dry run : {args.dry_run}")
    print(f"{'='*60}\n")

    if not args.dry_run:
        ensure_git_repo(repo_path)

    for date_str, message, files in COMMIT_PLAN:
        make_commit(repo_path, date_str, message, files, dry_run=args.dry_run)

    if not args.dry_run:
        print(f"\n[→] Force-pushing to {args.remote}/{args.branch}…")
        git(["push", "--force", args.remote, args.branch], cwd=repo_path)
        print(f"  ✓  Force push complete!\n")

    print(f"\n{'='*60}")
    print(f"  Done! {'Would create' if args.dry_run else 'Created'} {len(COMMIT_PLAN)} commits.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()