---
description: Silver SWE-bench task creation, hardening, validation, and submission guide — use this after the repo is approved
applyTo: "**/{instruction.md,reference_plan.md,task.toml,environment/**,solution/**,tests/**,config.json}"
---

Edit one task at a time.
Do not modify another task unless the user explicitly asks.

## Task Creation Runbook

Use this runbook on every new task.

1. Read this guide and the three checker scripts: `silver_quality_check.sh`, `silver_similarity_check.sh`, and `silver_fairness_check.sh`.
2. Draft `instruction.md` before writing tests.
3. Draft `reference_plan.md` with root cause and fix strategy, no exact implementation recipe.
4. Author verifier tests and align `tests/config.json`.
5. Run `bash silver_quality_check.sh <task-dir>` after structural edits.
6. Run `bash silver_fairness_check.sh <task-dir>`.
7. Run `bash silver_similarity_check.sh <task-dir>`.
8. Run `bash silver_instruction/presubmit_gate.sh <task-dir>` and inspect outputs.
9. Perform the difficulty probe:
   1. Sonnet 4.6 for fast implementation pressure.
   2. Opus 4.8 for reasoning pressure.
10. Keep final difficulty in the 1-4/10 target:
   1. If Sonnet is too successful, add cross-file flow and meaningful edge cases.
   2. If Opus fails repeatedly, remove hidden assumptions and clarify behavior.
11. Re-run checks after final edits.

For `instruction.md` and `reference_plan.md`, keep them:
- Human-readable and behavior-focused.
- Explicit about edge cases and expected outputs.
- Clear about compatibility constraints.
- Free of test internals, platform vocabulary, reward paths, and file references.
- Implicit about implementation approach, and explicit about required behavior.

# Silver Task Authoring Guide

**Prerequisite:** The target repository must already be approved by the platform admin and have a registered Docker base image before you start. See `silver_repo_guide.instructions.md` for the repo submission process.

Use this guide when creating, revising, validating, or packaging a Silver SWE-bench-style task. A task is ready only when it is well-specified, behaviorally verified, fair to agents, locally validated (F2P tests fail before solution, all tests pass after solution), and zipped with only the required task files.

---

## Authoring Rules

- Prefer cybersecurity-focused task candidates when possible.
- Every task must be unique: do not use a bug or fix that already exists as a completed or obvious fix in the base commit history.
- Do not create a task that is a reworded version of another task's root cause or that replays an existing repository patch with light wording changes. Require a distinct root cause and behavioral contract.
- Before finalizing a task, check nearby tasks for overlap in bug mechanism, touched files, and expected behavior. If similarity risk is high, pivot to a different bug class — not just different wording.
- Prefer cross-module or multi-file fixes when the bug naturally calls for them.
- Do not inflate a task with meaningless edits only to increase file count. Difficulty must come from the behavior, edge cases, or integration reasoning.

---

## Required Task Layout

A complete task directory (replace `task-name` with a descriptive, unique name using only letters, numbers, hyphens, underscores, or dots):

```text
task-name/
  instruction.md          ← agent-facing engineering ticket (the ONLY thing the agent sees)
  reference_plan.md       ← reviewer-only: root cause, fix outline, test plan
  task.toml               ← metadata: difficulty, timeouts, resources, category
  environment/
    Dockerfile            ← pinned base image, install deps, pre-create /logs/verifier
  solution/
    solve.sh              ← applies reference fix via git apply; resolves repo root robustly
  tests/
    config.json           ← base_commit, test_patch, fail_to_pass, pass_to_pass, selected files
    parser.py             ← parses test runner output to extract test names
    run_script.sh         ← configurable: runs selected or all tests using the repo's test command
    test.sh               ← orchestrates: write reward trap → apply test_patch → run → write result
```

Do not add `requirements.txt` at the task root (that is a Harbor convention, not a Silver one). Do not copy tests or solution files into the Dockerfile.

---

## Core Workflow

