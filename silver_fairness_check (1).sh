#!/usr/bin/env bash
set -euo pipefail

# Silver SWE-bench — Fairness Review Script
# Checks whether a task's instruction.md is fair to agents: no hidden knowledge,
# no ambiguous tested terms, no over-constrained tests, no solution-leaking output.
#
# Usage:
#   bash silver_fairness_check.sh <task-dir>
#
# Exit codes:
#   0  — no blocking issues found (warnings may still appear)
#   1  — one or more FAIL-level fairness issues detected
#   2  — usage error

usage() {
  cat <<'EOF'
Usage: bash silver_fairness_check.sh <task-dir>

Runs fairness checks on a Silver task. Checks that:
  - instruction.md defines every ambiguous term that tests depend on
  - tests do not assert implementation structure instead of behavior
  - test names and error messages do not leak the exact solution
  - instruction.md covers every behavioral surface tested by fail_to_pass
  - pass_to_pass behaviors are mentioned in the instruction
  - no hidden-knowledge assumptions are required to solve the task
  - instruction register is human (no AI-assistant prose patterns)
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 1 ]]; then
  usage
  exit 2
fi

TASK_DIR="${1%/}"

fail() { printf 'FAIL: %s\n' "$*" >&2; FAIL_COUNT=$((FAIL_COUNT + 1)); }
warn() { printf 'WARN: %s\n' "$*"; WARN_COUNT=$((WARN_COUNT + 1)); }
pass() { printf 'PASS: %s\n' "$*"; }

FAIL_COUNT=0
WARN_COUNT=0

[[ -d "$TASK_DIR" ]] || { echo "error: task directory does not exist: $TASK_DIR" >&2; exit 2; }
[[ -f "$TASK_DIR/instruction.md" ]] || { echo "error: instruction.md missing" >&2; exit 2; }
[[ -f "$TASK_DIR/tests/config.json" ]] || { echo "error: tests/config.json missing" >&2; exit 2; }

python3 - "$TASK_DIR" <<'PY'
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
fail_items: list[str] = []
warn_items: list[str] = []

instruction = (root / "instruction.md").read_text(encoding="utf-8", errors="replace")
config = json.loads((root / "tests/config.json").read_text(encoding="utf-8", errors="replace"))

fail_to_pass: list[str] = config.get("fail_to_pass", [])
pass_to_pass: list[str] = config.get("pass_to_pass", [])
test_patch: str = config.get("test_patch", "")

# -------------------------------------------------------------------------
# 1. Ambiguous term definitions
# -------------------------------------------------------------------------
# Terms that are commonly tested but require an explicit definition to be fair.
AMBIGUOUS_TERMS = [
    ("malformed",      r"\bmalformed\b"),
    ("invalid",        r"\binvalid\b"),
    ("stale",          r"\bstale\b"),
    ("duplicate",      r"\bduplicate\b"),
    ("canonical",      r"\bcanonical\b"),
    ("normalized",     r"\bnormalized?\b"),
    ("unauthenticated",r"\bunauthenticated\b"),
    ("authenticated",  r"\bauthenticated\b"),
    ("expired",        r"\bexpired?\b"),
    ("corrupted",      r"\bcorrupted?\b"),
    ("truncated",      r"\btruncated?\b"),
]

# Phrases that count as a definition or clarification nearby
DEFINITION_PATTERNS = [
    r"means\b", r"defined as\b", r"defined by\b",
    r"for example", r"such as", r"including", r"specifically",
    r"treat(ed)? as", r"consider(ed)?( as)?",
    r"for (this|the) (task|purpose)",
    r"in (this|the) context",
    r"must (be|include|contain|return|reject|accept)",
]
DEF_RE = re.compile("|".join(DEFINITION_PATTERNS), re.I)

