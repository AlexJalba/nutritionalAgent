# Copyright Headers — Reference

Every new source file MUST have a copyright header as the first content.
This rule strengthens IP enforceability by establishing SAP authorship on every artifact.

## Which format to use

Check `01-project-identity.md` → **License type** field:

| License type | Header format |
|---|---|
| `SAP-Internal` | SAP proprietary header |
| `Apache-2.0`, `MIT`, or other OSS | SPDX two-liner |

If the license type is not set, default to `SAP-Internal`.

---

## SAP Internal (proprietary) — default

### Python
```python
# SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved.
# SPDX-License-Identifier: SAP-Internal-Use-Only
```

### TypeScript / JavaScript
```typescript
// SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved.
// SPDX-License-Identifier: SAP-Internal-Use-Only
```

### Go
```go
// SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved.
// SPDX-License-Identifier: SAP-Internal-Use-Only
```

### Java / Kotlin
```java
// SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved.
// SPDX-License-Identifier: SAP-Internal-Use-Only
```

### HTML / XML / XSLT
```html
<!-- SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved. -->
<!-- SPDX-License-Identifier: SAP-Internal-Use-Only -->
```

### CSS / SCSS
```css
/* SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved. */
/* SPDX-License-Identifier: SAP-Internal-Use-Only */
```

### Shell (bash, sh, zsh)
```bash
# SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved.
# SPDX-License-Identifier: SAP-Internal-Use-Only
```

### YAML / TOML
```yaml
# SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved.
# SPDX-License-Identifier: SAP-Internal-Use-Only
```

### SQL
```sql
-- SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company. All rights reserved.
-- SPDX-License-Identifier: SAP-Internal-Use-Only
```

---

## SAP Open Source (REUSE-compliant)

Use when the project is published under an open-source license (Apache-2.0, MIT, etc.).

### Python
```python
# SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company and <repo> contributors
# SPDX-License-Identifier: Apache-2.0
```

### TypeScript / JavaScript
```typescript
// SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company and <repo> contributors
// SPDX-License-Identifier: Apache-2.0
```

### Go
```go
// SPDX-FileCopyrightText: <YEAR> SAP SE or an SAP affiliate company and <repo> contributors
// SPDX-License-Identifier: Apache-2.0
```

Replace `Apache-2.0` with the actual SPDX identifier matching the project's LICENSE file.

---

## Placement rules

1. **First content in the file** — before imports, before module docstrings, before any code
2. **After shebang only** — if the file has `#!/usr/bin/env ...`, the header goes on the line after it
3. **One blank line after the header** — then normal code begins
4. **`<YEAR>` = the year the file was created** — do not update on every edit (REUSE standard)

## Existing files without headers

Use the **lazy retrofit** approach: add headers only when you modify a file for other reasons. No bulk-migration PRs.

**Year to use:** The year the file was first committed. Determine via:
```bash
git log --follow --diff-filter=A --format=%ad --date=format:%Y -- <file> | tail -1
```

If the command returns empty (file added via merge commit or unusual history), fall back to the earliest commit that touches the file:
```bash
git log --follow --format=%ad --date=format:%Y -- <file> | tail -1
```

**Workflow:** When editing a file that lacks a header, prepend it before committing your functional change. This keeps copyright additions bundled with real work — no noise-only commits.

## Files that do NOT get headers

- `README.md`, `CHANGELOG.md`, and other documentation markdown files
- `package.json`, `tsconfig.json`, and JSON config files (JSON has no comment syntax)
- `.gitignore`, `.env.example`, and other dotfiles
- Binary files, images, fonts
- Auto-generated files (build output, lock files)
- Third-party vendored code (keep their original headers)

For projects using REUSE, these files are covered by the `.reuse/dep5` blanket declaration instead.

## REUSE dep5 template (for open-source projects)

Projects publishing to GitHub as open source should also include `.reuse/dep5`:

```
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: <repo-name>
Upstream-Contact: <team-email>
Source: https://github.com/SAP/<repo-name>

Files: *
Copyright: <YEAR> SAP SE or an SAP affiliate company and <repo-name> contributors
License: <SPDX-License-Identifier>
```

## LICENSE file at repo root

Every repository MUST have a LICENSE file. Use the format matching the project's license type:

- **SAP-Internal:** Copy from `ai-core-proxy/LICENSE` pattern in sap-kb-skills sources
- **Apache-2.0:** Standard Apache 2.0 text
- **MIT:** Standard MIT text with SAP SE copyright line