1. **Pick a bug.** Select a real bug, missing feature, or refactor from the approved repo. The base commit must be the state *before* the fix.
2. **Confirm base commit.** Verify the commit hash exists in the repo's git history. Write it down — it goes everywhere.
3. **Write `instruction.md`.** Draft the agent-facing ticket before writing tests, so testing is driven by the specification.
4. **Write `reference_plan.md`.** Document the root cause, why base commit is broken, the intended fix approach, and the test coverage rationale.
5. **Write `tests/config.json`.** Define `base_commit`, `test_patch` (unified diff adding verifier tests), `fail_to_pass`, `pass_to_pass`, and `selected_test_files_to_run`.
6. **Configure `tests/run_script.sh`.** Set up `run_all_tests()` and `run_selected_tests()` for the repo's test toolchain.
7. **Verify `tests/parser.py`.** Ensure it extracts test names in exactly the format used in `fail_to_pass` / `pass_to_pass`.
8. **Write `solution/solve.sh`.** Apply a minimal unified diff via `git apply`. Resolve REPO_ROOT robustly (check multiple candidate paths).
9. **Write `environment/Dockerfile`.** Use the exact approved base image. Reset to `base_commit`, install dependencies, pre-create `/logs/verifier`.
10. **Local validation (required before zipping):**
    - Reset repo → apply `test_patch` → run selected tests → confirm F2P **fails**, P2P **passes**.
    - Apply `solution/solve.sh` → run selected tests → confirm F2P **and** P2P both **pass**.
11. **Run quality check twice:** before and after local validation.
12. **Zip** only the required task files for submission.

---

## Local Commands

**Important:** Silver tasks use a private AQ base image. `harbor run` does not work locally for Silver tasks. Validation is done manually against the actual target repository.

### Quality check

```bash
bash silver_quality_check.sh "<task-dir>"
```

### Oracle simulation — does the fix make all tests pass?

```bash
# 1. Reset repo to base_commit (broken state)
git -C "<repo-dir>" reset --hard "<base_commit>"
git -C "<repo-dir>" clean -fd

# 2. Apply test_patch (adds verifier tests — agents never see these)
python3 -c "
import json, sys
patch = json.load(open('<task-dir>/tests/config.json')).get('test_patch', '')
if patch and not patch.startswith('<'): sys.stdout.write(patch)
" > /tmp/test_patch.diff
git -C "<repo-dir>" apply /tmp/test_patch.diff

# 3. Apply your fix
git -C "<repo-dir>" apply /tmp/solution.diff
# or run: bash "<task-dir>/solution/solve.sh"

# 4. Run tests — ALL (F2P + P2P) must PASS
cd "<repo-dir>"
npx jest --verbose --forceExit      # JS/TS
# pytest --tb=short -q              # Python
# go test ./...                     # Go
```

### Nop simulation — do F2P tests fail without any fix?

```bash
# 1. Reset repo to base_commit (no fix applied)
git -C "<repo-dir>" reset --hard "<base_commit>"
git -C "<repo-dir>" clean -fd

# 2. Apply test_patch only (no fix)
git -C "<repo-dir>" apply /tmp/test_patch.diff

# 3. Run tests — F2P must FAIL, P2P must PASS
cd "<repo-dir>"
npx jest --verbose --forceExit
```

If any F2P test passes here, it already exists in the repo at `base_commit` or the test is wrong. Fix the test or choose a different `base_commit`.

### Storing the diff in solve.sh

```bash
# Generate the diff from the current patched state of the repo
git -C "<repo-dir>" diff HEAD -- <files-you-changed> > /tmp/solution.diff
```

Paste that diff into the `solve.sh` heredoc between `<<'__SOLUTION__'` and `__SOLUTION__`.

### Final quality check

```bash
bash silver_quality_check.sh "<task-dir>"
```

---

## `instruction.md` — Agent Ticket

This is the **only** thing the evaluated agent reads. Write it as a real engineering ticket.

