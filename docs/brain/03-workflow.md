# Development Workflow — Non-Negotiable

**NO HOTFIXES. NO QUICK FIXES. NO SKIPPING PHASES.**
Every change, no matter how small, follows this sequence.
The loop repeats until CURRENT.md has zero open items.

<EXTREMELY_IMPORTANT>
This workflow is SELF-ENFORCING. Do NOT invoke external skills for orchestration:
- Do NOT call superpowers:brainstorming — Phase 1 IS the brainstorming process
- Do NOT call superpowers:writing-plans — Phase 2 IS the planning process
- Do NOT call superpowers:subagent-driven-development — Phase 3 IS the team execution
- Do NOT call superpowers:verification-before-completion — verification is embedded in Phase 3/4
- Do NOT call superpowers:dispatching-parallel-agents — team dispatch is embedded in every phase

The discipline, rigor, and enforcement from those skills is ABSORBED here.
If you find yourself thinking "I should invoke a superpowers skill" — STOP. Read this file instead.
</EXTREMELY_IMPORTANT>

---

## RED FLAGS — If you think any of these, STOP

| Thought | Reality |
|---------|---------|
| "This is simple, skip the workflow" | Use `quick:` escape hatch if truly trivial. Otherwise, workflow applies. |
| "Let me just write the code first" | BRAINSTORM comes first. Always. No exceptions. |
| "I'll invoke superpowers:brainstorming" | NO. This workflow IS the brainstorming process. |
| "I don't need the team for this" | The workflow decides when to use the team, not you. |
| "Let me ask the user what to do" | The team decides internally. User gate only at phase boundaries. |
| "I can skip the audit, the code is simple" | Phase 4 applies to ALL changes. Simple code has bugs too. |
| "I'll just do one more thing before the review" | Stop. Run the audit NOW. Don't accumulate unreviewed work. |
| "The user already approved, I can skip review" | User approval ≠ team review. Both are required. |

---

## The Loop

```
CURRENT.md has open items?
         ↓
  1. BRAINSTORM → 2. PLAN → 3. IMPLEMENT → 4. AUDIT → 5. DOCUMENT
         ↑___________________any audit blockers?__NO resolved?___↩
                              YES ↓
                    CURRENT.md fully green → sprint closed
```

**Gate rule:** The loop does not exit until Phase 4 produces zero blockers.

---

## Escape Hatch — Quick Mode

**Trigger:** User prefixes message with `quick:`

**Behavior:** Skip directly to Phase 3 (implement). No team, no brainstorm, no gates. For:
- Typo fixes
- Single-line changes
- Config tweaks with no architectural implications
- README edits

**NOT for quick mode:** Anything involving new logic, new files, new dependencies, or behavioral changes.

When in doubt, use the full workflow. Quick mode is an escape hatch, not a default.

---

## Phase 1 — BRAINSTORM

**Who leads:** Chief Architect
**Purpose:** Understand the problem, explore approaches, converge on a design.

### Process:

1. **Explore context:** Read relevant code, recent commits, architecture docs.
   If the task involves SAP technologies, consult the SAP knowledge base
   (path in `~/.claude/skills/claude-dev-standards/clone-path` → check `index.md` for relevant skills).

2. **Spawn team in parallel** — ALL agents produce findings independently:

   | Agent | Focus |
   |-------|-------|
   | Chief Architect | Technical approach, architecture fit, cross-cutting concerns |
   | Product Manager | Acceptance criteria, scope, user stories |
   | Security Expert | Attack surface, auth requirements, data sensitivity |
   | QA Expert | Test strategy, coverage gaps, edge cases |
   | DBA Expert | Schema implications, migration needs, query patterns (if applicable) |
   | UX Expert | User flow, accessibility, component design (if applicable) |

3. **Chief Architect consolidates** findings into a spec document.

4. **Self-closing review loop:**
   ```
   REPEAT:
     All agents review the consolidated spec
     Chief Architect collects findings
     IF any agent reports blockers:
       Address the blockers
       CONTINUE (re-review with ALL agents)
     ELSE:
       All agents report "No blockers"
       BREAK
   ```
   **CRITICAL:** Never ask the user to review mid-iteration. Never ask "should I do another pass?" The loop is self-closing — it ends when the team converges.

