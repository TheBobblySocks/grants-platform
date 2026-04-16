# Changelog

All notable changes to the GrantOS grants platform.

## 2026-04-16

### Added — Claude Code automation suite

- **Orchestrator skill** (`/orchestrate`) — scans PLAN.md for pending work,
  dispatches parallel sub-agents in isolated worktrees (one per stream),
  reviews results, and creates PRs. Designed for repeated triggering to
  advance the build incrementally.
- **Ship skill** (`/ship`) — pre-flight checks (tests, lint, boot), branch
  creation, and structured PR opening. Enforces the PR-only workflow.
- **Verify skill** (`/verify`) — quick health check reporting tests, lint,
  boot status, and git state in a summary table.
- **Stream context skills** (`/stream-a` through `/stream-d`) — per-stream
  reference encoding file ownership, public APIs, imports, implementation
  status, and pending work. Used by the orchestrator to brief sub-agents.
- **Project settings** (`.claude/settings.json`) — pre-allowed permissions
  for pytest, ruff, flask, git, and gh commands so agents run without manual
  approval prompts.
- **CLAUDE.md** updated with automation skill documentation and orchestrator
  workflow description.

### Context

- 138 tests passing, 8 pre-existing failures in `test_assessor_ai.py`
- Core platform (Phase 0-1) fully implemented
- Phase 2 partially complete (uploads and eligibility evaluation still stubbed)