**Must include:**
- The user-visible problem or missing behavior in plain language.
- Concrete expected outcomes for the main case and every edge case the tests cover.
- Any input/output, endpoint, CLI command, or file contract that is part of the behavioral expectation.
- Exact definitions of ambiguous terms when tests depend on that distinction (e.g., what counts as a "malformed token", "stale record", "duplicate entry", or "invalid path").
- Compatibility or regression expectations covered by `pass_to_pass` tests.

**Must not include:**
- Pseudocode, dictated helper names, prescribed algorithms, or exact implementation steps.
- Test names, verifier file names, parser mechanics, or solution patch hints.
- Platform prose, internal reviewer instructions, or assessment mechanics.
- A vague phrase like "handle malformed input" when the tests make a specific distinction about it.
- Stack traces or config dumps unless a small excerpt is essential to explain the bug.

The alignment rule: if a test checks a behavior, the instruction must describe that behavior. If the instruction requests a behavior, the tests must verify it.

**AI register check:** Write the way you would explain the problem to a teammate. Drop heavy nested bullet hierarchies. Avoid phrases like "ensure", "leverage", "utilize", "seamlessly". Natural register passes the AI text check; over-polished prose fails it. Pre-check with GPTZero (≥80% human) before submission.

---

## `reference_plan.md` — Reviewer Notes

For reviewers only — never shown to agents. Keep it concise:

- Root cause: what code is broken and why.
- Why the base commit is the right start point.
- Intended repair approach (do not prescribe exact code shape — solutions that reach the same outcome through different code are equally valid).
- Test plan: what each `fail_to_pass` group proves and what each `pass_to_pass` group protects.
- Fairness notes for any edge case that could be tricky or misinterpreted.

Use this document to explain why the task is difficult for the *right* reason: non-obvious behavior, cross-module interaction, subtle edge cases, or realistic integration work.

---

## `tests/config.json` — Test Contract

All fields are required:

```json
{
  "repo": "<repo-name>",
  "instance_id": "instance_<author>__<reponame>-<short-hash>-<slug>",
  "base_commit": "<full-or-7-char commit hash>",
  "test_patch": "<unified diff that adds/modifies verifier tests>",
  "fail_to_pass": ["<test-name-exactly-as-parser-emits>", ...],
  "pass_to_pass": ["<test-name-exactly-as-parser-emits>", ...],
  "selected_test_files_to_run": ["tests/<file1>", "tests/<file2>"],
  "patch": "<auto-derived from solution/solve.sh at submit time>",
  "problem_statement": "<auto-derived from instruction.md at submit time>",
  "before_repo_set_cmd": ""
}
```

Rules:
- `base_commit` must exist in the repo's git history (7–40 chars).
- `fail_to_pass` must be non-empty. Test names must **exactly match** what `parser.py` emits — copy from real local output, never from memory.
- `pass_to_pass` should be smaller than `fail_to_pass`. Focus on proving unrelated existing behavior still works.
- `test_patch` is a unified diff that adds the verifier test files. The platform applies this patch at grading time only — the agent never sees these test files directly.
- `selected_test_files_to_run` lists the test files the harness executes.
- `patch` and `problem_statement` are auto-derived at submit time; use the placeholder strings shown above.

**Good verifier tests** execute real code paths and assert observable outcomes: HTTP response codes, CLI output, file content, database state, return values, or runtime errors. Do not assert on source code structure, import names, or implementation details unless the task is explicitly about formatting or naming conventions.

**Test determinism:** avoid wall-clock time, external network calls, random ordering, mutable global state, or environment-specific paths. Tests must produce the same result every run.

---

## `tests/run_script.sh` — Test Runner

The configurable section defines two shell functions; the rest is boilerplate. Only edit the configurable section:

