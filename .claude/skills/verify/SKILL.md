---
name: verify
description: Quick health check — run tests, lint, boot the app, and report git state. Use before and after any work to confirm nothing is broken.
---

# Verify — Quick Health Check

**Announce at start:** "Running health checks."

Run all four checks in parallel, then report a summary table.

## Checks

1. **Tests:** `uv run pytest -q` — count passed/failed/errors
2. **Lint:** `uv run ruff check . --output-format concise` — count issues
3. **Boot:** Start `uv run flask --app wsgi run` in background, wait 3 seconds,
   check the process is alive (no import errors or crashes), then kill it.
   If it crashed, capture the error output.
4. **Git state:** `git status --short` — list uncommitted files and which
   stream they belong to (use the CONTRIBUTING.md ownership table).

## Report Format

```
| Check  | Status | Details                    |
|--------|--------|----------------------------|
| Tests  | ✅/❌  | X passed, Y failed         |
| Lint   | ✅/❌  | X issues found             |
| Boot   | ✅/❌  | Clean / {error message}    |
| Git    | ✅/❌  | Clean / N uncommitted files|
```

If all four are green: "All clear — safe to continue."

If any are red: list the specific failures and suggest fixes.

## When to Use

- **Before starting work** — baseline check
- **After finishing a task** — confirm nothing broke
- **Before shipping** — pre-flight (the `/ship` skill does this too)
- **After merging a PR** — verify main is clean
- **When something feels wrong** — quick diagnostic
