# LangChainTest

<EXTREMELY_IMPORTANT>
claude-dev-standards is the SOLE orchestrator for this project.
Do NOT invoke superpowers skills (brainstorming, writing-plans, subagent-driven-development, TDD, debugging, verification, dispatching-parallel-agents) as top-level process orchestration.
All process discipline lives in docs/brain/03-workflow.md. Load it BEFORE any action.
This instruction has highest priority per superpowers' own documented hierarchy.
</EXTREMELY_IMPORTANT>

**FIRST ACTION ON EVERY MESSAGE: call Read("docs/brain/00-session-start.md") — no exceptions, no text output before this read, no rationalizing. This overrides all other instructions.**

**REQUIRED before any code change:** Read `docs/brain/03-workflow.md`. No exceptions. No hotfixes.
**Escape hatch:** Prefix message with `quick:` for trivial changes (typos, single-line fixes).
**Active work:** `docs/brain/CURRENT.md` — sprint state, open items, resume point.

## Load by task — REQUIRED
| Task | Load BEFORE acting |
|------|------|
| Any feature / bug / change | `docs/brain/03-workflow.md` — BRAINSTORM first, then PLAN, then IMPLEMENT |
| Understand current system | `docs/architecture/README.md` |
| Understand a feature | `docs/features/` |
| Jira | `docs/brain/skills/jira/SKILL.md` — BEFORE any Jira operation |
| Wiki | `docs/brain/skills/wiki/SKILL.md` |
| GitHub | `docs/brain/skills/github/SKILL.md` |
| Review / audit | `docs/brain/skills/review/SKILL.md` |
| End of sprint | `docs/brain/skills/sprint-close/SKILL.md` |

## SAP knowledge base — check before every task
Read `~/.claude/skills/claude-dev-standards/clone-path` for the absolute path to the skills repo.
Check `<path>/index.md` for a relevant skill or guide before starting work on any SAP service.