```bash
#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
  cd "${REPO_ROOT:-$PWD}"
  # Replace this with the repo's test command:
  npx jest --verbose --silent --maxWorkers=1 --forceExit 2>&1 || true
  # Python: pytest --tb=short -q 2>&1 || true
  # Go:     go test ./... 2>&1 || true
}

run_selected_tests() {
  local test_files=("$@")
  echo "Running selected tests: ${test_files[@]}"
  cd "${REPO_ROOT:-$PWD}"
  npx jest --verbose --silent --maxWorkers=1 --forceExit "${test_files[@]}" 2>&1 || true
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
if [ $# -eq 0 ]; then
  run_all_tests
  exit $?
fi
if [[ "$1" == *","* ]]; then
  IFS=',' read -r -a TEST_FILES <<< "$1"
else
  TEST_FILES=("$@")
fi
run_selected_tests "${TEST_FILES[@]}"
```

---

## `tests/test.sh` — Test Orchestrator

**Copy `test.sh` from the task-1 template.** Only change the candidate paths inside `resolve_repo_root()` to match your repo's mount location. Do not rewrite the rest — it is load-bearing boilerplate.

What the full `test.sh` does (in order):
1. Installs an EXIT trap that writes `reward.txt` before anything can crash.
2. Resolves the repo root across multiple mount-path candidates.
3. Extracts and applies `test_patch` from `/tests/config.json` (verifier tests — never seen by agent).
4. Reads `selected_test_files_to_run` from `/tests/config.json` and passes them to `run_script.sh`.
5. Captures stdout/stderr to temp files.
6. Runs `parser.py` to produce `/tmp/output.json`.
7. Copies output/logs to `/logs/verifier/` for debugging.
8. Evaluates `fail_to_pass` and `pass_to_pass` against the parsed results and exits 0 (reward=1) or 1 (reward=0).

The only part you author is `resolve_repo_root()`. Template:

```bash
resolve_repo_root() {
    local candidates=(
        "/app/<RepoName>"
        "/app"
        "/testbed"
        "/testbed/<RepoName>"
    )
    local dir child
    for dir in "${candidates[@]}"; do
        if [ -d "$dir" ] && [ -f "$dir/package.json" ] && { [ -d "$dir/app" ] || [ -d "$dir/pages" ]; }; then
            echo "$dir"; return 0
        fi
    done
    for dir in "/app" "/testbed"; do
        [ -d "$dir" ] || continue
        for child in "$dir"/*; do
            [ -d "$child" ] || continue
            if [ -f "$child/package.json" ] && { [ -d "$child/app" ] || [ -d "$child/pages" ]; }; then
                echo "$child"; return 0
            fi
        done
    done
    return 1
}
```

Adapt the identification check (`-f package.json && -d app`) to match your repo's signature file (e.g., `setup.py`, `go.mod`, `Cargo.toml`).

---

## `tests/parser.py` — Output Parser

**Copy `parser.py` from the task-1 template** (for Jest/TypeScript repos). For Python/pytest repos, use a pytest parser; for Go, use a Go test parser. Do not write one from scratch.

The parser reads stdout/stderr from the test runner and writes a JSON file with this exact format:

```json
{"tests": [{"name": "<fully-qualified test name>", "status": "PASSED"}, ...]}
```

Valid status values: `PASSED`, `FAILED`, `SKIPPED`, `ERROR`.

The fully-qualified name format for Jest (what task-1 parser.py emits) is:
```
test_file_name.test.ts::Describe block name > test name
```
Example: `test_auth_middleware.test.ts::Blog POST requires authentication > rejects request with no Authorization header - returns 401`

This format must **exactly** match the strings in `fail_to_pass` and `pass_to_pass`. Copy test names from real local output — never type them from memory.

For pytest repos, the equivalent format is:
```
tests/test_foo.py::TestClassName::test_method_name
```

Do not modify the output format or `main` signature — `test.sh` calls `parser.py stdout_file stderr_file output_json_path`.

---

## `solution/solve.sh` — Reference Fix

`solve.sh` applies the gold solution that makes all tests pass. Structure:

