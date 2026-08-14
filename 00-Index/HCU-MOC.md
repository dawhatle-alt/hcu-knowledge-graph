---
type: moc
status: skeleton
tags:
  - hcu
  - moc
---

# HCU Knowledge Graph — Master Map of Content

Source of truth for interpreting **Control-M Health Check Utility
(`ctm_data_collector`)** archives across all three products. Notes carry
`product:` frontmatter; EM note names are unprefixed (the vault started
EM-only), Server and Agent notes are prefixed `Server-` / `Agent-`.

**Agent entry protocol:**
1. Read [[About-This-Vault]] for schema and retrieval rules.
2. Identify the product from the archive folder name and layout:
   - `ctm_data_collector_*` with an `EM/` folder → **EM** → [[EM-MOC]]
   - `ctm_data_collector_*` with `CNF_INFO`/`LOG_INFO`/`TBL_INFO` → **Server** → [[Server-MOC]]
   - `_data_*` with `AG_CNF`/`AG_LOG` → **Agent** → [[Agent-MOC]]
3. Follow that product MOC's entry protocol from its archive-root note.
4. Judge archive completeness via the collector log ([[Artifact-hcu-collector-log]]
   format) before concluding anything from a *missing* file.
5. Route symptoms via [[Diagnostic-Playbooks-MOC]].

## Product maps
- [[EM-MOC]] — Enterprise Manager (sample: EM 9.0.22.100, PostgreSQL, Medium size)
- [[Server-MOC]] — Control-M/Server (sample: 9.0.21.300, Linux, Oracle-backed)
- [[Agent-MOC]] — Control-M/Agent (sample: 9.0.21.300, Linux)

## Vault-wide notes
- [[About-This-Vault]] — schema, conventions, retrieval rules
- [[Diagnostic-Playbooks-MOC]] — symptom-class routing
- Diagnostic chains (Findings → Root Causes → Resolutions) are listed per
  product in the product MOCs.