5. **Challenger step** — adversarial review of the converged spec:

   After the team converges, ask these questions of the spec:
   - **What did we miss?** Edge cases, failure modes, race conditions, scale limits
   - **What could go wrong?** Security holes, data loss scenarios, dependency risks
   - **Is there a simpler alternative?** Over-engineering check — can we achieve the same with less?
   - **What assumptions are we making?** Unstated prerequisites, availability of services, user behavior
   - **What happens when it fails?** Degraded state, recovery path, user experience during failure

   If the Challenger surfaces a genuine gap: loop back to step 3 (consolidate with the new finding).
   If no gaps: proceed. The Challenger is not a blocker factory — it catches real blind spots, not hypotheticals.

6. **User gate** (if `gates.after_brainstorm: true` in config, default: true):
   ```
   Spec complete. Summary:
   • [bullet points of what will be built]
   
   Approve direction? [Y/n/edit]
   ```
   Present converged result ONCE. Single prompt. Wait for response.

7. **Save spec** to `docs/brain/specs/YYYY-MM-DD-<feature>-design.md` (local working file, not committed)

8. **Update state:** Write/update `docs/brain/state.lock`:
   ```json
   {"phase": "brainstorm", "started": "<ISO timestamp>", "feature": "<name>"}
   ```

### Debugging Mode (replaces brainstorm for bugs):

**Trigger:** Task is clearly a bug (user says "fix", "broken", "error", "bug", "failing")

**Process:**
1. Reproduce the issue (run the failing test/command)
2. Form hypothesis — what COULD cause this?
3. Narrow search space — add logging, check assumptions, binary search
4. Identify root cause — confirm with evidence, not guessing
5. Then proceed to Phase 2 (Plan the fix)

Do NOT jump to a fix. Understand the root cause first.

---

## Phase 2 — PLAN

**Who leads:** Product Manager
**Purpose:** Break the spec into actionable tasks with clear acceptance criteria.

### Process:

1. **Product Manager creates task checklist** from the approved spec.

2. **Each agent contributes domain-specific sections in parallel:**

   | Agent | Contribution per task |
   |-------|----------------------|
   | Security Expert | Auth checks, input validation, threat model |
   | QA Expert | Test plan (unit + integration + edge cases) |
   | DBA Expert | Migrations, schema changes, adapter updates |
   | UX Expert | Components, CSS requirements, accessibility |

3. **Chief Architect reviews plan completeness.**

4. **Self-closing review loop** (same pattern as Phase 1):
   - All agents verify plan covers their domain
   - Iterate until zero blockers

5. **No user gate by default** (plan follows approved spec direction).
   If `gates.after_plan: true`, present plan summary to user.

6. **Save plan** to `docs/brain/plans/YYYY-MM-DD-<feature>.md` (local working file, not committed)

7. **Update CURRENT.md** with task checklist. Every task MUST include:
   - [ ] Implementation description
   - [ ] Test coverage (unit + integration)
   - [ ] Security section (auth checks; "N/A" with reason if none)
   - [ ] DB changes section (if applicable)

8. **Update state.lock:** `{"phase": "plan", ...}`

---

## Phase 3 — IMPLEMENT

**Who leads:** Chief Architect (coordination)
**Purpose:** Build what was planned, with quality gates at every step.

### Process:

1. **Chief Architect creates TaskList** from CURRENT.md tasks.

2. **Parallel agent tracks:**

   | Agent | Track |
   |-------|-------|
   | Developer | Implements per task checklist |
   | QA Expert | Writes tests ALONGSIDE code (test first when possible) |
   | DBA Expert | Writes migrations as DB tasks come up |
   | Security Expert | On-call — re-engaged if implementation deviates from plan |

3. **Before ANY task is marked complete, verify:**
   - Tests pass (run the actual test command, check output)
   - Code does what the task specifies (not just "looks right")
   - No regressions introduced (run full test suite if feasible)
   - If the task has a security section, security checks are implemented

4. **Phase visibility:** Print one line at meaningful moments:
   ```
   [brain] Task 2/5 complete: health endpoint implemented, tests passing.
   ```
   Not a gate — just visibility so the user knows it's progressing.

5. **Update state.lock** as tasks complete:
   ```json
   {"phase": "implement", "started": "...", "task_count": 5, "tasks_complete": 3, "feature": "..."}
   ```

### TDD Discipline (embedded from superpowers:TDD):
- Write the test first when the behavior is clearly specified
- Run the test, see it fail (red)
- Implement the minimum code to pass (green)
- Refactor if needed
- This is the QA Expert's responsibility, working alongside Developer

### Verification (embedded from superpowers:verification-before-completion):
- Before claiming ANY task is done: run the tests, check the output, confirm it works
- Never say "tests should pass" — run them and verify
- Never say "this should work" — test it and confirm
- Evidence before assertions. Always.