```bash
#!/bin/bash
set -euo pipefail

# Resolve repo root with multiple candidate paths — handle different mount layouts
resolve_repo_root() {
    local candidates=("${REPO_ROOT:-}" "/app/<RepoName>" "/app" "/testbed" "/testbed/<RepoName>")
    local dir child
    for dir in "${candidates[@]}"; do
        [ -n "$dir" ] || continue
        if [ -d "$dir" ] && <repo-identifying-check>; then
            echo "$dir"; return 0
        fi
    done
    # Fallback: search under /app and /testbed
    for dir in "/app" "/testbed"; do
        [ -d "$dir" ] || continue
        for child in "$dir"/*; do
            [ -d "$child" ] || continue
            if <repo-identifying-check-on-child>; then echo "$child"; return 0; fi
        done
    done
    return 1
}

REPO_ROOT=$(resolve_repo_root) || { echo "ERROR: cannot locate repo root"; exit 1; }
cd "$REPO_ROOT"

cat > /tmp/solution.patch <<'__SOLUTION__'
<paste unified diff here>
__SOLUTION__

git apply /tmp/solution.patch
```

Rules:
- Patch must apply cleanly at `base_commit`.
- The fix must be minimal: no unrelated refactors, no cleanup commits, no whitespace changes.
- Do not edit verifier test files in the solution patch.
- Do not forge `/logs/verifier/reward.txt` — never write the reward file from `solve.sh`.
- Do not hardcode behavior that only matches the specific hidden test inputs.

---

## `environment/Dockerfile` — Agent Environment

Use the **exact** base image path given by the platform after repo approval:

```dockerfile
FROM us-docker.pkg.dev/afterqueryai/silver-repo-images/<reponame>-<tag>:v1@sha256:<digest>

ENTRYPOINT []

WORKDIR "/app/<RepoName>"

# Reset repo to base commit state
RUN set -e \
 && git reset --hard <base_commit> \
 && git clean -fd \
 && git checkout <base_commit>

# Install dependencies (pin versions; use --no-install-recommends for apt)
RUN npm install --force --legacy-peer-deps --no-audit --no-fund
# or: pip install -r requirements.txt
# or: go mod download

# Pre-create the reward file directory
RUN mkdir -p /logs/verifier
```

Rules:
- Do **not** copy `tests/`, `solution/`, or any verifier files into the image. The platform mounts them at runtime.
- Do **not** add a `VOLUME` directive — it wipes the directory in subsequent layers.
- Keep `.git/` available (do not delete it). The harness resets to `base_commit` using git.
- If the base image declares a `HEALTHCHECK`, override it: `HEALTHCHECK NONE`.
- If the base image does not have `git` installed, add: `RUN apt-get install -y --no-install-recommends git`.
- Pin all package versions explicitly. Do not use `latest` tags.

---

## `task.toml` — Metadata

```toml
[metadata]
author_name = "<your name>"
author_email = "<your email>"
difficulty = "hard"          # easy | medium | hard
category = "security"        # security | bug | feature | refactor | performance
tags = ["security", "authentication", "access-control"]
human_solve_time = ""        # leave blank if unknown
requires_internet = false
repo_type = ""
task_type = ""
verifier_runtime_sec = 0

[verifier]
timeout_sec = 3000

[agent]
timeout_sec = 3600

[environment]
build_timeout_sec = 1800.0
cpus = 1
memory_mb = 4096
storage_mb = 10240
```

Set `difficulty` to match the expected pass rate (1–4 out of 10 strong agents). Set `category` and `tags` accurately. Do not leave placeholder values.

---

## Difficulty Target

Aim for tasks where roughly **1 to 4 of 10** strong-agent attempts succeed:

- Hard enough that a quick Sonnet-style pass is unlikely to solve it from obvious search results or a one-line fix.
- Fair enough that a strong Opus-style agent can solve it in some runs by reasoning from the instruction and the repository.

Difficulty must come from the repository problem itself: cross-file reasoning, subtle edge cases, integration behavior, compatibility constraints, or non-obvious root cause. Do not manufacture difficulty by making instructions vague, breaking the test setup, or hiding essential information.

