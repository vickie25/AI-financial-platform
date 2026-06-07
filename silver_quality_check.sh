#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash silver_quality_check.sh <task-dir>

Runs local static quality checks for a Silver SWE-bench task.

NOTE: Silver tasks use a private AQ base image and cannot be validated with
'harbor run' locally. After this static check passes, validate manually:

  # Step 1 — oracle simulation: apply patch, run tests, all must PASS
  git -C <repo-dir> reset --hard <base_commit> && git -C <repo-dir> clean -fd
  git -C <repo-dir> apply <solution-diff>            # or run solution/solve.sh
  cd <repo-dir> && <test-command>                    # all tests must pass

  # Step 2 — nop simulation: reset, run tests without patch
  git -C <repo-dir> reset --hard <base_commit> && git -C <repo-dir> clean -fd
  # Apply test_patch from tests/config.json
  cd <repo-dir> && <test-command>
  # fail_to_pass tests must FAIL; pass_to_pass tests must PASS
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

TASK_DIR="${1%/}"

if [[ $# -gt 1 ]]; then
  echo "Unknown argument: ${2}" >&2
  usage
  exit 2
fi

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

warn() {
  printf 'WARN: %s\n' "$*" >&2
}

pass() {
  printf 'PASS: %s\n' "$*"
}

need_file() {
  [[ -f "$TASK_DIR/$1" ]] || fail "missing required file: $1"
}

need_dir() {
  [[ -d "$TASK_DIR/$1" ]] || fail "missing required directory: $1"
}

[[ -d "$TASK_DIR" ]] || fail "task directory does not exist: $TASK_DIR"

need_file instruction.md
need_file reference_plan.md
need_file task.toml
need_file environment/Dockerfile
need_file solution/solve.sh
need_file tests/test.sh
need_file tests/run_script.sh
need_file tests/parser.py
need_file tests/config.json
need_dir tests

bash -n "$TASK_DIR/solution/solve.sh" || fail "solution/solve.sh has shell syntax errors"
bash -n "$TASK_DIR/tests/test.sh" || fail "tests/test.sh has shell syntax errors"
bash -n "$TASK_DIR/tests/run_script.sh" || fail "tests/run_script.sh has shell syntax errors"
pass "shell scripts parse"

python -m py_compile "$TASK_DIR/tests/parser.py" || fail "tests/parser.py does not compile"
find "$TASK_DIR/tests" -maxdepth 1 -type f -name '*.py' -print0 | while IFS= read -r -d '' pyfile; do
  python -m py_compile "$pyfile" || exit 1
done
pass "python verifier files compile"

python - "$TASK_DIR" <<'PY'
import json
import pathlib
import re
import sys
import tomllib

root = pathlib.Path(sys.argv[1])
errors = []
warnings = []

def text(rel):
    return (root / rel).read_text(encoding="utf-8", errors="replace")

try:
    toml_data = tomllib.loads(text("task.toml"))
except Exception as exc:
    errors.append(f"task.toml is not valid TOML: {exc}")
    toml_data = {}

metadata = toml_data.get("metadata", {})
difficulty = metadata.get("difficulty")
if difficulty not in {"easy", "medium", "hard"}:
    errors.append("task.toml metadata.difficulty must be easy, medium, or hard")

for section in ("verifier", "agent", "environment"):
    if section not in toml_data:
        errors.append(f"task.toml missing [{section}] section")

for section, key in (("verifier", "timeout_sec"), ("agent", "timeout_sec")):
    value = toml_data.get(section, {}).get(key)
    if not isinstance(value, (int, float)) or value <= 0:
        errors.append(f"task.toml [{section}].{key} must be positive")

env = toml_data.get("environment", {})
for key in ("build_timeout_sec", "cpus", "memory_mb", "storage_mb"):
    value = env.get(key)
    if not isinstance(value, (int, float)) or value <= 0:
        errors.append(f"task.toml [environment].{key} must be positive")

for suspicious in ("verifier_runtime_sec",):
    if suspicious in toml_data or any(isinstance(v, dict) and suspicious in v for v in toml_data.values()):
        warnings.append(f"task.toml contains unusual field {suspicious}; remove it unless the template requires it")

try:
    config = json.loads(text("tests/config.json"))
except Exception as exc:
    errors.append(f"tests/config.json is not valid JSON: {exc}")
    config = {}

base_commit = config.get("base_commit")
if not isinstance(base_commit, str) or not re.fullmatch(r"[0-9a-fA-F]{7,40}", base_commit):
    errors.append("tests/config.json base_commit must be a 7-40 character hex string")

for key in ("fail_to_pass", "pass_to_pass", "selected_test_files_to_run"):
    value = config.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"tests/config.json {key} must be a list of non-empty strings")

if not config.get("fail_to_pass"):
    errors.append("tests/config.json fail_to_pass must be non-empty")
elif isinstance(config.get("pass_to_pass"), list) and len(config["fail_to_pass"]) <= len(config["pass_to_pass"]):
    errors.append("fail_to_pass must contain more tests than pass_to_pass (F2P set should be the larger one)")

test_patch = config.get("test_patch")
if not isinstance(test_patch, str) or not test_patch.strip():
    errors.append("tests/config.json test_patch must be a non-empty unified diff string")
elif "diff --git" not in test_patch and "--- " not in test_patch:
    warnings.append("tests/config.json test_patch does not look like a unified diff")

instruction = text("instruction.md")
reference = text("reference_plan.md")
dockerfile = text("environment/Dockerfile")
solve = text("solution/solve.sh")
test_sh = text("tests/test.sh")
run_script = text("tests/run_script.sh")
parser = text("tests/parser.py")
all_authoring_text = "\n".join([instruction, reference, dockerfile, solve, test_sh, run_script, parser])

# --- instance_id check ---
instance_id = config.get("instance_id", "")
if not instance_id or instance_id.startswith("<") or "instance_" not in instance_id:
    errors.append("tests/config.json instance_id must be set (pattern: instance_<author>__<repo>-<hash>-<slug>)")

# --- placeholder checks ---
for placeholder_field in ("patch", "problem_statement"):
    val = config.get(placeholder_field, "")
    if not isinstance(val, str) or (val and not val.startswith("<")):
        warnings.append(f"tests/config.json '{placeholder_field}' should be the auto-derived placeholder string; do not fill it manually")

if not config.get("selected_test_files_to_run"):
    errors.append("tests/config.json selected_test_files_to_run must be non-empty")

if len(instruction.strip()) < 400:
    warnings.append("instruction.md is quite short; ensure all tested behavior and edge cases are specified")

for banned in ("new_task.instruction", "CLAUDE.md"):
    if banned.lower() in all_authoring_text.lower():
        errors.append(f"task files contain project-specific authoring text: {banned}")

for leak in ("Project Silver", "Silver pipeline", "assessment page", "expert role", "difficulty probe"):
    if leak.lower() in instruction.lower():
        errors.append(f"instruction.md appears to leak internal platform/review language: {leak}")

if re.search(r"\b(grep|regex|source\s+scan|scan\s+source)\b", instruction, re.I):
    warnings.append("instruction.md mentions source scanning; verify tests are behavior-based")

if "git apply" not in solve:
    warnings.append("solution/solve.sh does not mention git apply; confirm it applies a real patch at base_commit")

if "/logs/verifier/reward.txt" not in test_sh:
    errors.append("tests/test.sh must write /logs/verifier/reward.txt")

if not re.search(r"trap\b.*EXIT", test_sh):
    errors.append("tests/test.sh must install an EXIT trap to write reward.txt before any crashable command")

if not re.search(r"echo\s+1\s*>\s*/logs/verifier/reward.txt", test_sh):
    warnings.append("tests/test.sh may not write reward 1 on success")

if not re.search(r"echo\s+0\s*>\s*/logs/verifier/reward.txt", test_sh):
    warnings.append("tests/test.sh may not write reward 0 on failure")

from_lines = [line for line in dockerfile.splitlines() if line.strip().upper().startswith("FROM ")]
if not from_lines:
    errors.append("environment/Dockerfile missing FROM line")
else:
    first_from = from_lines[0].split()
    image = first_from[1] if len(first_from) > 1 else ""
    if image and ":" not in image and "@" not in image and image != "scratch":
        errors.append("environment/Dockerfile FROM image must be pinned by tag or digest")

if re.search(r"apt-get\s+install(?![^\n]*--no-install-recommends)", dockerfile):
    errors.append("environment/Dockerfile apt-get install must use --no-install-recommends")

if re.search(r"^\s*VOLUME\b", dockerfile, re.MULTILINE):
    errors.append("environment/Dockerfile must not declare VOLUME — it wipes the repo directory in subsequent layers")

if not re.search(r"mkdir\s+-p\s+/logs/verifier", dockerfile):
    errors.append("environment/Dockerfile must pre-create /logs/verifier (RUN mkdir -p /logs/verifier)")

if re.search(r"\bCOPY\b.*\b(tests|solution|jobs|logs)\b", dockerfile, re.I):
    warnings.append("environment/Dockerfile appears to copy verifier or solution material")

if "TODO" in all_authoring_text or "PLACEHOLDER" in all_authoring_text:
    errors.append("task files contain TODO or PLACEHOLDER text")

ambiguous_terms = ["malformed", "invalid", "stale", "duplicate", "canonical", "normalized", "unauthenticated"]
for term in ambiguous_terms:
    if re.search(rf"\b{re.escape(term)}\b", instruction, re.I):
        nearby = re.search(rf"\b{re.escape(term)}\b(.{{0,180}})(means|defined as|for example|such as|including|must)", instruction, re.I | re.S)
        if not nearby:
            warnings.append(f"instruction.md uses '{term}'; ensure tests do not rely on an unstated exact definition")

test_files = [p for p in (root / "tests").glob("*") if p.is_file()]
test_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in test_files)
if re.search(r"\bgrep\b|read_text\([^)]*\).*assert|open\([^)]*\).*assert", test_text, re.I | re.S):
    warnings.append("tests may inspect source text; confirm this is necessary and behavior cannot be tested instead")

