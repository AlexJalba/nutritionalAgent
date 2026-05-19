---
name: review
description: Phase 4 full audit. All personas in parallel + SAP Product Standards. Loop back to Phase 1 if blockers found.
trigger: manual
---

# Phase 4 — Full Audit

Launch all review agents in parallel. Each checks their domain independently.
Chief Architect consolidates results and makes the go/no-go decision.

## Pre-audit quick check (optional but recommended)

Before spinning up the full team, run `feature-dev:code-reviewer` as a fast first pass:
- Feed it the diff or list of changed files
- It catches obvious code quality issues cheaply (bugs, security, patterns)
- Fix any blockers it raises **before** launching the full 9-persona team

---

## Domain checklists

### Security Expert
SAP Product Standards: SEC-*, SDOL-*, DPP-*

- [ ] Every mutation/action is authenticated — no unauthenticated write endpoints (SEC-376)
- [ ] User ID comes from verified token claims, never from caller input (SEC-248)
- [ ] Input validation at all system boundaries — injection attacks prevented (SEC-100)
- [ ] No credentials, secrets, or PII in code, logs, or HTTP responses (SEC-309, DPP-254)
- [ ] No IDOR vulnerabilities — actions scoped to authenticated user's data (SEC-376)
- [ ] New dependencies scanned for known CVEs (SDOL-025, SDOL-009)
- [ ] IAS/XSUAA used for auth — no custom auth schemes (SEC-230, INTG-02R1)
- [ ] mTLS or equivalent for system-to-system calls (SEC-374)
- [ ] Security-relevant events logged (SEC-215)
- [ ] CSRF protection in place for state-changing requests (SEC-223)
- [ ] HTTP security headers applied (SEC-390)

### Legal / Data Privacy Expert
SAP Product Standards: DPP-*, GDPR

- [ ] Personal data handling has documented legal basis (DPP-366)
- [ ] PII not present in logs or error messages (DPP-254, DPP-265)
- [ ] Data retained only as long as necessary — retention policy defined (DPP-256)
- [ ] Explicit consent captured before collecting personal data where required (DPP-224)
- [ ] AI usage compliant — no undocumented automated decision-making (DPP-350)
- [ ] Customer data not used for SAP product improvement without agreement (DPP-302)
- [ ] Personal data minimization applied — no unnecessary data collected (DPP-362)

### DBA Expert
SAP Product Standards: FC-*, PERF-*

- [ ] All schema changes have migration scripts
- [ ] Migration scripts tested — syntax valid, idempotent where possible
- [ ] ALL adapters/repositories updated (not just the primary one)
- [ ] No N+1 query patterns introduced (PERF-04)
- [ ] New columns/tables have appropriate indexes
- [ ] HANA-specific: no implicit conversions, correct data types used
- [ ] ILM considered for any new data objects with retention requirements (ILM-001)

### QA Expert
SAP Product Standards: FC-1, FC-2, FC-4

- [ ] Test suite: 0 failing tests (FC-4)
- [ ] Coverage: ≥80% for new/modified code (FC-2)
- [ ] Tests written during implementation — not deferred (FC-100)
- [ ] IDOR test present if any action accepts external ID
- [ ] i18n key presence test for new translation keys (GLOB-187)
- [ ] Edge cases covered: empty input, max length, concurrent access if relevant
- [ ] Static code checks passing (FC-1)

### UX Expert
SAP Product Standards: UXC-*, ACC-*

- [ ] SAP UI5 / Fiori design system components used — no custom replacements (UXC-010 to UXC-030)
- [ ] Correct SAP theming variables used — no hardcoded colors (UXC-010, UXC-011)
- [ ] SAP icons used from SAP icon font — no custom icon sets (UXC-013, UXC-019)
- [ ] Shell bar, side navigation, user menu follow SAP standard patterns (UXC-016, UXC-026, UXC-020)
- [ ] Accessibility: keyboard navigable, ARIA labels, visible focus (ACC-270, ACC-271)
- [ ] Minimum contrast ratios met (ACC-261)
- [ ] RTL layout supported if project targets RTL locales (GLOB-179)
- [ ] Error and message handling uses SAP standard message patterns (UXC-023)
- [ ] No physical CSS direction properties — logical CSS or SAP layout components only

### i18n/L10n Expert
SAP Product Standards: GLOB-*

- [ ] Zero hardcoded strings in new/modified components (GLOB-187)
- [ ] All new translation keys present in ALL locale files (GLOB-146)
- [ ] No concatenated translations — use ICU MessageFormat or SAP i18n patterns (GLOB-187)
- [ ] Date, time, number, currency formatting uses locale-aware SAP APIs (GLOB-186, GLOB-185)
- [ ] RTL/LTR layout handled correctly for all supported locales (GLOB-179)
- [ ] Fallback language (English) always available (GLOB-57)

### Chief Architect
SAP Product Standards: DPC-046, INTG-*, SLC-*

- [ ] Implementation matches the plan from Phase 2
- [ ] No new technical debt without explicit reasoning
- [ ] No patterns that break existing architecture boundaries (DPC-046)
- [ ] Cross-cutting concerns (auth, logging, error handling) consistent with codebase
- [ ] API design follows SAP API Guidelines if new endpoints added (INTG-03R1R2, INTG-03R5)
- [ ] Open Resource Discovery (ORD) updated if new APIs/events exposed (INTG-03R3)
- [ ] BTP service bindings and destinations follow SAP patterns (INTG-04R1)
- [ ] No unrelated changes included

---

## SAP Product Standards — full check

The requirements index is at `C:\BDC\sap-kb-skills\product-standards\requirements-index.md`.
The compliance guide is at `C:\BDC\sap-kb-skills\product-standards\guide.md`.

**Which standards apply to this change — quick filter:**

| Change type | Standards to check |
|-------------|-------------------|
| Any auth / identity change | INTG-02R1, SEC-230, SEC-248, SEC-376 |
| New API endpoint | INTG-03R1R2, INTG-03R3, INTG-03R5, SEC-390 |
| UI change | UXC-010–030, ACC-252–287 |
| Personal data touched | DPP-224, DPP-254, DPP-256, DPP-362, DPP-366 |
| New dependency | SDOL-025, LIC-1, LIC-2 |
| AI feature | SEC-380, SEC-381, DPP-350, DPP-367, DPC-070 |
| Schema / data model change | ILM-001, PERF-04 |
| New cloud service / BTP binding | INTG-04R1, CDE-060, SLC-19 |
| Logging / observability change | CDE-48R1R2R3, CDE-50R1R2R3, SEC-215 |

---

## Audit report format

```markdown
## Audit Result: [PASS | FAIL]
_Date: YYYY-MM-DD_

### Blockers (must fix before proceeding)
- [ ] BLOCK-001: <issue> — Domain: Security — Standard: SEC-376 — Severity: Critical

### Warnings (should fix, not blocking this cycle)
- [ ] WARN-001: <issue> — Domain: UX — Standard: UXC-011

### Passed
- [x] Security: all mutations authenticated, IAS used, secrets managed
- [x] DBA: migrations valid, all adapters updated
- [x] Tests: passing, coverage ≥80%
- [x] i18n: 0 hardcoded strings, all locales present
- [x] UX: SAP Fiori components, theming variables, accessibility
- [x] SAP Product Standards: compliant for applicable requirements
```

## If FAIL

1. Add each blocker to CURRENT.md "Blockers" section
2. Loop back to Phase 1 (Brainstorm) for the blockers
3. Do NOT proceed to Phase 5 until all blockers resolved
4. Warnings become new CURRENT.md tasks for next sprint (with reasoning)