---

## Difficulty Calibration

The 1–4/10 window is narrow. Check both failure modes before submitting.

**Too easy (≥5/10) — warning signs:**
- The fix is a single line: one import added, one boolean flipped, one config key renamed, with no cross-file effect.
- The instruction describes the expected change so specifically that the correct code is largely dictated — "add a check that returns 401 before line X" is not a task, it's a recipe.
- A grep search for a key term from the instruction returns the exact file and line that needs editing in ≤3 tries.
- Every F2P test covers the same single code path — no cross-module interaction or multi-step reasoning required.
- The existing failing test (before the fix) already has a comment explaining the root cause.

**Too hard (0/10) — warning signs:**
- The fix is in a file that is not hinted at by the instruction *and* cannot be discovered by tracing from the repo entry point in under 5 file hops.
- The instruction uses an ambiguous term and the only way to know the exact expected behavior is to read the verifier test.
- The tests expect behavior that contradicts one reasonable interpretation of the instruction.
- No existing test in the repo exercises the relevant code path; the verifier tests are the first time the behavior runs at all.
- The bug only manifests under a runtime condition (race, env variable, specific Docker network) that can't be reproduced by normal test execution at `base_commit`.

**Recommended F2P count:** 4–8 tests. Fewer than 4 means one lucky patch may satisfy them all by coincidence; more than 10 turns the task into a marathon and adds no meaningful signal about the agent's understanding.

**Self-test before submitting:** Read the instruction once and honestly ask two questions:
1. "Could a strong developer, unfamiliar with this repo, identify the root cause and plan a fix in under two minutes?" — If yes, the task is probably too easy.
2. "Could they write working code that satisfies the instruction in 30 minutes with only the repo and the instruction?" — If no, the task is probably unsolvable.

Target: root cause takes 5–15 minutes to isolate, correct fix takes another 10–20 minutes to implement and verify.

**When the first version is too easy**, apply the hardening patterns in `.github/instructions/make_a_task_hard.instructions.md`: add fixture depth, split broad tests into focused assertions, cover cross-module edge cases. Do not add difficulty by making the instruction vaguer — that converts a too-easy task into a broken one.

**After the difficulty probe**, if the score is outside 1–4/10, use `silver_instruction/difficulty_band_repair.instructions.md` to diagnose and fix the specific gap — it covers both the too-hard (0/10) and too-easy (≥5/10) directions.

---

## Fairness Review

Before zipping, read the instruction from an agent's perspective and look for failure modes:

- **Ambiguous terms:** words like "malformed", "invalid", "stale", "duplicate", "canonical", "normalized", or "authenticated" — does the instruction define exactly what these mean for any test that depends on the distinction?
- **Over-constrained tests:** does a test require stricter behavior than the instruction specifies?
- **Underspecified contract:** would many reasonable implementations fail because the instruction left something undefined?
- **Solution-leaking tests:** do test names or failure messages reveal the exact fix?
- **Hidden-knowledge dependency:** would an agent need access to information not in the instruction or the repo to solve the task?

When fairness risk is high, update the instruction **and** the tests together. Never fix fairness by making the instruction vaguer — that just makes the task worse.

---

## Quality Criteria (Self-Review Before Submission)

1. **Verifiable:** tests produce a clear deterministic pass/fail signal.
2. **Well specified:** a senior engineer can implement the expected outcome from `instruction.md` alone.
3. **Solvable:** the task is achievable in the repository within the agent time budget.
4. **Genuinely difficult:** the hard part is real reasoning, not vague wording or broken tests.
5. **Behavioral verification:** tests execute code and check observable outcomes.
6. **Outcome oriented:** instructions say what to accomplish, not how to code it.
7. **Test-instruction alignment:** every tested behavior is described in the instruction; every described behavior is tested.
8. **Human-register instruction:** concise, plain English, no AI-assistant prose patterns.
9. **Fair:** no insider knowledge, hidden assumptions, or unspecified edge cases.
10. **Anti-cheat robustness:** hardcoding output, monkey-patching, or fake wrappers must not pass.
11. **Deterministic:** repeated runs on the same repo state produce the same result.
12. **Verifier plumbing correct:** `test.sh` writes reward before any crashable command; `run_script.sh` and `parser.py` produce correct output.
13. **Metadata valid:** `task.toml` has real difficulty, timeouts, resources, category, and tags.
14. **Dockerfile correct:** approved base image, `base_commit` reset, reproducible installs, no placeholder paths, no `VOLUME`, `/logs/verifier` pre-created.
15. **No platform leakage:** `instruction.md` contains no internal reviewer notes, assessment mechanics, or platform-specific prose.

