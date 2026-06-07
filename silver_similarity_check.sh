#!/usr/bin/env bash
set -euo pipefail

# Silver SWE-bench — Similarity Check Script
# Detects task overlap across Silver task directories in the workspace.
# Compares instruction.md content, test_patch, category/tags, and touched files.
#
# Usage:
#   bash silver_similarity_check.sh <task-dir> [threshold_percent] [--scan-dir <dir>]
#
# Examples:
#   bash silver_similarity_check.sh silver_instruction/my-new-task
#   bash silver_similarity_check.sh silver_instruction/my-new-task 20
#   bash silver_similarity_check.sh my-task 25 --scan-dir /other/silver/tasks
#
# Exit codes:
#   0  — no similarity issues found
#   1  — similarity threshold exceeded (task should be reworked)
#   2  — usage error

usage() {
  cat <<'EOF'
Usage: bash silver_similarity_check.sh <task-dir> [threshold_percent] [--scan-dir <dir>]

Compares <task-dir> against all other Silver task directories found alongside it
(or in <scan-dir>) for content similarity.

Arguments:
  task-dir           Path to the Silver task directory to check.
  threshold_percent  Similarity threshold (default: 25). Tasks above this score
                     are flagged as too similar. Platform rejects at cosine ≥ 0.75
                     (roughly corresponds to ~35%+ in this tool's scoring).
  --scan-dir <dir>   Search for other tasks in this directory instead of the
                     parent of task-dir.

The check compares:
  - instruction.md  (weighted highest — this is what agents and reviewers read)
  - test_patch      (shared test surface suggests shared bug class)
  - task.toml tags  (same tag cluster = same category = possible overlap)
  - Dockerfile      (same base image + same files touched = likely same bug area)
  - solve.sh        (shared diff fragments = shared root cause)

Output: similarity score from 0% (no overlap) to 100% (identical).
A score ≥ threshold is a HARD BLOCK. Scores ≥ 15% get a detail breakdown.
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
THRESHOLD="${2:-25}"
SCAN_DIR=""

# Parse optional --scan-dir
i=2
while [[ $i -le $# ]]; do
  arg="${!i}"
  if [[ "$arg" == "--scan-dir" ]]; then
    i=$((i + 1))
    SCAN_DIR="${!i}"
  elif [[ "$arg" =~ ^[0-9]+$ ]]; then
    THRESHOLD="$arg"
  else
    echo "Unknown argument: $arg" >&2
    usage
    exit 2
  fi
  i=$((i + 1))
done

if [[ ! -d "$TASK_DIR" ]]; then
  echo "error: task directory not found: $TASK_DIR" >&2
  exit 2
fi

if [[ ! -f "$TASK_DIR/instruction.md" || ! -f "$TASK_DIR/tests/config.json" ]]; then
  echo "error: $TASK_DIR does not look like a Silver task (missing instruction.md or tests/config.json)" >&2
  exit 2
fi

if [[ -z "$SCAN_DIR" ]]; then
  SCAN_DIR="$(dirname "$(realpath "$TASK_DIR")")"
fi

python3 - "$TASK_DIR" "$SCAN_DIR" "$THRESHOLD" <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

target = Path(sys.argv[1]).resolve()
scan_dir = Path(sys.argv[2]).resolve()
threshold = float(sys.argv[3])

# -------------------------------------------------------------------------
# File inclusion rules
# -------------------------------------------------------------------------
SKIP_PARTS = {".git", ".pytest_cache", "__pycache__", "jobs", "node_modules", "logs"}
TEXT_SUFFIXES = {".md", ".sh", ".py", ".toml", ".json", ".ts", ".tsx", ".js", ".go", ".rs"}
TEXT_FILENAMES = {"Dockerfile"}

# Weight per file (higher = more influence on similarity score)
FILE_WEIGHTS: dict[str, float] = {
    "instruction.md": 0.55,     # heaviest — this is the agent-facing contract
    "tests/config.json": 0.15,  # test names + test_patch overlap is a strong signal
    "solution/solve.sh": 0.15,  # shared diff = shared root cause
    "environment/Dockerfile": 0.08,
    "task.toml": 0.05,
    "reference_plan.md": 0.02,
}

STOPWORDS = {
    "and", "are", "for", "from", "has", "have", "into", "must", "not",
    "only", "should", "that", "the", "this", "was", "will", "with",
    "any", "all", "can", "each", "its", "also", "when", "then", "than",
    # Silver-specific generic terms that appear in every task
    "instruction", "solution", "environment", "tests", "config", "patch",
    "task", "agent", "output", "input", "file", "path", "error", "test",
    "run", "base", "commit", "repo", "docker", "image", "fail", "pass",
    "behavior", "function", "return", "value", "check", "verify", "ensure",
}

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def normalize(text: str) -> str:
    text = text.lower()
    # Strip hash digests and UUIDs
    text = re.sub(r"sha256:[0-9a-f]{20,}", "sha256:<digest>", text)
    text = re.sub(r"[0-9a-f]{7,40}\b", "<hash>", text)
    text = re.sub(r"[0-9]{6,}", "<num>", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_silver_task(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "instruction.md").exists()
        and (path / "tests" / "config.json").exists()
    )


def read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def load_task_texts(task_dir: Path) -> dict[str, str]:
    """Load each weighted file. For config.json, extract instruction + test names."""
    texts: dict[str, str] = {}

    # Instruction — primary signal
    texts["instruction.md"] = normalize(read_file_safe(task_dir / "instruction.md"))

    # config.json — extract test names and test_patch (not the whole JSON structure)
    config_raw = read_file_safe(task_dir / "tests" / "config.json")
    if config_raw:
        try:
            cfg = json.loads(config_raw)
            test_names = cfg.get("fail_to_pass", []) + cfg.get("pass_to_pass", [])
            patch = cfg.get("test_patch", "")
            texts["tests/config.json"] = normalize(" ".join(test_names) + " " + patch)
        except Exception:
            texts["tests/config.json"] = normalize(config_raw)

    # solve.sh
    solve_path = task_dir / "solution" / "solve.sh"
    if solve_path.exists():
        texts["solution/solve.sh"] = normalize(read_file_safe(solve_path))

    # Dockerfile — strip base-image-specific GUIDs for comparison
    df_path = task_dir / "environment" / "Dockerfile"
    if df_path.exists():
        df_text = read_file_safe(df_path)
        df_text = re.sub(r"FROM\s+\S+", "FROM <image>", df_text)
        texts["environment/Dockerfile"] = normalize(df_text)

    # task.toml — just tags + category
    toml_path = task_dir / "task.toml"
    if toml_path.exists():
        toml_text = read_file_safe(toml_path)
        # Extract tags and category lines only
        tags_lines = [l for l in toml_text.splitlines()
                      if re.match(r"\s*(tags|category|difficulty)\s*=", l)]
        texts["task.toml"] = normalize(" ".join(tags_lines))

    # reference_plan.md
    ref_path = task_dir / "reference_plan.md"
    if ref_path.exists():
        texts["reference_plan.md"] = normalize(read_file_safe(ref_path))

    return texts


def word_tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9_./:-]{3,}", text) if w not in STOPWORDS]


def shingles(items: list[str], k: int) -> set[str]:
    if len(items) < k:
        return {" ".join(items)} if items else set()
    return {" ".join(items[i: i + k]) for i in range(len(items) - k + 1)}


def char_shingles(text: str, k: int = 9) -> set[str]:
    compact = re.sub(r"\s+", " ", text)
    if len(compact) < k:
        return {compact} if compact else set()
    return {compact[i: i + k] for i in range(len(compact) - k + 1)}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def important_terms(words: list[str]) -> set[str]:
    terms: set[str] = set()
    for w in words:
        for piece in re.split(r"[^a-z0-9]+", w):
            if len(piece) >= 4 and piece not in STOPWORDS and not piece.isdigit():
                terms.add(piece)
    return terms


def file_similarity(a_text: str, b_text: str) -> float:
    """Returns 0.0–1.0 similarity for two normalized file texts."""
    if not a_text.strip() and not b_text.strip():
        return 1.0
    if not a_text.strip() or not b_text.strip():
        return 0.0

    a_words = word_tokens(a_text)
    b_words = word_tokens(b_text)

    tok5 = jaccard(shingles(a_words, 5), shingles(b_words, 5))
    tok3 = jaccard(shingles(a_words, 3), shingles(b_words, 3))
    char = jaccard(char_shingles(a_text), char_shingles(b_text))

    a_lines = {l.strip() for l in a_text.splitlines() if l.strip()}
    b_lines = {l.strip() for l in b_text.splitlines() if l.strip()}
    line = jaccard(a_lines, b_lines)

    terms = jaccard(important_terms(a_words), important_terms(b_words))

    return (
        0.30 * tok5
        + 0.22 * tok3
        + 0.18 * char
        + 0.15 * line
        + 0.15 * terms
    )


def task_similarity(a_texts: dict[str, str], b_texts: dict[str, str]) -> tuple[float, dict[str, float]]:
    """Weighted average similarity across all file slots."""
    total_weight = 0.0
    total_score = 0.0
    per_file: dict[str, float] = {}

    for key, weight in FILE_WEIGHTS.items():
        a_text = a_texts.get(key, "")
        b_text = b_texts.get(key, "")
        if not a_text.strip() and not b_text.strip():
            continue
        s = file_similarity(a_text, b_text)
        per_file[key] = s
        total_weight += weight
        total_score += weight * s

    if total_weight == 0:
        return 0.0, per_file
    return total_score / total_weight, per_file


# -------------------------------------------------------------------------
# Main comparison
# -------------------------------------------------------------------------
all_tasks = [p for p in sorted(scan_dir.iterdir()) if is_silver_task(p)]
if target not in all_tasks:
    all_tasks.append(target)

target_texts = load_task_texts(target)

results: list[tuple[float, Path, dict[str, float]]] = []
for other in all_tasks:
    if other.resolve() == target.resolve():
        continue
    other_texts = load_task_texts(other)
    score, per_file = task_similarity(target_texts, other_texts)
    results.append((score * 100.0, other, per_file))

results.sort(key=lambda t: t[0], reverse=True)

print(f"Silver similarity report for: {target.name}")
print(f"Scan directory: {scan_dir}")
print(f"Hard-block threshold: {threshold:.0f}%")
print(f"Tasks compared: {len(results)}")
print()

if not results:
    print("No other Silver tasks found to compare against.")
    print("\nResult: PASS (no comparisons made)")
    sys.exit(0)

print("Top matches:")
for pct, other, per_file in results[:10]:
    flag = " *** SIMILAR ***" if pct >= threshold else (" (review)" if pct >= threshold * 0.65 else "")
    print(f"  {pct:5.1f}%  {other.name}{flag}")
    if pct >= threshold * 0.50:
        detail = "  ".join(
            f"{k.split('/')[-1].replace('.md','').replace('.json','').replace('.sh','')}={v*100:.0f}%"
            for k, v in sorted(per_file.items(), key=lambda x: -x[1])
        )
        print(f"          breakdown: {detail}")

top_pct, top_dir, top_parts = results[0]

print()
blocking_reasons: list[str] = []

# Hard block: overall score above threshold
if top_pct >= threshold:
    blocking_reasons.append(f"overall score {top_pct:.1f}% >= threshold {threshold:.0f}%")

# Hard block: instruction alone is highly similar (even if overall score is diluted)
instr_sim = top_parts.get("instruction.md", 0.0) * 100
if instr_sim >= 40.0:
    blocking_reasons.append(
        f"instruction.md similarity {instr_sim:.1f}% is too high — "
        f"instructions describe similar problems"
    )

# Hard block: test surface very similar (same bug class)
test_sim = top_parts.get("tests/config.json", 0.0) * 100
if test_sim >= 45.0:
    blocking_reasons.append(
        f"test surface similarity {test_sim:.1f}% — "
        f"test names and test_patch suggest same bug class"
    )

# Hard block: solution patch nearly identical
solve_sim = top_parts.get("solution/solve.sh", 0.0) * 100
if solve_sim >= 50.0:
    blocking_reasons.append(
        f"solve.sh similarity {solve_sim:.1f}% — "
        f"solution patches are nearly identical (same root cause)"
    )

if blocking_reasons:
    print("Result: HARD BLOCK")
    print(f"Closest task: {top_dir.name} ({top_pct:.1f}%)")
    for reason in blocking_reasons:
        print(f"  Reason: {reason}")
    print()
    print("Fix: pivot to a different bug class, module, or behavioral contract.")
    print("Paraphrasing the same instruction rarely moves similarity scores enough.")
    sys.exit(1)

if top_pct >= threshold * 0.65:
    print(f"Result: REVIEW RECOMMENDED ({top_pct:.1f}% — below threshold but worth checking)")
    print(f"Closest task: {top_dir.name}")
    print("Consider whether the root cause, bug class, and test surface are truly distinct.")
    sys.exit(0)

print(f"Result: PASS (highest similarity: {top_pct:.1f}%)")
sys.exit(0)
PY
