---
name: ship
description: Run pre-flight checks (tests, lint, boot), create a branch, commit changes, and open a PR to main. Never pushes to main directly.
---

# Ship — Create a PR for Current Changes

**Announce at start:** "Running pre-flight checks before shipping."

## Step 1: Pre-Flight Checks

Run these in parallel:

1. **Tests:** `uv run pytest` — all must pass
2. **Lint:** `uv run ruff check .` — no errors
3. **Boot:** `uv run flask --app wsgi run &` then wait 3 seconds, check the
   process is still running (no crash), then kill it

If any check fails:
- Fix the issue if it's small (lint auto-fix, missing import)
- Report to the user if it's larger (test failure, boot crash)
- Do NOT proceed to PR creation with failing checks

## Step 2: Prepare the Branch

1. Check `git status` for uncommitted changes
2. Check `git diff --stat` to see which files changed
3. Verify changed files are within the expected stream ownership (warn if not)
4. Create a branch: `git checkout -b <stream>/<short-description>`
   - Example: `stream-b/eligibility-precheck`
   - Example: `stream-d/upload-implementation`
5. Stage relevant files: `git add <specific-files>` (never `git add .`)
6. Commit with message format: `P{phase}.{item} stream-{letter}: {description}`

## Step 3: Create PR

1. Push: `git push -u origin <branch-name>`
2. Create PR with structured body:

```bash
gh pr create --base main --head <branch-name> \
  --title "P{phase}.{item} stream-{letter}: {description}" \
  --body "$(cat <<'EOF'
## Summary
- {what changed and why, 1-3 bullets}

## Stream
{stream letter}: {stream name}

## Phase / PLAN.md items
- P{X}.{Y}: {item description}

## Verification
- [x] `uv run pytest` passes
- [x] `uv run flask --app wsgi run` boots
- [x] `uv run ruff check .` clean
- [x] Only edited files within stream ownership

## Test plan
- [ ] {specific thing to verify manually}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

3. Report the PR URL to the user.

## Step 4: Post-Ship Tracking

1. Update `PLAN.md` — mark items as done or in-progress
2. Add entry to `CHANGELOG.md`
3. Update `.claude/notes/` with what was shipped

## Rules

- **Never push to main.** Always create a branch and PR.
- **Never skip checks.** Green tests, clean lint, clean boot — all three.
- **Never `git add .`** — stage specific files to avoid committing secrets or junk.
- **Never commit .env, credentials, or grants.db** — check what's staged.
- **Always include the phase/stream in the commit message and PR title.**