---

## Validation Gates (In Order)

| Gate | What it checks | Common failure |
|------|---------------|----------------|
| AI text check | `instruction.md` reads like human writing | "AI-register" prose; over-polished bullet hierarchy |
| Quality review | Substantive, follows spec | Trivial fix; vague instruction |
| Image build | Dockerfile builds successfully | `.git` in `.dockerignore`; missing `git` in base image |
| Nop check | Tests fail as expected without any fix applied | `test_patch` adds 0 tests; F2P tests pass at base commit |
| Oracle check | `solve.sh` makes all tests pass | `RewardFileNotFoundError`; `ModuleNotFoundError`; VOLUME wipes repo |
| Difficulty assessment | Pass rate 1–4 out of 10 agents | Too hard (0/10) or too easy (5+/10) |

---

## Rejection Classes

| Issue | What it means | Fix |
|-------|--------------|-----|
| **Q1 solution-inject** | Verifier applies the gold solution before scoring — every run passes regardless of agent output | Remove the solution-applying step from the verifier; grade only agent changes |
| **Q1 oracle-gate** | Reward is keyed off a flag file rather than test results | Drop the flag-file branch; let test pass/fail decide the reward directly |
| **F2P/P2P mismatch** | `fail_to_pass` tests don't flip to passing when the gold solution is applied | Align solution with tests; fix `config.json` and re-verify locally |

---

## Common Verifier Errors

### RewardFileNotFoundError

`Trials: 0 + RewardFileNotFoundError` — the reward file was never written. This is always a plumbing issue, not a correctness issue.

**Dockerfile fix** — pre-create the file at build time:
```dockerfile
RUN mkdir -p /logs/verifier \
  && echo 0 > /logs/verifier/reward.txt \
  && chmod -R 0777 /logs
```

**`test.sh` fix** — install the EXIT trap before any command that can crash:
```bash
mkdir -p /logs/verifier && echo 0 > /logs/verifier/reward.txt
cleanup() { [ $? -eq 0 ] && echo 1 || echo 0 > /logs/verifier/reward.txt; }
trap cleanup EXIT
```

Also check: `.git` in `.dockerignore` silently breaks git operations so the test never runs and the file is never written.

### RuntimeError / NonZeroAgentExitCodeError

| Cause | Fix |
|-------|-----|
| Base image has `VOLUME` on the repo path — wipes everything in subsequent layers | Remove `VOLUME` directive, or copy repo to a non-VOLUME path |
| `HEALTHCHECK` inherited from base image causes timeout | Add `HEALTHCHECK NONE` to Dockerfile |
| `git` not in base image | Add `RUN apt-get install -y --no-install-recommends git` |
| `solve.sh` crashes before writing reward | See `RewardFileNotFoundError` — reward must be written by `test.sh`, not `solve.sh` |

### ModuleNotFoundError: No module named 'app'

Pytest cannot find the package. Fix with:
- Add `conftest.py` at repo root
- `pip install -e .` in Dockerfile
- Set `PYTHONPATH=/app` in test command or Dockerfile `ENV`

### test_patch adds 0 tests

