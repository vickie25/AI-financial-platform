# SILVER REPOSITORY CONSTRUCTION & HARDENING STANDARD

## PURPOSE

This instruction governs creation, expansion, validation, packaging, and hardening of repositories intended for:

* Silver review
* SWE-bench style evaluation
* Codex execution environments
* Repository archaeology
* Contributor analysis
* Enterprise repository assessment

The objective is to produce repositories that:

* build from clean checkout
* pass tests from clean checkout
* maintain visible Git history
* contain meaningful business logic
* avoid scaffold classification
* avoid tutorial-clone classification
* avoid starter-template classification
* survive repository resets
* survive Dockerized execution
* survive static analysis
* survive similarity analysis

---

# CORE PRINCIPLES

Never optimize for appearance.

Optimize for:

* real functionality
* real workflows
* real integration
* real tests
* real repository evolution

Do not:

* add filler code
* add dead code
* add fake modules
* add fake commits
* add synthetic domains
* add meaningless abstractions
* add test-only production files

Every module must:

* be used
* be integrated
* be tested
* be reachable
* participate in production workflows

---

# REPOSITORY SCALE REQUIREMENTS

Minimum targets:

Production LOC:

* 10,000+

Preferred:

* 12,000+

Business Logic LOC:

* 5,000+

Preferred:

* 7,500+

Production Modules:

* 100+

Business Domains:

* 12+

Models:

* 15+

Repositories:

* 10+

Services:

* 10+

API Routes:

* 20+

Tests:

* 150+

Preferred:

* 200+

Coverage:

* 90%+

Preferred:

* 100%

Meaningful Commits:

* 100+

Preferred:

* 200+

---

# BUSINESS LOGIC REQUIREMENTS

The repository must represent a platform.

Not:

* CRUD demo
* dashboard demo
* tutorial clone
* starter project

Each domain must include:

* models
* repositories
* services
* API endpoints
* validations
* authorization
* tests

---

# DOMAIN REQUIREMENTS

Each domain should contain:

* lifecycle
* workflows
* state transitions
* validation
* reporting
* auditing

Avoid:

Entity
├── page
├── client
├── columns
├── form
└── CRUD API

repeated across the entire repo.

Every domain should have unique workflows.

---

# WORKFLOW REQUIREMENTS

Examples:

## Governance

* approval workflows
* review workflows
* rejection workflows

## Audit

* audit logs
* audit events
* change history

## Compliance

* policy enforcement
* validation pipelines

## Analytics

* reporting
* metrics
* aggregation

## Operations

* jobs
* retries
* scheduling

## Integration

* provider adapters
* webhooks
* event handling

---

# SERVICE LAYER REQUIREMENTS

Business logic belongs in services.

Avoid:

route.ts
→ contains all logic

Instead:

route
→ service
→ repository

Every service must be tested.

Every repository must be tested.

---

# TEST REQUIREMENTS

Tests must cover:

Success paths

Failure paths

Validation paths

Authorization paths

Idempotency paths

Concurrency paths

Edge cases

Null cases

Empty cases

Error handling

Retry handling

Fallback handling

---

# COVERAGE REQUIREMENTS

Coverage must include:

app

components

hooks

providers

actions

lib

middleware

Do not narrow coverage scope.

Forbidden:

coverage.include:
only api
only lib
only services

Coverage must represent repository-wide behavior.

Required verification:

npx vitest run --coverage

Expected:

All files

not:

selected files

---

# BUILD REQUIREMENTS

Repository must build from:

git reset --hard HEAD

git clean -xfd

npm install

npm run build

without:

manual fixes

environment hacks

local caches

generated files

---

# CLEAN CHECKOUT VALIDATION

Required verification:

git reset --hard HEAD

git clean -xfd

npm install

npm run lint

npm run typecheck

npm run build

npm test

npx vitest run --coverage

All must pass.

---

# DOCKER REQUIREMENTS

Never exclude .git when repository is intended for:

* Silver
* Codex
* SWE-bench
* archaeology
* commit analysis

Required:

.git visible inside task environment

Required exclusions:

node_modules

coverage

.next

dist

build

tmp

logs

.env

.env.*

Keep:

!.env.example

---

# GIT HISTORY REQUIREMENTS

History must appear organic.

Avoid:

50 commits same timestamp

100 commits same minute

part 1/2
part 2/2
part 3/3

repeated excessively

Preferred:

feature commits

refactor commits

test commits

fix commits

integration commits

workflow commits

deployment commits

---

# COMMIT REQUIREMENTS

Every commit must:

build

pass tests

represent logical work

Examples:

add audit pipeline

add reconciliation workflow

add approval engine

add reporting service

integrate governance checks

fix checkout race condition

---

# TUTORIAL-CLONE ELIMINATION

Remove:

tutorial comments

tutorial naming

tutorial typos

tutorial metadata

tutorial README text

starter screenshots

starter assets

starter branding

---

# SIMILARITY HARDENING

Search for:

tutorial paths

tutorial entities

tutorial comments

copied wording

copied structure

copied README content

Remove all.

Replace tutorial domains with:

organization-specific domains

business-specific workflows

platform-specific terminology

---

# BRANDING REQUIREMENTS

Repository identity must be consistent across:

README

package.json

metadata

OpenGraph

titles

UI

docs

CI

Docker

badges

archive names

---

# ARCHIVE REQUIREMENTS

Submission archive must:

contain one top-level folder

contain .git

exclude generated artifacts

exclude secrets

exclude coverage output

exclude node_modules

exclude build output

exclude logs

exclude temporary files

---

# FORBIDDEN FILES

Never submit:

.env

coverage/

node_modules/

.next/

dist/

build/

tmp/

logs/

tsconfig.tsbuildinfo

---

# SCAFFOLD DETECTION HARDENING

Remove:

next.svg

vercel.svg

starter text

starter metadata

generator configs

unused template assets

unused scaffold files

unused examples

---

# PRISMA REQUIREMENTS

Prisma generation must be reproducible.

Use:

postinstall:
prisma generate

Repository must work after clean install.

---

# BUILD-TIME SAFETY

Avoid:

eager Prisma initialization

eager Stripe initialization

eager external service initialization

Use:

lazy initialization

dependency injection

runtime factories

---

# API REQUIREMENTS

Every API route must include:

validation

auth

authorization

error handling

audit support

tests

---

# REPOSITORY AUDIT CHECKLIST

Must pass:

[ ] git status clean

[ ] git rev-list --count HEAD

[ ] git log --oneline -10

[ ] npm install

[ ] npm run lint

[ ] npm run typecheck

[ ] npm run build

[ ] npm test

[ ] npx vitest run --coverage

[ ] archive verification

[ ] no tracked secrets

[ ] no scaffold residue

[ ] no tutorial residue

[ ] no dead code

[ ] no unused domains

[ ] no generated artifacts

[ ] Git history visible

[ ] coverage repository-wide

[ ] build reproducible

[ ] tests reproducible

---

# FINAL ACCEPTANCE CRITERIA

Repository should appear as:

enterprise platform

production application

evolving codebase

multi-domain system

business-driven architecture

not:

tutorial

starter template

CRUD demo

prototype

toy project

class assignment

bootcamp exercise

or generated scaffold
