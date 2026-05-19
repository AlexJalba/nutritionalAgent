# Hard Rules — Never Violate

Universal defaults that apply to every SAP project. Add project-specific rules below.

## Workflow
1. **No hotfixes, no quick fixes** — every change follows the 5-phase loop in `03-workflow.md`
2. **No task marked done** until ALL CURRENT.md checklist items for that task are ticked
3. **No deferred items** — if something can't be done now, it becomes a new CURRENT.md entry with explicit reasoning

## Security
4. **Never commit credentials** — no passwords, tokens, keys, or secrets in any file
5. **Input validation at all boundaries** — user input, external API responses, file reads
6. **Principle of least privilege** — request only the permissions actually needed
7. **Authentication on every mutation** — no unauthenticated write endpoints in production

## Code quality
8. **Tests written during implementation** — never as a final step after code is done
9. **No `git add -A`** without reviewing untracked files first — use specific file staging
10. **No dead code** — remove unused functions, imports, variables immediately

## Documentation
11. **CLAUDE.md is an index** — maximum 15 lines, links only, no content
12. **CURRENT.md stays current** — update immediately when tasks complete or blockers appear
13. **Sprint close is mandatory** — no feature is done until `sprint-close/SKILL.md` is run

## SAP-specific
14. **SAP Product Standards** — every feature must pass the audit in `skills/review/SKILL.md`
15. **MCP limitations** — always load `skills/jira/SKILL.md` before any Jira operation; the MCP has known failures
16. **SAP knowledge base** — recipes, guides, and product standards live in the sap-kb-skills repo recorded at `~/.claude/skills/claude-dev-standards/clone-path`. Read relevant guides before starting work on any SAP service (BTP, CAP, IAS, AI Core, etc.)

## Copyright & IP
17. **Copyright header on every new source file** — SPDX format, applied at file creation. See `05-copyright-headers.md` for the exact header per language and license type. No exceptions.
18. **License type declared in project identity** — `01-project-identity.md` must specify `SAP-Internal`, `Apache-2.0`, `MIT`, or another SPDX identifier. Default: `SAP-Internal`.
19. **LICENSE file at repo root** — every repository must have a LICENSE file matching its declared license type. Missing LICENSE = Phase 4 audit blocker.

## 17. Report Issue — Unified Feedback Command
> **Trigger:** say `report issue` at any time in any session (before or after init). This is a post-init reinforcement reminder — pre-init entry points are the plugin README and SKILL.md Quick Commands.

When the developer says "report issue", "report problem", "report bug", or
"report standards issue", follow this procedure exactly:

### Step 1 — Collect the report
Ask the developer (one prompt only):
> "Describe what happened and what you expected.
> (Write however you like — I'll rewrite it into a clean bug report before filing.
> Your project name, file names, and repo URLs will not be included.)"

### Step 2 — Auto-classify
Determine issue type from the description:
- Mentions a specific SAP skill or tool (CAP, Jira, ArgoCD, AI Core, etc.)
  → label: `skill-gap`
- Mentions workflow behavior (phase skipped, rule not followed, agent non-compliance)
  → label: `standards-gap`
- Mentions plugin install, update-skills command, or report-issue itself
  → label: `tooling-gap`

When unclear, use `skill-gap` as default and note the ambiguity in the issue body.

### Step 3 — Collect metadata automatically
Gather the following without asking the developer. Use "unknown" for anything
not detectable:

```yaml
agent: <claude-code | copilot | cline | cursor | codex | unknown>
agent_version: <version string or unknown>
model: <model name or unknown>
os: <windows | macos | linux>
shell: <bash | zsh | powershell | unknown>
skill_active: <skill name if in context, else unknown>
workflow_phase: <brainstorm | plan | implement | audit | document | unknown>
workflow_present: <true if docs/brain/ and CURRENT.md exist, else false>
project_stack: <comma-separated list from package.json/pom.xml/go.mod/etc>
mcp_servers: <comma-separated list from ~/.claude.json or agent equivalent>
session_compacted: <true | false | unknown>
```

### Step 3.5 — Rewrite for quality and anonymization

Rewrite the developer's raw description into a structured, professional bug report:

- Rephrase in neutral, technical language — remove informal phrasing, frustration
  language, profanity, or casual speech
- Preserve the technical facts exactly — do not change what happened or what
  was expected
- Split into two clear sections: "What happened" and "What was expected"
- Make it actionable for a maintainer who has no session context
- Keep it concise — one to three sentences per section

Show the rewritten text to the developer before filing:
> "Filing as: [one-line summary of what happened]"
> "If this looks wrong, say 'cancel report issue' before I proceed."

If the developer responds with "cancel report issue", abort.
Otherwise proceed to Step 4 when they continue or send any other message.

### Step 4 — Open the GitHub issue

If `GH_HOST=github.tools.sap gh auth status` fails — inform the developer:
"Cannot file issue: not authenticated to github.tools.sap. Run `GH_HOST=github.tools.sap gh auth login` first, then re-run `report issue`."

**Before filing:** scrub the rewritten description and the skill context field.
Remove any of the following if present: file paths, directory paths, branch names,
repo URLs, project names, internal hostnames, IP addresses, credential strings,
or environment variable values. Replace each with `[REDACTED]`.

```bash
GH_HOST=github.tools.sap gh issue create \
  --repo bdc-kb/sap-kb-skills \
  --title "[<label>] <one-line summary>" \
  --label "<skill-gap|standards-gap|tooling-gap>" \
  --body "$(cat <<'EOF'
## What happened
<rewritten description — scrubbed of project-specific details>

## What was expected
<rewritten description — scrubbed of project-specific details>

## Metadata
| Field | Value |
|---|---|
| Agent | <agent> <agent_version> |
| Model | <model> |
| OS | <os> |
| Shell | <shell> |
| Skill active | <skill_active> |
| Workflow phase | <workflow_phase> |
| Workflow present | <workflow_present> |
| Project stack | <project_stack> |
| MCP servers | <mcp_servers> |
| Session compacted | <session_compacted> |

## Skill context
<if skill_active is known: paste the skill name and the exact guidance text
from the skill that was being followed when the failure occurred.
Do NOT include: project code, file paths, repo URLs, variable values, or
any content that could identify the project or developer.>

_Report generated by report-issue command. Project details anonymized._
EOF
)"
```

### Step 5 — Confirm to developer
```
Issue filed: [<label>] <summary> (#<number>)
View: https://github.tools.sap/bdc-kb/sap-kb-skills/issues/<number>
```

---

## Project-specific rules
> Add rules here that are specific to this project's stack, domain, or team agreements.
> Example format:
> 16. **Logical CSS only** — `ms-`/`me-` not `ml-`/`mr-` (Next.js + RTL project)
> 17. **withAuth() on every server action** — no bare exports in `actions/`

## 18. Workflow Is Self-Enforcing — No External Orchestrators

The 5-phase workflow in `docs/brain/03-workflow.md` is the SOLE process orchestrator.
Do NOT invoke superpowers skills (brainstorming, writing-plans, subagent-driven-development,
TDD, debugging, verification, dispatching-parallel-agents) as top-level process orchestration.
All process discipline is embedded directly in 03-workflow.md.