---

## Phase 4 — AUDIT

**Who leads:** Chief Architect (consolidation)
**Purpose:** Independent review of everything built. Find what was missed.

**REQUIRED:** Load `docs/brain/skills/review/SKILL.md` before starting Phase 4.
Each agent checks their relevant SAP Product Standards section from that file.
This applies to ALL code changes — even small ones can violate product standards.

### Process:

1. **All agents review in parallel** — each checks their domain against the plan AND the SAP Product Standards checklist in the review skill:

   | Agent | Reviews |
   |-------|---------|
   | Security Expert | Auth, input validation, OWASP top 10, SAP SEC-*/SDOL-*/DPP-* |
   | QA Expert | Test coverage, edge cases, test quality |
   | DBA Expert | Migration safety, query performance, schema correctness |
   | UX Expert | Layout, accessibility, responsive behavior (if applicable) |
   | Chief Architect | Architecture fit, code quality, cross-cutting concerns |

2. **Self-closing review loop:**
   - All agents report findings
   - If ANY blocker: fix it → re-run audit with ALL agents
   - Repeat until zero blockers
   - Never ask user mid-iteration

3. **Produce review artifact** at `docs/brain/reviews/phase4-YYYY-MM-DD.md`:
   ```markdown
   # Phase 4 Review — YYYY-MM-DD
   
   ## Reviewed commit: <SHA>
   
   ## Agent reviews:
   ### <Agent Name>
   - Reviewed: <what they checked>
   - Finding: <pass / specific issue>
   
   ## Verdict: PASS
   ```

4. **If blockers remain after fixes:** Add to CURRENT.md → loop back to Phase 3.

5. **User gate** (if `gates.after_audit: true`, default: true):
   ```
   Audit complete. [N] files changed, tests passing, review passed.
   [Summary of what was built + audit findings resolved]
   
   Ready to proceed? [Y/n/review]
   - Y: move to Phase 5 (document)
   - n: provide feedback → loop back to Phase 3
   - review: show full Phase 4 review artifact
   ```

6. **Update state.lock:** `{"phase": "audit", ...}`

---

## Phase 5 — DOCUMENT

**Who leads:** Chief Architect + Product Manager
**Purpose:** Close the loop. Archive, document, prepare for next work.

### Process:

1. **Update living docs** (if anything architectural changed):
   - `docs/architecture/README.md`
   - `docs/features/<feature>.md`
   - `docs/decisions/YYYY-MM-DD-<topic>.md` (ADR for key decisions)

2. **Archive:** Move spec + plan + audit report to `docs/archive/YYYY-MM-DD-<feature>/`

3. **Update CURRENT.md:** Mark complete, add next items if known.

4. **Update brain files** if new rules/patterns discovered during this sprint.

5. **Commit:** `docs: sprint close - <feature>`

6. **Delete state.lock** (phase complete).

---

## Self-Closing Audit Loop — The Rule

This pattern applies in Phases 1, 2, and 4. It is NON-NEGOTIABLE:

```
REPEAT:
  Spawn all relevant agents in parallel
  Each agent produces their review/findings
  Chief Architect consolidates
  IF zero blockers from ALL agents:
    BREAK — present converged result to user (if gate active)
  ELSE:
    Address blockers
    CONTINUE — re-review with ALL agents (not just the one that found the issue)
```

**Never:**
- Ask the user "should I do another review pass?" → Just do it.
- Ask the user "the team found issues, should I fix them?" → Just fix them.
- Present partial results → Only present converged, finalized results.
- Skip re-review after fixes → The fix might introduce new issues.

**The user sees ONE prompt per gate.** Everything else is internal team work.

---

## Configuration

Read `docs/brain/config.json` for gate settings. If file is missing, use defaults:

```json
{
  "mode": "guided",
  "gates": {
    "after_brainstorm": true,
    "after_plan": false,
    "after_implement": false,
    "after_audit": true
  }
}
```

| Mode | Gates active |
|------|-------------|
| `guided` (default) | after_brainstorm + after_audit |
| `autonomous` | none — team runs full cycle, presents final result only |
| `gated` | all four — maximum user control |

---

## Session Resilience

On session start, check `docs/brain/state.lock`:
- If exists and phase is active → resume from that phase
- If exists and started > 2h ago → warn user: "Stale state detected. Resume or reset?"
- If absent → fresh start (Phase 1 or whatever the task requires)