for label, pattern in AMBIGUOUS_TERMS:
    if re.search(pattern, instruction, re.I):
        # Check that a clarification exists nearby (within 300 chars)
        for m in re.finditer(pattern, instruction, re.I):
            context = instruction[max(0, m.start()-50) : m.end()+300]
            if DEF_RE.search(context):
                break
        else:
            warn_items.append(
                f"instruction.md uses '{label}' but does not define it — "
                f"tests that distinguish '{label}' inputs require an explicit definition"
            )

# -------------------------------------------------------------------------
# 2. Test names leaking solution
# -------------------------------------------------------------------------
SOLUTION_LEAK_PATTERNS = [
    r"\bgit apply\b", r"\bgit reset\b", r"\bpatch\b.*apply",
    r"\bsolution\.patch\b", r"\bsolve\.sh\b",
    r"\bsecret\b", r"\bhidden\b", r"\bflag file\b",
]
for name in fail_to_pass + pass_to_pass:
    for pat in SOLUTION_LEAK_PATTERNS:
        if re.search(pat, name, re.I):
            fail_items.append(
                f"test name leaks solution details: '{name}' (pattern: {pat})"
            )

# -------------------------------------------------------------------------
# 3. test_patch checks for structural (non-behavioral) assertions
# -------------------------------------------------------------------------
STRUCTURAL_PATTERNS = [
    (r"open\(['\"].*?['\"].*?\).*?assert", "file read + assert (possible source scan)"),
    (r"read_text\([^)]*\).*?assert",        "read_text + assert (possible source scan)"),
    (r"subprocess.*grep",                   "grep in test (source text scan)"),
    (r"ast\.parse|inspect\.",               "AST/inspect usage (may assert implementation structure)"),
    (r"re\.search.*import|import.*re\.search", "regex scan on source imports"),
]
for pat, label in STRUCTURAL_PATTERNS:
    if re.search(pat, test_patch, re.I | re.S):
        warn_items.append(
            f"test_patch may assert implementation structure rather than behavior: {label}"
        )

# -------------------------------------------------------------------------
# 4. fail_to_pass test surface vs instruction coverage
# -------------------------------------------------------------------------
# Extract meaningful keywords from test names and check they appear in instruction.
def keywords_from_test_name(name: str) -> list[str]:
    # Strip file path prefix (e.g. "test_auth.test.ts::")
    parts = re.split(r"::", name)
    label_parts = parts[-1] if len(parts) > 1 else name
    # Strip describe prefix separated by " > "
    label_parts = label_parts.split(" > ")[-1]
    words = re.findall(r"[a-z][a-z0-9_]{3,}", label_parts.lower())
    skip = {"test", "that", "with", "should", "when", "returns", "given",
            "after", "before", "does", "have", "been", "will", "from"}
    return [w for w in words if w not in skip]

coverage_gaps: list[str] = []
for name in fail_to_pass:
    kws = keywords_from_test_name(name)
    uncovered = [kw for kw in kws if kw not in instruction.lower()]
    if len(uncovered) >= 2:
        coverage_gaps.append(f"  F2P '{name}' keywords not found in instruction.md: {uncovered[:4]}")

if coverage_gaps:
    fail_items.append(
        "instruction.md does not appear to cover all tested F2P behaviors:\n" + "\n".join(coverage_gaps)
    )

# -------------------------------------------------------------------------
# 5. AI-register patterns in instruction
# -------------------------------------------------------------------------
AI_PHRASES = [
    r"\bleverage\b", r"\butilize\b", r"\bseamlessly\b", r"\brobust(ly)?\b",
    r"\bensure that\b", r"\bplease note\b", r"\bplease ensure\b",
    r"\bit is important to\b", r"\bit is worth noting\b",
    r"\bproactively\b", r"\boptimally\b", r"\bcomprehensively\b",
    r"\bactionable\b", r"\bsynergize\b", r"\bparadigm\b",
    r"\bstate-of-the-art\b", r"\bbest practices\b",
]
ai_hits = [pat for pat in AI_PHRASES if re.search(pat, instruction, re.I)]
if ai_hits:
    warn_items.append(
        "instruction.md contains AI-assistant prose patterns that may trigger the AI text check: "
        + ", ".join("'" + p.replace(r"\b", "") + "'" for p in ai_hits[:5])
    )

