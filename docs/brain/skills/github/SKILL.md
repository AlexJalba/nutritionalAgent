---
name: github
description: SAP GitHub (github.tools.sap) integration. gh CLI primary, cookie REST fallback. Load before any GitHub operation.
trigger: manual
---

# SAP GitHub Integration

## Two SAP GitHub instances

| Domain | Used for | Auth |
|--------|---------|------|
| `github.tools.sap` | Most SAP repos (primary) | `gh` CLI with `GH_HOST` |
| `github.wdf.sap.corp` | Older WDF repos | Separate browser auth needed |

## Step 0 — Authenticate

```bash
GH_HOST=github.tools.sap gh auth status
# If not authenticated:
GH_HOST=github.tools.sap gh auth login
```

## Decision tree

| Need | Method |
|------|--------|
| Any `github.tools.sap` operation | `gh` CLI with `GH_HOST=github.tools.sap` (Option A) |
| `gh` CLI unavailable or failing | Cookie REST (Option B) |
| `github.wdf.sap.corp` access | Playwright (Option C) |

**Never use `mcp__github__*` tools for `github.tools.sap`** — they do not work reliably with this instance.

## Option A — `gh` CLI (primary, always prefer this)

```bash
# All commands require GH_HOST prefix
GH_HOST=github.tools.sap gh issue list --repo ORG/REPO --state open
GH_HOST=github.tools.sap gh issue create --repo ORG/REPO --title "Title" --body "Body"
GH_HOST=github.tools.sap gh issue comment 123 --repo ORG/REPO --body "Comment"
GH_HOST=github.tools.sap gh issue close 123 --repo ORG/REPO
GH_HOST=github.tools.sap gh pr list --repo ORG/REPO --state open
GH_HOST=github.tools.sap gh pr merge 4 --repo ORG/REPO --squash
GH_HOST=github.tools.sap gh pr create --repo ORG/REPO --title "Title" --body "Body"
GH_HOST=github.tools.sap gh api repos/ORG/REPO/contents/path/to/file.md
```

## Option B — Cookie REST (fallback if gh CLI unavailable)

Authenticate via sap-auth first:
```bash
mcp__sap_auth__sap_authenticate entry_url="https://github.tools.sap" store_path="C:\Users\<I-NUMBER>\.sap-auth"
```

```python
import json, urllib.request

with open('C:/Users/<I-NUMBER>/.sap-auth/sap_cookies.json') as f:
    cookies = json.load(f)['cookies']

cookie_header = '; '.join(
    f'{c["name"]}={c["value"]}'
    for c in cookies if 'github.tools.sap' in c.get('domain', '')
)
HEADERS = {
    'Cookie': cookie_header,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'claude-dev-standards/1.0',
}
BASE = 'https://github.tools.sap/api/v3'

def gh_get(path):
    req = urllib.request.Request(f'{BASE}/{path}', headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def gh_post(path, payload):
    req = urllib.request.Request(
        f'{BASE}/{path}',
        data=json.dumps(payload).encode(),
        headers={**HEADERS, 'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

Common operations:
```python
issues = gh_get('repos/ORG/REPO/issues?state=open&per_page=50')
prs = gh_get('repos/ORG/REPO/pulls?state=open')
issue = gh_post('repos/ORG/REPO/issues', {'title': 'Title', 'body': 'Body', 'labels': ['bug']})
```

## Option C — Playwright (github.wdf.sap.corp or auth expired)

Use `playwright@claude-plugins-official` to navigate to the URL.
SAP SSO session in the browser will authenticate automatically.
Call `mcp__sap_auth__sap_authenticate` with `entry_url: "https://github.wdf.sap.corp"` for WDF domain.

## If all methods fail

Stop after 2 attempts. Tell the user what was tried. Ask for help.
