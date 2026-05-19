---
name: wiki
description: SAP Wiki (Confluence) integration. Load before any Wiki operation. MCP decision tree + raw REST fallback.
trigger: manual
---

# SAP Wiki Integration

## Step 0 — Authenticate first

Call `mcp__sap_auth__sap_authenticate` with:
- `entry_url`: `"https://wiki.one.int.sap"`
- `store_path`: `"C:\\Users\\<I-NUMBER>\\.sap-auth"`

Same cookie store as Jira — one `sap_authenticate` call covers both if done in same session.

---

## Step 1 — Check which MCP is available

If `mcp__sap_wiki__*` tools appear in your tool list, use them (Option A).
If not, use raw Python REST (Option B).

## Option A — sap-wiki MCP (if installed)

The `sfsfmcp/sap-wiki-mcp` MCP provides:
- `mcp__sap_wiki__search_pages` — keyword or CQL search
- `mcp__sap_wiki__get_page` — fetch page content by ID or title
- `mcp__sap_wiki__create_page` — create new page in a space
- `mcp__sap_wiki__update_page` — update existing page content
- `mcp__sap_wiki__add_comment` — add comment to page

Install if not present — add to `~/.claude.json` mcpServers:
```json
"sap-wiki": {
  "command": "npx",
  "args": ["-y", "git+https://github.tools.sap/sfsfmcp/sap-wiki-mcp.git"],
  "env": { "AUTH_COOKIE_DIR": "C:\\Users\\<I-NUMBER>\\.sap-auth" }
}
```

## Option B — Raw Python REST

```python
import json, urllib.request

with open('C:/Users/<I-NUMBER>/.sap-auth/sap_cookies.json') as f:
    cookies = json.load(f)['cookies']

cookie_header = '; '.join(
    f'{c["name"]}={c["value"]}'
    for c in cookies if 'wiki.one.int.sap' in c.get('domain', '')
)
HEADERS = {'Cookie': cookie_header, 'Accept': 'application/json'}
BASE = 'https://wiki.one.int.sap/rest/api'

def wiki_get(path):
    req = urllib.request.Request(f'{BASE}/{path}', headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def wiki_post(path, payload):
    req = urllib.request.Request(
        f'{BASE}/{path}',
        data=json.dumps(payload).encode(),
        headers={**HEADERS, 'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

## Search pages

```python
results = wiki_get('content/search?cql=text~"search term"+AND+space="SPACEID"&limit=10')
for r in results['results']:
    print(r['id'], r['title'])
```

## Get page content

```python
page = wiki_get('content/PAGE_ID?expand=body.storage,version')
title = page['title']
body = page['body']['storage']['value']
version = page['version']['number']
```

## Create page

```python
result = wiki_post('content', {
    'type': 'page',
    'title': 'Page Title',
    'space': {'key': 'SPACEID'},
    'ancestors': [{'id': 'PARENT_PAGE_ID'}],
    'body': {
        'storage': {
            'value': '<p>Page content in HTML storage format</p>',
            'representation': 'storage'
        }
    }
})
print(result['id'], result['_links']['webui'])
```

## Update page (must increment version)

```python
# Fetch current version first (see "Get page content" above)
req = urllib.request.Request(
    f'{BASE}/content/PAGE_ID',
    data=json.dumps({
        'version': {'number': version + 1},
        'title': 'Updated Title',
        'type': 'page',
        'body': {'storage': {'value': '<p>Updated</p>', 'representation': 'storage'}}
    }).encode(),
    headers={**HEADERS, 'Content-Type': 'application/json'},
    method='PUT'
)
with urllib.request.urlopen(req) as r:
    pass  # 200 OK on success
```

## If all methods fail

Stop after 2 attempts. Tell the user what was tried. Ask for help.