missing_mentions = []
for rel in config.get("selected_test_files_to_run", []) if isinstance(config.get("selected_test_files_to_run"), list) else []:
    name = pathlib.PurePosixPath(rel).name
    if name and name not in test_patch and not (root / "tests" / name).exists():
        missing_mentions.append(rel)
if missing_mentions:
    warnings.append("selected test files are not present locally and not obvious in test_patch: " + ", ".join(missing_mentions))

if errors:
    for item in errors:
        print(f"ERROR: {item}")
if warnings:
    for item in warnings:
        print(f"WARN: {item}")
if errors:
    sys.exit(1)
PY
pass "task metadata and authoring text checks passed"

if command -v git >/dev/null 2>&1; then
  BASE_COMMIT="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["base_commit"])' "$TASK_DIR/tests/config.json")"
  if git -C "$TASK_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$TASK_DIR" cat-file -e "${BASE_COMMIT}^{commit}" 2>/dev/null || warn "base_commit not found from task directory git context: $BASE_COMMIT"
  else
    warn "task directory is not inside a git worktree; skipped base_commit existence check"
  fi
fi

pass "Silver quality check completed for $TASK_DIR"

cat <<'MSG'

Next step — local validation (Silver tasks cannot use 'harbor run' locally):
  See 'bash silver_quality_check.sh --help' for the manual oracle/nop simulation steps.
MSG
