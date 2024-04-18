# 📊 AI Finance Platform (Next.js + Prisma + Clerk + Inngest)

A modern, full-stack personal finance dashboard built with **Next.js (App Router)**, **Clerk auth**, **Prisma**, **PostgreSQL**, **Inngest background jobs**, **ArcJet security/rate limiting**, and **Google Gemini AI**.

This app helps users:
- Track multiple bank accounts and balances
- Log income and expenses (including recurring payments)
- Set monthly budgets and receive alerts
- Scan receipts with AI-powered OCR
- Generate monthly insights via email

---

## 🚀 Key Features

- ✅ **User authentication** (Clerk)
- ✅ **Accounts & transactions** (CRUD + balance tracking)
- ✅ **Recurring transactions** (automated via Inngest)
- ✅ **Budgets & alerts** (email notifications when spending is high)
- ✅ **Receipt scanning** (Google Gemini + image parsing)
- ✅ **Monthly AI reports** (Gemini insights + Resend email)
- ✅ **Rate limiting & bot protection** (ArcJet + middleware)

---

## 🧰 Tech Stack

- **Next.js 15 (App Router)**
- **React 19 (canary)**
- **Tailwind CSS + shadcn/ui**
- **Clerk** (auth)
- **Prisma + PostgreSQL**
- **Inngest** (background jobs & cron)
- **ArcJet** (security & rate limiting)
- **Google Gemini** (AI/ML)
- **Resend** (transactional email)

---

## 🔧 Getting Started

### 1) Prerequisites

- Node.js 20+ (recommended)
- PostgreSQL (local or hosted)
- Clerk project (for auth)
- Resend account (for email)
- Google Cloud project with Gemini API enabled
- ArcJet account (optional but recommended for bot protection)

### 2) Install dependencies

```bash
npm install
```

### 3) Configure environment variables

Create a `.env` file in the project root with the following values:

```env
DATABASE_URL=
DIRECT_URL=

NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/onboarding
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

GEMINI_API_KEY=

RESEND_API_KEY=

ARCJET_KEY=
```

> 💡 If you use Vercel, set these values in your project’s Environment Variables settings.

### 4) Run database migrations

```bash
npx prisma migrate dev --name init
```

### 5) Seed demo data (optional)

Start the dev server and visit the seed endpoint to generate sample transactions:

```bash
npm run dev
# In your browser:
http://localhost:3000/api/seed
```

---

## ▶️ Running Locally

```bash
npm run dev
```

Then open: http://localhost:3000

---

## 🧠 Background Jobs (Inngest)

This project uses Inngest to run scheduled tasks and background processing.

Key functions are in `lib/inngest/function.js`:

- `triggerRecurringTransactions` (runs daily)
- `processRecurringTransaction` (processes recurring entries in batches)
- `generateMonthlyReports` (sends AI-powered reports via email)
- `checkBudgetAlerts` (sends budget threshold emails)

### Running Inngest locally

```bash
npx inngest dev
```

---

## 📦 Deployment

This app is well-suited for Vercel, but any Next.js host works.

### Vercel Checklist

- Set all `.env` values in your Vercel project
- Ensure `DATABASE_URL` and `DIRECT_URL` are correct
- Enable Next.js App Router support

---

## 🧩 Notes

- Authentication is handled with **Clerk** via `middleware.js`.
- Rate limiting + bot filtering is handled by **ArcJet**.
- Receipt scanning uses **Gemini** for OCR and data extraction.
- Email sending uses **Resend** and React-based email templates.

---

## 📌 Useful Commands

- `npm run dev` – Start dev server
- `npm run build` – Build for production
- `npm run start` – Start production server
- `npm run lint` – Run ESLint

---

## 📨 Want to contribute?

1. Fork the repo
2. Add a feature or fix
3. Open a pull request with a clear description

---

## 🔍 Where to look next

- `app/(main)/dashboard` – Main dashboard page
- `app/(main)/transaction` – Create/scan transactions
- `app/api/inngest/route.js` – Inngest endpoint
- `lib/arcjet.js` – ArcJet config
- `prisma/schema.prisma` – Database schema

---

Enjoy building! 🚀
# updated 2024-01-08 09:14:22
# updated 2024-01-08 09:14:22
# updated 2024-04-18 14:29:53