# -------------------------------------------------------------------------
# 6. Hidden-knowledge or platform-internal references
# -------------------------------------------------------------------------
HIDDEN_KNOWLEDGE = [
    (r"/logs/verifier",           "verifier path exposed to agent"),
    (r"reward\.txt",              "reward file path exposed to agent"),
    (r"test_patch",               "test_patch field name exposed to agent"),
    (r"fail_to_pass|pass_to_pass","config field names exposed to agent"),
    (r"solver|solve\.sh",         "solution file referenced in instruction"),
    (r"parser\.py|run_script",    "verifier script referenced in instruction"),
    (r"silver pipeline|aq server|project silver", "internal platform prose in instruction"),
    (r"harbor-canary guid",       "internal canary GUID in instruction"),
]
for pat, label in HIDDEN_KNOWLEDGE:
    if re.search(pat, instruction, re.I):
        fail_items.append(f"instruction.md contains {label}: /{pat}/")

# -------------------------------------------------------------------------
# 7. Over-constrained tests (test asserts more than instruction states)
# -------------------------------------------------------------------------
# Check: if a test name contains "exactly N" or "must return X", verify
# the instruction specifies the same exact value.
EXACT_VALUE_RE = re.compile(r"\b(exactly|must return|must be|equal to)\s+[\"']?([0-9]+|[A-Z_]{3,})[\"']?", re.I)
for name in fail_to_pass:
    m = EXACT_VALUE_RE.search(name)
    if m:
        value = m.group(2)
        if value not in instruction and value.lower() not in instruction.lower():
            warn_items.append(
                f"test name constrains exact value '{value}' but instruction may not specify it: '{name}'"
            )

# -------------------------------------------------------------------------
# 8. pass_to_pass coverage in instruction
# -------------------------------------------------------------------------
p2p_gaps: list[str] = []
for name in pass_to_pass:
    kws = keywords_from_test_name(name)
    uncovered = [kw for kw in kws if kw not in instruction.lower()]
    if len(uncovered) >= 3:
        p2p_gaps.append(f"  P2P '{name}' keywords not found in instruction.md: {uncovered[:4]}")
if p2p_gaps:
    warn_items.append(
        "instruction.md may not describe the regression expectations covered by pass_to_pass:\n"
        + "\n".join(p2p_gaps)
    )

# -------------------------------------------------------------------------
# 9. Instruction length and structure sanity
# -------------------------------------------------------------------------
if len(instruction.strip()) < 300:
    fail_items.append(
        "instruction.md is very short (<300 chars). A senior engineer must be able to "
        "implement the solution from this alone."
    )
elif len(instruction.strip()) < 600:
    warn_items.append("instruction.md is short; verify all tested behaviors and edge cases are described")

# Check for giant stack traces/config dumps
if re.search(r"(?:Traceback|at .+:\d+|stack frame)", instruction, re.I):
    warn_items.append(
        "instruction.md may contain a stack trace; trim to only the excerpt needed to understand the bug"
    )

# -------------------------------------------------------------------------
# Output results
# -------------------------------------------------------------------------
if fail_items:
    for item in fail_items:
        print(f"FAIL: {item}")
if warn_items:
    for item in warn_items:
        print(f"WARN: {item}")
if not fail_items and not warn_items:
    print("All fairness checks passed — no issues found.")
if fail_items:
    sys.exit(1)
sys.exit(0)
PY

EXIT_CODE=$?
if [[ $EXIT_CODE -eq 0 ]]; then
  pass "Fairness check completed for $TASK_DIR"
else
  echo "FAIL: Fairness check found blocking issues in $TASK_DIR" >&2
  exit 1
fi
