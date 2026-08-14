---
type: meta
status: skeleton
tags:
  - hcu
  - meta
---

# About This Vault

## Purpose
Source of truth for AI agents (and humans) interpreting Control-M HCU
(`ctm_data_collector`) archives during diagnosis.

## Note types (frontmatter `type`)
| type | folder | one note per |
|---|---|---|
| `archive-section` | 10-Archive-Sections | directory in the HCU archive |
| `check` | 20-Checks | check_config health check |
| `artifact` | 25-Artifacts | key file/report format |
| `component` | 30-Components | EM/Control-M component |
| `finding` | 40-Findings | observable abnormal pattern |
| `root-cause` | 50-Root-Causes | underlying mechanism |
| `resolution` | 60-Resolutions | fix procedure |

## Conventions
- Wikilinks are the graph. Findings link → root causes link → resolutions; checks and
  artifacts link to components and sections.
- `status: skeleton` = structure generated deterministically from a real archive,
  enrichment pending. `status: seeded` / `status: enriched` after review.
- All customer identifiers are sanitized (`<hostname>`, `<n>`, `<ts>`).
- Thresholds in check notes are **size-dependent** — never quote a minimum without the
  `production_size` context.

## Retrieval rules for agents
1. Prefer structured sources (check_config JSON, metric CSVs) over prose logs.
2. Before reasoning about a missing file, verify collection succeeded in
   [[Artifact-hcu-collector-log]].
3. Match symptoms against `Finding-*` signatures first; only free-form log analysis when
   no finding matches — and propose a new Finding note when done.