| Cause | Fix |
|-------|-----|
| Test functions don't start with `test_` | Rename — pytest requires `test_` prefix for discovery |
| Missing `__init__.py` in `tests/` | Add it |
| Patch is empty diff vs base commit | Run `git diff <base_commit> -- tests/` locally to verify the diff has content |
| Used the in-website editor to paste patch | Use the import function instead — the editor strips patches |
| Syntax error in test file | File fails to import; harness sees zero tests |
| JS/TS repo — test runner not configured | Confirm Jest/Vitest is installed and `run_script.sh` uses the right command |

Quickest debug: apply your `test_patch` locally and run `git diff <base_commit> -- tests/` — that output is exactly what the platform will apply.

---

## Before Zipping — Final Checklist

Run the single presubmit gate. It executes all checks and only writes the zip if everything passes:

```bash
# Runs all 6 gates in order and zips the task if they all pass
bash silver_instruction/presubmit_gate.sh "<task-dir>"

# If the repo lives outside ~/repos, point the script to it:
SILVER_REPO_ROOT=/path/to/repos bash silver_instruction/presubmit_gate.sh "<task-dir>"

# To skip oracle/nop sim (e.g. repo not available locally):
SKIP_SIM=1 bash silver_instruction/presubmit_gate.sh "<task-dir>"
```

The gate runs these steps automatically:

```
1. Static quality check  (silver_quality_check.sh)
2. Fairness check        (silver_fairness_check.sh)
3. Similarity check      (silver_similarity_check.sh)
4. Oracle simulation     — all F2P + P2P tests PASS with fix applied
5. Nop simulation        — F2P tests FAIL, P2P tests PASS without fix
6. Zip task              — writes <task-name>.zip if all gates pass
```

Only the zip produced by `presubmit_gate.sh` when all gates show **✓ PASS** is ready for upload. If any gate fails, the zip is not written and the task must be fixed first.

Individual manual steps (if you need to debug a specific gate):

```bash
# Oracle simulation
git -C "<repo-dir>" reset --hard "<base_commit>" && git -C "<repo-dir>" clean -fd
git -C "<repo-dir>" apply /tmp/test_patch.diff        # from tests/config.json
git -C "<repo-dir>" apply /tmp/solution.diff          # the fix from solve.sh
cd "<repo-dir>" && npx jest --verbose --forceExit     # all PASS → oracle OK

# Nop simulation
git -C "<repo-dir>" reset --hard "<base_commit>" && git -C "<repo-dir>" clean -fd
git -C "<repo-dir>" apply /tmp/test_patch.diff        # verifier tests only
cd "<repo-dir>" && npx jest --verbose --forceExit     # F2P FAIL, P2P PASS → nop OK
```

Only submit when all of these are true:

- [ ] **Oracle sim:** apply test_patch + solution → all F2P and P2P tests PASS
- [ ] **Nop sim:** apply test_patch only, no fix → every F2P test FAILS, every P2P test PASSES
- [ ] `fail_to_pass` is larger than `pass_to_pass` (where practical)
- [ ] `instruction.md`, `reference_plan.md`, `task.toml`, `Dockerfile`, `solve.sh`, and `config.json` are all aligned
- [ ] `instruction.md` has no platform prose, reviewer notes, or test-implementation hints
- [ ] Dockerfile uses the exact approved base image with digest pinning
- [ ] No `node_modules/`, `.pytest_cache/`, build outputs, logs, or generated archives in the zip
- [ ] Task name is unique, descriptive, and uses only `[a-z0-9._-]`
- [ ] `silver_fairness_check.sh` passes (no FAIL)
- [ ] `silver_similarity_check.sh` passes (no hard block)
- [ ] `presubmit_gate.sh` exits 0 and the zip file has been written

---

## Platform Limits (Tasks)

- **Max 5 Opus/DIFFICULTY_CHECK runs per task.** Each costs ~$5. Debug locally first. Running on the server without local validation is wasteful and against project rules.
- **Max 20 tasks per repo.** No more than 5 tasks per repo should be similar in nature — diversify across bug fix, feature, security, refactor, and performance categories.
- **Validate locally first.** Replicate any platform error locally before posting for help.
