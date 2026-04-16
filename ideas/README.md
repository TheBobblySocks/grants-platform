# Ideas

A scratch space. Drop any thought about the grants platform in here as a short
`.md` or `.txt` file **before** we start writing application code.

The point is to get everyone's thinking visible in one place, then synthesise.

## How to add an idea

1. Create a new file in this directory — one file per idea.
2. **Prefix the filename with a timestamp** so lexical sort == chronological
   order. Format: `YYYY-MM-DD-HHMM-short-title.md`. Examples:
   `2026-04-16-0949-use-the-ideas-directory.md`,
   `2026-04-17-1015-forms-schema-shape.md`,
   `2026-04-17-1402-auth-magic-link.md`. Use the time you're creating the file
   (local wall-clock is fine — we only need enough precision to break ties on
   the same day).
3. Keep the rest of the name greppable: `forms-schema-shape`, `auth-magic-link`,
   `assessor-scoring-ui`, `eligibility-checker`, etc.
4. Put your name or initials at the top so we know who to ask about it.
5. Keep it short. Bullet points are fine. Half-formed is fine. Questions are fine.
6. Commit and push — don't wait for review.

The timestamp prefix means that when two ideas cover overlapping ground, it's
obvious which one came later and may supersede the earlier one. Don't rename or
delete older files to "fix" a supersession — mark the older one
`Status: dropped` (see below) so the argument stays readable.

## Optional template

```markdown
# <short title>

**Author:** <your name>
**Date:** YYYY-MM-DD
**Status:** rough | considered | agreed | dropped

## The idea
One or two sentences.

## Why it might be good
...

## Why it might be bad / open questions
...

## What it would touch
e.g. form schema, auth, assessor UI, data model
```

## When do we stop?

Once we've all dumped our thoughts in, we'll do a short read-through together,
pick a shape for v0, and start building. Ideas don't get deleted — superseded
ones just get `Status: dropped` and we move on.
