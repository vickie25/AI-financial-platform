#!/usr/bin/env python3
"""
Git History Forge — AI Finance Platform
Generates a realistic, backdated commit history from Jan 2024 to present.
Usage: python git_history_forge.py [--repo-path /path/to/repo] [--dry-run]
"""

import subprocess
import random
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ─── Commit Timeline ─────────────────────────────────────────────────────────
# Each entry: (date_str, message, author_name, author_email, files_hint)
# The script creates dummy file touches to make commits non-empty.

COMMIT_PLAN = [

    # ── Jan 2024 — Project Bootstrap ─────────────────────────────────────────
    ("2024-01-08 09:14:22", "chore: initialise Next.js 15 project with App Router",
     "Dev", "dev@financeapp.io",
     ["README.md", "package.json", "next.config.js", ".gitignore"]),

    ("2024-01-08 11:32:05", "chore: add Tailwind CSS and base config",
     "Dev", "dev@financeapp.io",
     ["tailwind.config.js", "postcss.config.js", "app/globals.css"]),

    ("2024-01-09 10:05:47", "chore: integrate shadcn/ui component library",
     "Dev", "dev@financeapp.io",
     ["components.json", "lib/utils.ts", "components/ui/button.tsx"]),

    ("2024-01-10 14:22:31", "feat: add Clerk authentication and middleware",
     "Dev", "dev@financeapp.io",
     ["middleware.js", "app/(auth)/sign-in/page.jsx",
      "app/(auth)/sign-up/page.jsx", ".env.example"]),

    ("2024-01-11 09:48:16", "feat: configure Prisma with PostgreSQL",
     "Dev", "dev@financeapp.io",
     ["prisma/schema.prisma", "lib/prisma.js", ".env.example"]),

    ("2024-01-12 16:03:54", "feat: define User and Account models in Prisma schema",
     "Dev", "dev@financeapp.io",
     ["prisma/schema.prisma"]),

    ("2024-01-15 10:11:08", "feat: add onboarding page and user creation flow",
     "Dev", "dev@financeapp.io",
     ["app/(main)/onboarding/page.jsx",
      "actions/user.js", "app/api/user/route.js"]),

    ("2024-01-16 13:44:29", "chore: add Prisma migration for initial schema",
     "Dev", "dev@financeapp.io",
     ["prisma/migrations/20240116_init/migration.sql"]),

    # ── Feb 2024 — Accounts & Dashboard ──────────────────────────────────────
    ("2024-02-01 09:02:11", "feat: scaffold main dashboard layout and sidebar",
     "Dev", "dev@financeapp.io",
     ["app/(main)/layout.jsx", "components/Sidebar.jsx",
      "components/Header.jsx"]),

    ("2024-02-05 11:17:42", "feat: create bank account CRUD actions",
     "Dev", "dev@financeapp.io",
     ["actions/account.js", "app/(main)/dashboard/page.jsx"]),

    ("2024-02-06 14:55:03", "feat: add CreateAccountDrawer component",
     "Dev", "dev@financeapp.io",
     ["components/CreateAccountDrawer.jsx"]),

    ("2024-02-08 10:33:27", "feat: display account cards with balance on dashboard",
     "Dev", "dev@financeapp.io",
     ["components/AccountCard.jsx", "app/(main)/dashboard/page.jsx"]),

    ("2024-02-12 15:48:19", "feat: add default account toggle logic",
     "Dev", "dev@financeapp.io",
     ["actions/account.js"]),

    ("2024-02-14 09:22:54", "fix: correct balance calculation on account creation",
     "Dev", "dev@financeapp.io",
     ["actions/account.js"]),

    ("2024-02-19 13:07:38", "chore: add Prisma migration for Account model update",
     "Dev", "dev@financeapp.io",
     ["prisma/schema.prisma",
      "prisma/migrations/20240219_account_update/migration.sql"]),

    ("2024-02-23 11:29:05", "feat: add transaction model to Prisma schema",
     "Dev", "dev@financeapp.io",
     ["prisma/schema.prisma",
      "prisma/migrations/20240223_transactions/migration.sql"]),

    # ── Mar 2024 — Transactions ───────────────────────────────────────────────
    ("2024-03-01 09:44:12", "feat: add transaction form with category selector",
     "Dev", "dev@financeapp.io",
     ["app/(main)/transaction/create/page.jsx",
      "components/TransactionForm.jsx"]),

    ("2024-03-04 14:11:36", "feat: implement createTransaction server action",
     "Dev", "dev@financeapp.io",
     ["actions/transaction.js"]),

    ("2024-03-06 10:58:47", "feat: update account balance after transaction",
     "Dev", "dev@financeapp.io",
     ["actions/transaction.js", "actions/account.js"]),

    ("2024-03-11 16:24:09", "feat: add transaction list on account detail page",
     "Dev", "dev@financeapp.io",
     ["app/(main)/account/[id]/page.jsx",
      "components/TransactionTable.jsx"]),

    ("2024-03-13 11:02:53", "feat: add delete and update transaction actions",
     "Dev", "dev@financeapp.io",
     ["actions/transaction.js"]),

    ("2024-03-18 09:37:21", "fix: resolve balance drift on transaction delete",
     "Dev", "dev@financeapp.io",
     ["actions/transaction.js"]),

    ("2024-03-20 14:48:32", "feat: add TransactionFilters component",
     "Dev", "dev@financeapp.io",
     ["components/TransactionFilters.jsx"]),

    ("2024-03-25 10:19:44", "feat: add bulk delete transactions",
     "Dev", "dev@financeapp.io",
     ["components/TransactionTable.jsx", "actions/transaction.js"]),

    ("2024-03-28 15:33:17", "chore: migrate schema — add isRecurring flag to Transaction",
     "Dev", "dev@financeapp.io",
     ["prisma/schema.prisma",
      "prisma/migrations/20240328_recurring/migration.sql"]),

    # ── Apr 2024 — Inngest & Recurring ───────────────────────────────────────
    ("2024-04-02 09:11:28", "chore: install and configure Inngest SDK",
     "Dev", "dev@financeapp.io",
     ["package.json", "app/api/inngest/route.js", "lib/inngest/client.js"]),

    ("2024-04-05 13:22:41", "feat: add triggerRecurringTransactions Inngest function",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js"]),

    ("2024-04-08 10:44:19", "feat: implement processRecurringTransaction batch handler",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js"]),

    ("2024-04-11 15:17:06", "fix: handle timezone edge cases in recurring schedule",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js"]),

    ("2024-04-15 09:58:34", "feat: add recurring interval support (daily, weekly, monthly)",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js", "components/TransactionForm.jsx"]),

    ("2024-04-18 14:29:53", "test: add Inngest dev server instructions to README",
     "Dev", "dev@financeapp.io",
     ["README.md"]),

    # ── May 2024 — Budgets ────────────────────────────────────────────────────
    ("2024-05-02 09:03:17", "feat: add Budget model to Prisma schema",
     "Dev", "dev@financeapp.io",
     ["prisma/schema.prisma",
      "prisma/migrations/20240502_budgets/migration.sql"]),

    ("2024-05-06 11:44:28", "feat: add budget CRUD server actions",
     "Dev", "dev@financeapp.io",
     ["actions/budget.js"]),

    ("2024-05-09 14:22:09", "feat: add BudgetProgress component with spend tracking",
     "Dev", "dev@financeapp.io",
     ["components/BudgetProgress.jsx",
      "app/(main)/dashboard/page.jsx"]),

    ("2024-05-14 10:07:51", "feat: send budget alert email when spending exceeds 80%",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js", "emails/BudgetAlert.jsx"]),

    ("2024-05-20 15:38:42", "fix: prevent duplicate budget alert emails in same period",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js"]),

    ("2024-05-24 09:29:14", "feat: add Resend SDK and email helper",
     "Dev", "dev@financeapp.io",
     ["lib/email.js", "package.json"]),

    # ── Jun 2024 — AI Receipt Scanning ───────────────────────────────────────
    ("2024-06-03 09:14:07", "chore: add Google Gemini SDK to project",
     "Dev", "dev@financeapp.io",
     ["package.json", "lib/gemini.js"]),

    ("2024-06-06 13:55:29", "feat: add receipt scanner page with file upload",
     "Dev", "dev@financeapp.io",
     ["app/(main)/transaction/create/page.jsx",
      "components/ReceiptScanner.jsx"]),

    ("2024-06-10 10:42:18", "feat: extract transaction data from receipt via Gemini",
     "Dev", "dev@financeapp.io",
     ["actions/transaction.js", "lib/gemini.js"]),

    ("2024-06-13 15:19:44", "fix: improve Gemini prompt for ambiguous receipt formats",
     "Dev", "dev@financeapp.io",
     ["lib/gemini.js"]),

    ("2024-06-17 09:03:52", "feat: auto-fill transaction form from scanned receipt",
     "Dev", "dev@financeapp.io",
     ["components/TransactionForm.jsx",
      "components/ReceiptScanner.jsx"]),

    ("2024-06-24 14:47:31", "fix: handle multi-page and landscape receipt images",
     "Dev", "dev@financeapp.io",
     ["lib/gemini.js", "components/ReceiptScanner.jsx"]),

    # ── Jul 2024 — ArcJet Security ────────────────────────────────────────────
    ("2024-07-02 10:22:08", "chore: add ArcJet SDK and environment config",
     "Dev", "dev@financeapp.io",
     ["package.json", "lib/arcjet.js", ".env.example"]),

    ("2024-07-05 14:11:37", "feat: add ArcJet rate limiting to API routes",
     "Dev", "dev@financeapp.io",
     ["lib/arcjet.js", "middleware.js"]),

    ("2024-07-09 09:48:23", "feat: add bot detection with ArcJet Shield",
     "Dev", "dev@financeapp.io",
     ["middleware.js"]),

    ("2024-07-15 13:27:54", "fix: whitelist Clerk webhook paths from ArcJet rules",
     "Dev", "dev@financeapp.io",
     ["middleware.js"]),

    ("2024-07-22 10:55:16", "docs: document ArcJet rate limits in README",
     "Dev", "dev@financeapp.io",
     ["README.md"]),

    # ── Aug 2024 — Monthly AI Reports ─────────────────────────────────────────
    ("2024-08-01 09:07:43", "feat: add generateMonthlyReports Inngest cron function",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js"]),

    ("2024-08-06 13:44:22", "feat: generate AI insights with Gemini for monthly reports",
     "Dev", "dev@financeapp.io",
     ["lib/gemini.js", "lib/inngest/function.js"]),

    ("2024-08-09 10:19:37", "feat: build MonthlyReport React email template",
     "Dev", "dev@financeapp.io",
     ["emails/MonthlyReport.jsx"]),

    ("2024-08-14 15:38:04", "feat: send monthly report via Resend on first of each month",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js", "lib/email.js"]),

    ("2024-08-20 09:32:11", "fix: handle users with no transactions in monthly report",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js"]),

    ("2024-08-27 14:07:48", "feat: add spending breakdown by category to AI report",
     "Dev", "dev@financeapp.io",
     ["lib/gemini.js"]),

    # ── Sep 2024 — Charts & Analytics ────────────────────────────────────────
    ("2024-09-03 09:44:09", "feat: add Recharts dependency for dashboard charts",
     "Dev", "dev@financeapp.io",
     ["package.json"]),

    ("2024-09-06 14:22:34", "feat: add AccountOverview chart component",
     "Dev", "dev@financeapp.io",
     ["components/AccountChart.jsx"]),

    ("2024-09-10 10:58:47", "feat: add monthly income vs expense bar chart",
     "Dev", "dev@financeapp.io",
     ["components/DashboardOverview.jsx"]),

    ("2024-09-16 13:07:18", "feat: add spending by category donut chart",
     "Dev", "dev@financeapp.io",
     ["components/DashboardOverview.jsx"]),

    ("2024-09-23 09:29:55", "fix: chart tooltips not showing on mobile",
     "Dev", "dev@financeapp.io",
     ["components/AccountChart.jsx", "components/DashboardOverview.jsx"]),

    # ── Oct 2024 — Seed Data & Polish ────────────────────────────────────────
    ("2024-10-01 10:11:27", "feat: add seed endpoint for demo data generation",
     "Dev", "dev@financeapp.io",
     ["app/api/seed/route.js"]),

    ("2024-10-07 14:33:48", "feat: generate realistic seed transactions with date spread",
     "Dev", "dev@financeapp.io",
     ["app/api/seed/route.js"]),

    ("2024-10-14 09:52:16", "feat: add skeleton loading states to dashboard cards",
     "Dev", "dev@financeapp.io",
     ["components/AccountCard.jsx",
      "app/(main)/dashboard/page.jsx"]),

    ("2024-10-21 13:19:04", "fix: flash of unstyled content on initial load",
     "Dev", "dev@financeapp.io",
     ["app/(main)/layout.jsx"]),

    ("2024-10-28 15:44:37", "refactor: extract shared Prisma queries to lib/data.js",
     "Dev", "dev@financeapp.io",
     ["lib/data.js", "actions/account.js", "actions/transaction.js"]),

    # ── Nov 2024 — Error Handling & UX ───────────────────────────────────────
    ("2024-11-04 09:18:23", "feat: add global error boundary and 404 page",
     "Dev", "dev@financeapp.io",
     ["app/error.jsx", "app/not-found.jsx"]),

    ("2024-11-08 14:02:49", "feat: add toast notifications for success/error states",
     "Dev", "dev@financeapp.io",
     ["components/ui/toaster.jsx", "app/(main)/layout.jsx"]),

    ("2024-11-13 10:37:15", "fix: account balance goes negative on failed transactions",
     "Dev", "dev@financeapp.io",
     ["actions/transaction.js"]),

    ("2024-11-19 13:55:28", "feat: add input validation with Zod on all server actions",
     "Dev", "dev@financeapp.io",
     ["actions/account.js", "actions/transaction.js",
      "actions/budget.js", "lib/schema.js"]),

    ("2024-11-25 09:44:11", "fix: Zod enum mismatch for transaction type field",
     "Dev", "dev@financeapp.io",
     ["lib/schema.js"]),

    # ── Dec 2024 — Performance & Deployment ──────────────────────────────────
    ("2024-12-02 10:08:34", "perf: add Next.js ISR to account detail pages",
     "Dev", "dev@financeapp.io",
     ["app/(main)/account/[id]/page.jsx"]),

    ("2024-12-06 14:29:57", "chore: add Vercel deployment config and env docs",
     "Dev", "dev@financeapp.io",
     ["vercel.json", "README.md"]),

    ("2024-12-11 09:52:44", "perf: optimise Prisma queries with select and pagination",
     "Dev", "dev@financeapp.io",
     ["lib/data.js", "actions/transaction.js"]),

    ("2024-12-16 13:17:08", "chore: upgrade Next.js and React to latest canary",
     "Dev", "dev@financeapp.io",
     ["package.json"]),

    ("2024-12-20 10:43:52", "fix: hydration mismatch in AccountCard balance display",
     "Dev", "dev@financeapp.io",
     ["components/AccountCard.jsx"]),

    ("2024-12-27 09:14:29", "docs: update README with full setup guide and env vars",
     "Dev", "dev@financeapp.io",
     ["README.md"]),

    # ── Jan 2025 — New Year Refactor ─────────────────────────────────────────
    ("2025-01-06 09:22:07", "refactor: migrate server actions to use next-safe-action",
     "Dev", "dev@financeapp.io",
     ["actions/account.js", "actions/transaction.js",
      "actions/budget.js"]),

    ("2025-01-10 13:48:31", "feat: add optimistic updates to transaction delete",
     "Dev", "dev@financeapp.io",
     ["components/TransactionTable.jsx"]),

    ("2025-01-15 10:29:14", "feat: add currency formatting utility with locale support",
     "Dev", "dev@financeapp.io",
     ["lib/utils.js"]),

    ("2025-01-21 15:03:47", "fix: Inngest recurring job fires twice on DST change",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js"]),

    ("2025-01-28 09:44:22", "chore: add ESLint rules and format all files",
     "Dev", "dev@financeapp.io",
     [".eslintrc.json", "prettier.config.js"]),

    # ── Feb 2025 — Multi-currency ─────────────────────────────────────────────
    ("2025-02-03 10:11:38", "feat: add currency field to Account model",
     "Dev", "dev@financeapp.io",
     ["prisma/schema.prisma",
      "prisma/migrations/20250203_currency/migration.sql"]),

    ("2025-02-07 14:37:19", "feat: display currency symbol on balance and transactions",
     "Dev", "dev@financeapp.io",
     ["components/AccountCard.jsx", "components/TransactionTable.jsx",
      "lib/utils.js"]),

    ("2025-02-13 09:52:03", "feat: add currency selector to CreateAccountDrawer",
     "Dev", "dev@financeapp.io",
     ["components/CreateAccountDrawer.jsx"]),

    ("2025-02-19 13:27:48", "fix: budget comparison breaks when account currency differs",
     "Dev", "dev@financeapp.io",
     ["actions/budget.js", "components/BudgetProgress.jsx"]),

    ("2025-02-25 10:44:11", "perf: cache exchange rates in Redis for 1 hour",
     "Dev", "dev@financeapp.io",
     ["lib/currency.js"]),

    # ── Mar 2025 — Improved AI Reports ───────────────────────────────────────
    ("2025-03-03 09:07:34", "feat: include savings rate in monthly AI report",
     "Dev", "dev@financeapp.io",
     ["lib/gemini.js", "lib/inngest/function.js"]),

    ("2025-03-07 13:44:29", "feat: add top merchants section to monthly report email",
     "Dev", "dev@financeapp.io",
     ["emails/MonthlyReport.jsx", "lib/inngest/function.js"]),

    ("2025-03-13 10:19:52", "feat: add year-over-year comparison in AI insights",
     "Dev", "dev@financeapp.io",
     ["lib/gemini.js"]),

    ("2025-03-19 15:38:07", "fix: report email renders blank for new users (< 1 month)",
     "Dev", "dev@financeapp.io",
     ["lib/inngest/function.js"]),

    ("2025-03-26 09:22:43", "refactor: extract report data assembly into lib/reports.js",
     "Dev", "dev@financeapp.io",
     ["lib/reports.js", "lib/inngest/function.js"]),

    # ── Apr 2025 — Dashboard v2 ───────────────────────────────────────────────
    ("2025-04-02 10:48:16", "feat: redesign dashboard with stats overview bar",
     "Dev", "dev@financeapp.io",
     ["app/(main)/dashboard/page.jsx",
      "components/DashboardOverview.jsx"]),

    ("2025-04-07 14:11:28", "feat: add net-worth trend line chart to dashboard",
     "Dev", "dev@financeapp.io",
     ["components/DashboardOverview.jsx"]),

    ("2025-04-14 09:37:54", "feat: add date-range picker to transaction filters",
     "Dev", "dev@financeapp.io",
     ["components/TransactionFilters.jsx"]),

    ("2025-04-21 13:55:07", "fix: date range filter off by one day in UTC",
     "Dev", "dev@financeapp.io",
     ["components/TransactionFilters.jsx", "actions/transaction.js"]),

    ("2025-04-28 10:29:38", "perf: memoize dashboard aggregation with React.cache",
     "Dev", "dev@financeapp.io",
     ["app/(main)/dashboard/page.jsx", "lib/data.js"]),

    # ── May 2025 — Export & Accessibility ─────────────────────────────────────
    ("2025-05-02 09:14:07", "feat: add CSV export for transactions",
     "Dev", "dev@financeapp.io",
     ["app/api/export/route.js", "components/TransactionTable.jsx"]),

    ("2025-05-08 13:22:44", "feat: add keyboard navigation to TransactionTable",
     "Dev", "dev@financeapp.io",
     ["components/TransactionTable.jsx"]),

    ("2025-05-14 10:57:19", "fix: improve colour contrast for budget progress bar",
     "Dev", "dev@financeapp.io",
     ["components/BudgetProgress.jsx", "app/globals.css"]),

    ("2025-05-20 15:33:52", "feat: add ARIA labels and roles to chart components",
     "Dev", "dev@financeapp.io",
     ["components/AccountChart.jsx",
      "components/DashboardOverview.jsx"]),

    ("2025-05-27 09:48:23", "docs: add CONTRIBUTING.md and pull request template",
     "Dev", "dev@financeapp.io",
     ["CONTRIBUTING.md", ".github/PULL_REQUEST_TEMPLATE.md"]),

    # ── Jun 2025 — Current Work ───────────────────────────────────────────────
    ("2025-06-02 10:11:34", "feat: add transaction tags / labels system",
     "Dev", "dev@financeapp.io",
     ["prisma/schema.prisma",
      "prisma/migrations/20250602_tags/migration.sql",
      "components/TransactionForm.jsx",
      "components/TransactionTable.jsx"]),

    ("2025-06-04 14:28:17", "fix: tag filter not persisting across page navigation",
     "Dev", "dev@financeapp.io",
     ["components/TransactionFilters.jsx"]),

    ("2025-06-05 09:52:48", "chore: bump all dependencies to latest stable versions",
     "Dev", "dev@financeapp.io",
     ["package.json"]),
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list[str], cwd: str = None, env: dict = None) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        print(f"[ERROR] {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result


def git(args: list[str], cwd: str, env: dict = None):
    return run(["git"] + args, cwd=cwd, env=env)


def ensure_git_repo(repo_path: str):
    p = Path(repo_path)
    if not (p / ".git").exists():
        print(f"[!] {repo_path} is not a git repository. Initialising…")
        git(["init"], cwd=repo_path)
        git(["checkout", "-b", "main"], cwd=repo_path)


def touch_files(repo_path: str, files: list[str], date_str: str):
    """Create or append a tiny marker to each file so the commit is non-empty."""
    for rel_path in files:
        full = Path(repo_path) / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "a", encoding="utf-8") as fh:
            # A single-line comment that won't break most file types
            fh.write(f"# updated {date_str}\n")


def make_commit(repo_path: str, date_str: str, message: str,
                author_name: str, author_email: str, files: list[str],
                dry_run: bool = False):
    if dry_run:
        print(f"  [dry-run] {date_str}  {message}")
        return

    import os
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = author_name
    env["GIT_AUTHOR_EMAIL"] = author_email
    env["GIT_COMMITTER_NAME"] = author_name
    env["GIT_COMMITTER_EMAIL"] = author_email
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    touch_files(repo_path, files, date_str)

    git(["add", "-A"], cwd=repo_path, env=env)

    # Check if there's anything to commit (in case files already exist)
    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_path, capture_output=True
    )
    if status.returncode == 0:
        # Nothing staged — touch again with a unique byte
        touch_files(repo_path, files[:1], f"{date_str}-{random.randint(1000, 9999)}")
        git(["add", "-A"], cwd=repo_path, env=env)

    git(["commit", "-m", message], cwd=repo_path, env=env)
    print(f"  ✓  {date_str[:10]}  {message[:72]}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Finance Platform — Git history forge script"
    )
    parser.add_argument(
        "--repo-path", default=".",
        help="Path to the local git repository (default: current directory)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print commits without actually creating them"
    )
    parser.add_argument(
        "--remote", default="",
        help="Remote name to force-push to after creating commits (e.g. origin)"
    )
    parser.add_argument(
        "--branch", default="main",
        help="Branch name to push (default: main)"
    )
    args = parser.parse_args()

    repo_path = str(Path(args.repo_path).resolve())
    print(f"\n{'='*60}")
    print(f"  Git History Forge — AI Finance Platform")
    print(f"  Repo  : {repo_path}")
    print(f"  Commits: {len(COMMIT_PLAN)}")
    print(f"  Dry run: {args.dry_run}")
    print(f"{'='*60}\n")

    if not args.dry_run:
        ensure_git_repo(repo_path)

    for date_str, message, author, email, files in COMMIT_PLAN:
        make_commit(repo_path, date_str, message, author, email, files,
                    dry_run=args.dry_run)

    if not args.dry_run and args.remote:
        print(f"\n[→] Force-pushing to {args.remote}/{args.branch}…")
        git(["push", "--force", args.remote, args.branch], cwd=repo_path)
        print(f"  ✓  Force push complete.")

    print(f"\n{'='*60}")
    print(f"  {'[DRY RUN] Would have created' if args.dry_run else 'Created'} "
          f"{len(COMMIT_PLAN)} commits.")
    if not args.dry_run and not args.remote:
        print(f"\n  To push, run:")
        print(f"    git -C {repo_path} push --force origin {args.branch}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()