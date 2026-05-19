---
name: sprint-close
description: Phase 5 sprint close. Archive plan/spec/audit, update living docs (architecture, features, decisions), update CURRENT.md, commit. Run at end of every sprint.
trigger: manual
---

# Phase 5 — Sprint Close

Run this at the end of every sprint/feature cycle.
Prerequisite: Phase 4 audit passed (zero blockers, zero deferred items).

## Step 1: Update living docs (single source of truth)

These files represent the **current state of the project** — always up to date, human-readable.

### docs/architecture/README.md
If anything architectural changed this sprint (new service, changed data flow, new dependency, removed component):
- Update or create `docs/architecture/README.md` with the current system design
- Keep it current — this is not a history doc, it reflects right now
- Sections: Overview, Components, Data flow, External dependencies, Key decisions

### docs/features/
One file per feature: `docs/features/<feature-name>.md`
- Create or update the file for this sprint's feature
- Format:
```markdown
# <Feature Name>

**Status:** Live / In progress / Deprecated
**Sprint:** YYYY-MM-DD
**Jira:** <key>

## What it does
<One paragraph — what this feature does for the user>

## How it works
<Technical summary — key files, flow, any gotchas>

## Key files
- `src/...` — what it does
- `tests/...` — test coverage

## Known limitations / future work
<anything deferred or incomplete>
```

### docs/decisions/
One file per significant decision: `docs/decisions/YYYY-MM-DD-<topic>.md`
- Write one for every non-obvious technical decision made this sprint
- Format:
```markdown
# <Decision title>

**Date:** YYYY-MM-DD
**Status:** Accepted

## Context
<Why was this decision needed?>

## Decision
<What was decided?>

## Alternatives considered
<What else was considered and why rejected?>

## Consequences
<What does this mean for future work?>
```

---

## Step 2: File skill-gap issues from this session

1. Read `docs/brain/failures-this-session.md`
2. If the file does not exist or is empty — skip to Step 3
3. For each distinct failure entry, open one GitHub issue on `sap-kb-skills`:
   - Use Rule 17 metadata collection and scrubbing steps (Steps 2–4) for each entry
   - Skip Rule 17 Step 3.5 (the interactive preview) — present all rewrites as a batch summary to the developer instead, then file
   - Title: `[skill-gap] <skill-name>: <one-line summary>` or `[standards-gap] <rule>: <summary>`
   - Label: `skill-gap` (wrong skill content), `standards-gap` (workflow rule violation), or `tooling-gap` (plugin/update-skills issue)
   - Include all auto-collected metadata
4. After all issues are filed, clear the file:
   `echo "" > docs/brain/failures-this-session.md`
5. Report to developer: "Filed N skill-gap issue(s) on sap-kb-skills: [list with issue numbers]"

---

## Step 3: Archive this sprint's artifacts (immutable)

```bash
FEATURE="your-feature-name"
DATE=$(date +%Y-%m-%d)
mkdir -p docs/archive/${DATE}-${FEATURE}
```

Copy (do **not** move) into the archive directory — source files remain gitignored, only the archive copy is committed:
- The implementation plan (`docs/brain/plans/YYYY-MM-DD-*.md`)
- The design spec (`docs/brain/specs/YYYY-MM-DD-*.md`) if one exists
- The audit report (from Phase 4)

---

## Step 3b: Update knowledge graph (if graphify is installed)

If `graphify-out/` exists in this project, run:
```bash
python -m graphify ./docs --update
```
This re-extracts only changed files (~10s) and keeps `graphify-out/GRAPH_REPORT.md` current for the next session. Run after archiving so the graph reflects the final committed docs.

---

## Step 4: Update CURRENT.md

- Change Status to DONE
- Move all open items to Completed
- Clear Blockers to "(none)"
- Clear Deferred to "(none)"
- Tick all Phase 5 gates
- Update "Last updated" timestamp
- Add next sprint items to Open Items if known

---

## Step 5: Update the brain (if anything changed)

| If you discovered | Update |
|------------------|--------|
| New never-violate rule | `docs/brain/02-hard-rules.md` |
| Stack or architecture changed | `docs/brain/01-project-identity.md` |
| New Jira/Wiki/GitHub pattern | Relevant skill file |
| New failure mode | Same skill file |
| New SAP Product Standard applies | `docs/brain/skills/review/SKILL.md` |

---

## Step 6: Commit

```bash
git add docs/brain/ docs/archive/ docs/architecture/ docs/features/ docs/decisions/
git commit -m "docs: sprint close - <feature> [skip ci]"
```

Use `[skip ci]` — this is a docs-only commit.

---

## Checklist

- [ ] `docs/architecture/README.md` updated if architecture changed
- [ ] `docs/brain/failures-this-session.md` processed — skill-gap issues filed and file cleared
- [ ] `docs/features/<feature>.md` created or updated
- [ ] `docs/decisions/YYYY-MM-DD-<topic>.md` written for key decisions
- [ ] Archive directory created with plan, spec, audit
- [ ] `graphify-out/` updated if graphify is installed (`python -m graphify ./docs --update`)
- [ ] CURRENT.md status set to DONE, all items resolved
- [ ] Brain files updated for new learnings
- [ ] Committed with `[skip ci]`
