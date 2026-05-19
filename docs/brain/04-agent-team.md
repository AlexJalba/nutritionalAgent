# Agent Team

Parallel agent execution is enabled by `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
(set globally by `claude-dev-standards install`).

## Full Roster (authoritative source)

This file is the authoritative roster reference. `03-workflow.md` shows a simplified
core subset per phase for readability — this file defines the complete participation map.

| Agent | Active Phases | Responsibilities |
|-------|--------------|-----------------|
| **Chief Architect** | 1, 3, 4, 5 | Technical direction, cross-cutting decisions, coordinates all Phase 3 tracks, final architecture review, loop gating |
| **Product Manager** | 1, 2, 5 | Acceptance criteria with explicit security/i18n/accessibility/compliance per task; CURRENT.md authorship |
| **Developer** | 3 | Feature implementation per CURRENT.md checklist; cannot mark done until all gates pass |
| **QA Expert** | 1, 2, 3, 4 | Pre-implementation coverage audit; writes tests alongside code (never after); full suite sign-off |
| **Security Expert** | 1, 2, 4, 3* | Attack surface at brainstorm; validates implementation at audit; on-call during Phase 3 |
| **DBA Expert** | 1, 2, 3, 4 | Schema review, migration scripts, adapter updates, query review as DB interactions are built |
| **UX Expert** | 1, 2, 3, 4 | Layout, accessibility, RTL/LTR, logical CSS, dark mode; signs off every UI file |
| **i18n/L10n Expert** | 3, 4 | Externalizes strings as features are built; flags hardcoded text immediately, blocking the task |
| **Legal Expert** | 1, 2, 4, 3* | Compliance per task at planning time; GDPR, data retention, privacy; on-call during Phase 3 |

*On-call in Phase 3 — re-engaged by Chief Architect if implementation deviates from plan.

## Parallel Execution Map

```
Phase 1 (Brainstorm):  ALL agents in parallel
                       Chief Architect consolidates → self-closing review loop
                       Output: technical approach doc (spec)

Phase 2 (Plan):        PM leads
                       Security + Legal + DBA + QA + UX contribute in parallel
                       Self-closing review loop until all domains covered
                       Output: CURRENT.md with full task checklist

Phase 3 (Implement):   Chief Architect coordinates
                       Developer + QA + i18n + UX + DBA in parallel tracks
                       Security + Legal on-call
                       Verification before marking ANY task complete
                       Output: implemented + tested feature

Phase 4 (Audit):       ALL agents in parallel — full domain review
                       Self-closing review loop until zero blockers
                       Produce review artifact with commit SHA
                       Output: docs/brain/reviews/phase4-<date>.md

Phase 5 (Document):    Chief Architect + PM
                       Output: archived sprint, updated brain, living docs
```

## Self-Closing Review Loop (applies to Phases 1, 2, 4)

This is the CRITICAL pattern that differentiates this workflow:

```
REPEAT:
  Spawn all relevant agents in parallel
  Each agent produces findings
  Chief Architect consolidates
  IF zero blockers from ALL agents → BREAK
  ELSE → Address blockers → CONTINUE (full re-review)
```

**Rules:**
- Never ask user to review mid-iteration
- Never ask "should I do another pass?" — just do it
- Present converged results to user ONCE per gate (if gate active)
- The user sees polished output, not work-in-progress

## Spawning the Team

Chief Architect creates tasks first, then dispatches agents via the Agent tool:

```
# Per-phase pattern:
1. TaskCreate for each agent's work item
2. Spawn agents in parallel (Agent tool with run_in_background)
3. Consolidate results when all complete
4. Run review loop if needed
5. Present to user only after convergence
```

Each agent reads CURRENT.md for context, then executes their domain brief.
Chief Architect monitors TaskList and unblocks cross-cutting decisions.

## Worktrees — Architect Decision (not default)

By default, all agents work on the same feature branch. This works when tasks touch
different files (the common case after good Phase 2 decomposition).

**When to use worktrees:** Chief Architect identifies during task dispatch that two
parallel tasks modify the same files. In that case:

1. Create worktrees for conflicting parallel tasks:
   ```
   git worktree add .worktrees/task-N -b feat/<feature>--task-N
   ```
2. Spawn agents with `EnterWorktree` targeting the worktree
3. When task completes, merge back to feature branch:
   ```
   git merge feat/<feature>--task-N
   ```
4. Resolve any conflicts at merge time (architect responsibility)
5. Remove worktree: `git worktree remove .worktrees/task-N`

**When NOT to use worktrees:**
- Tasks touch different files (majority case) — no benefit
- Tasks have dependencies (task 2 needs task 1's output) — must be sequential anyway
- QA writing tests for Developer's code — QA needs to see implementation first

The correct solution to file conflicts is better task decomposition in Phase 2.
Worktrees are a safety net for the rare case, not a default overhead.
