---
name: jira
description: SAP Jira integration. Load before ANY Jira operation. Decision tree + known failures + working Python REST patterns.
trigger: manual
---

# SAP Jira Integration

## Step 0 — Authenticate first (every session)

Call `mcp__sap_auth__sap_authenticate` with:
- `entry_url`: `"https://jira.tools.sap"`
- `store_path`: `"C:\\Users\\<I-NUMBER>\\.sap-auth"`

Replace `<I-NUMBER>` with actual I-number (e.g. `I053580`).
Cookies persist 24-168h but call this every session — it is a no-op if already valid.

---

## Step 1 — Decision tree: which method to use?

| Operation | Method | Notes |
|-----------|--------|-------|
| Search issues (JQL) | `mcp__sap_jira__search_issues` | Works reliably |
| Get single issue | `mcp__sap_jira__get_issue` | Works reliably |
| Add comment | `mcp__sap_jira__add_comment` | Works reliably |
| Update summary/description/labels | `mcp__sap_jira__update_issue` | Works for standard fields |
| Create issue — NO custom fields | `mcp__sap_jira__create_issue` | Works (summary/description/priority only) |
| Create issue — WITH Team/Epic/Sprint | **Raw Python REST** (see below) | MCP fails — see warning |
| Transitions (status changes) | **Raw Python REST** (see below) | More reliable than MCP |
| Bulk operations | **Raw Python REST** | MCP has no bulk support |

## CRITICAL: MCP cannot set custom fields on create

`mcp__sap_jira__create_issue` CANNOT set:
- `customfield_26740` (Team field)
- `customfield_15140` (Epic Link)
- `customfield_12740` (Sprint)

These fields silently fail or return HTTP 400. The MCP wraps them in an update
operation after creation, and Jira rejects the format. **Use raw Python REST instead.**

This is documented from production use — not theoretical.

---

## Step 2 — Raw Python REST setup

```python
import json, urllib.request, urllib.error

# Load cookies (call sap_authenticate first to refresh)
with open('C:/Users/<I-NUMBER>/.sap-auth/sap_cookies.json') as f:
    data = json.load(f)

cookies = data['cookies']
cookie_header = '; '.join(
    f'{c["name"]}={c["value"]}'
    for c in cookies if 'jira.tools.sap' in c.get('domain', '')
)
xsrf = next(c['value'] for c in cookies if c['name'] == 'atlassian.xsrf.token')

HEADERS = {
    'Content-Type': 'application/json',
    'Cookie': cookie_header,
    'X-Atlassian-Token': xsrf,  # required for all write operations
}

BASE = 'https://jira.tools.sap/rest/api/2'

def jira_post(path, payload):
    req = urllib.request.Request(
        f'{BASE}/{path}',
        data=json.dumps(payload).encode(),
        headers=HEADERS,
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Jira {e.code}: {e.read().decode()}')

def jira_put(path, payload):
    req = urllib.request.Request(
        f'{BASE}/{path}',
        data=json.dumps(payload).encode(),
        headers=HEADERS,
        method='PUT'
    )
    with urllib.request.urlopen(req) as r:
        return r.status

def jira_get(path):
    req = urllib.request.Request(
        f'{BASE}/{path}',
        headers={'Cookie': cookie_header, 'Accept': 'application/json'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

---

## Create issue with all fields

```python
result = jira_post('issue', {'fields': {
    'project': {'key': 'PROJECT_KEY'},
    'issuetype': {'id': '11'},              # 11=User Story, 12=Activity, 10=Epic
    'summary': 'Issue title here',
    'description': 'Jira wiki markup body',
    'priority': {'name': 'High'},            # Very High / High / Medium / Low
    'labels': ['label1', 'label2'],
    # Custom fields — exact format matters, wrong format causes silent fail
    'customfield_15140': 'EPIC-KEY',         # Epic Link — plain string key, NOT object
    'customfield_26740': '267',              # Team — STRING id, NOT {"id": 267}
    'customfield_12740': 360280,             # Sprint — INTEGER id, NOT string
    'timetracking': {'originalEstimate': '5d'},  # S=1d, M=5d, L=15d, XL=25d
}})
print(result['key'])  # e.g. PROJECT-36757
```

## Transition issue (change status)

```python
# First: get available transitions
transitions = jira_get(f'issue/{issue_key}/transitions')
for t in transitions['transitions']:
    print(t['id'], t['name'])

# Then: apply transition
jira_post(f'issue/{issue_key}/transitions', {
    'transition': {'id': '11'},  # use ID from above
    'comment': {'body': 'Reason for transition'}  # optional
})
```

## Update standard fields

```python
jira_put(f'issue/{issue_key}', {'fields': {
    'summary': 'New title',
    'description': 'New description',
    'labels': ['updated-label'],
    'priority': {'name': 'Medium'},
}})
# Returns 204 No Content on success
```

## Search with JQL

```python
result = jira_get('search?jql=project=MYPROJECT+AND+status="In Progress"&maxResults=50')
for issue in result['issues']:
    print(issue['key'], issue['fields']['summary'])
```

---

## Jira wiki markup cheatsheet

```
h1. Heading 1    h2. Heading 2    h3. Heading 3
*bold*           _italic_         +underline+
{{monospace}}
* bullet item    # numbered item
[link text|https://url]
{code:python}...{code}
||header1||header2||
|cell1|cell2|
```

## Finding field IDs for a project

```python
# Get issue type IDs for a project
meta = jira_get('issue/createmeta?projectKeys=PROJECT_KEY&expand=projects.issuetypes')
for it in meta['projects'][0]['issuetypes']:
    print(it['id'], it['name'])

# Get sprint IDs
sprints = jira_get('board/BOARD_ID/sprint?state=active,future')
for s in sprints['values']:
    print(s['id'], s['name'], s['state'])
```

## If all methods fail

Stop. Do not loop. Tell the user what was tried and ask for help.
Maximum 2 retry attempts. If 2nd attempt fails, escalate immediately.
