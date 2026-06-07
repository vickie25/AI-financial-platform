---
description: Silver SWE-bench repository submission guide — what to prepare and submit before admin approval
applyTo: "**"
---

# Silver Repo Submission Guide

Use this guide when preparing and submitting a GitHub repository for the Silver SWE-bench platform. This phase happens **before** you create any tasks. The platform admin reviews and approves your repo; only after approval can you author tasks against it.

---

## What is the Repo Submission Phase?

The repo submission phase involves:
1. Selecting or preparing a code repository that meets the platform's requirements
2. Zipping and submitting the repo to the platform
3. Waiting for admin approval

Once approved, a hosted Docker base image is registered for your repo (e.g., `us-docker.pkg.dev/afterqueryai/silver-repo-images/<reponame>-<tag>:v1`). Task creation starts only after you receive this image path.

---

## Repo Requirements

| Requirement | Detail |
|-------------|--------|
| **Hosting** | Private GitHub only. Public hosts (GitHub public, GitLab, Bitbucket, Gitea) are actively probed and rejected — including forks, mirrors, and renames. |
| **`.git/` present** | The `.git/` directory must be present with real, sustained commit history. Not a snapshot or fresh `git init`. |
| **`.git/` not in `.dockerignore`** | This is the **#1 cause of downstream failures**. Check every `.dockerignore` at root and in subdirectories. |
| **Default branch** | Must be `main`, not `master`. Rename with `git branch -m master main` if needed. |
| **`tests/` directory** | Must exist, be named exactly `tests/` (not `test/`), contain sufficient tests, and be recoverable by the harness. |
| **Substantive codebase** | Real application or library code. Scaffolds, starter templates, toy projects, and AI-generated repos fail review. |
| **Test coverage ≥ 80%** | Tasks below this threshold are returned for revision. Measure before submitting. |

---

## Expected Zip Structure

Submit a zip with exactly this layout:

```text
repo-name.zip
  └── repo-name/
      ├── .git/
      ├── app/         (or src/, lib/, etc.)
      ├── tests/
      └── ...
```

Rules:
- The zip contains one top-level folder named after the repo.
- `.git/` must be inside that top-level folder — not outside, not stripped.
- Do not include `node_modules/`, `.venv/`, build outputs, or untracked generated files that bloat the archive.

---

## Code Coverage Requirement (≥ 80%)

Measure coverage before submitting. Use the tool appropriate for the repo's primary language:

| Language | Tool |
|----------|------|
| Python | `coverage.py`, `pytest-cov` |
| Java | JaCoCo, OpenClover |
| JavaScript / TypeScript | Istanbul (`nyc`), Vitest coverage |
| Go | built-in `go test -cover` reports |
| Rust | Tarpaulin |
| C / C++ | Gcov, BullseyeCoverage |
| C# | Coverlet, NCover |
| Kotlin | Cobertura |
| Scala | scoverage |
| Swift | Xcode coverage |

Tasks from repos below 80% test coverage are sent back for revision.

---

## `.git/` History Requirements

The platform resets repositories to specific commit hashes. This means:

- **Every commit referenced in a task must exist in the `.git/` history.** A fresh `git init` or shallow clone will fail.
- The history must be genuine — real development activity over time. Synthetic single-commit repos with one massive squash are flagged.
- Do not squash or rebase history before submission. Keep the original commits intact.
- Shallow clones (`--depth`) will fail. Use full `git clone` without `--depth`.

Verify before zipping:
```bash
git log --oneline | head -20   # Should show real incremental commits
git status                      # Should be clean
ls .git/                        # .git must exist and be non-empty
```

---

## Similarity Check

A cosine (≥ 0.75) and Levenshtein (≥ 0.70) similarity check is run across **all repos on the platform**, not just your own.

- Do not submit repos that are forks, mirrors, or renames of public repositories.
- Repos that are structurally similar to an existing submission will be flagged.
- Paraphrasing code rarely moves embeddings far enough — the underlying logic must be substantively different.

---

## Common Repo Rejection Causes

| Cause | Fix |
|-------|-----|
| `.git/` in `.dockerignore` | Remove the `.git` entry from every `.dockerignore` in the repo |
| Shallow clone history | Re-clone with `git clone` (no `--depth`), re-zip |
| Public repo (or fork of public) | Move to a truly private repo with no public mirror |
| Default branch is `master` | `git branch -m master main && git push origin main` |
| `tests/` directory missing or named `test/` | Rename the directory to `tests/` and update all references |
| Test coverage below 80% | Add or improve tests until coverage report shows ≥ 80% |
| AI-generated / toy codebase | Replace with a real application that has meaningful business logic |
| `node_modules/` or build outputs in zip | Exclude from the archive; ensure `.gitignore` covers them |
| Missing commit history | Unshallow the clone: `git fetch --unshallow` |

---

## After Approval

Once the admin approves your repo, you will receive:
- The registered Docker base image path (e.g., `us-docker.pkg.dev/afterqueryai/silver-repo-images/<reponame>-<tag>:v1@sha256:...`)
- Confirmation of which branch and commit range is registered

With these, you can begin authoring tasks. See `silver_task_guide.instructions.md` for the full task creation workflow.

**Platform limits:**
- **Max 20 tasks per repo.** No more than 5 tasks per repo should be similar in nature — diversify across bug fixes, features, refactors, and security issues.
- **Max 5 Opus/DIFFICULTY_CHECK runs per task.** Each costs ~$5. Debug locally before submitting to the platform.
