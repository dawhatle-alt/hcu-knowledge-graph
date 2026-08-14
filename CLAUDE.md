# CLAUDE.md — HCU Knowledge Graph Vault

This repo is an Obsidian vault: the source of truth for interpreting Control-M
Health Check Utility (`ctm_data_collector`) archives. It feeds an HCU analysis
agent (Claude skill now, Copilot Studio later). Notes are the product —
treat every edit as a change to a diagnostic reference a TSA will rely on.

## Session protocol

1. `git pull` before touching anything.
2. Work in **batches of 3–5 notes**, then STOP and summarize what changed for
   review. Do not continue to the next batch without explicit approval.
3. One folder per session unless told otherwise. Default order:
   `20-Checks` → `25-Artifacts` → `30-Components` → finding chains (40/50/60).
4. Commit per batch with a descriptive message:
   `enrich(checks): site_config, tomcat_server — validation + failure modes`
5. Never rewrite a note wholesale. Fill the pending sections; preserve the
   deterministic content (parameter tables, inventories, paths) exactly.

## Vault schema

Folders and frontmatter `type` (do not invent new types without asking):

| Folder | type | One note per |
|---|---|---|
| 00-Index | moc / meta | map of content |
| 10-Archive-Sections | archive-section | directory in the HCU archive |
| 20-Checks | check | check_config health check |
| 25-Artifacts | artifact | key file/report format |
| 30-Components | component | EM/Control-M component |
| 40-Findings | finding | observable abnormal pattern |
| 50-Root-Causes | root-cause | underlying mechanism |
| 60-Resolutions | resolution | fix procedure |
| 90-Templates | template | note templates — never edit these during enrichment |
| _tools | — | build_hcu_vault.py generator — do not modify during enrichment |

Full conventions live in `00-Index/About-This-Vault.md`. Read it once per
session before editing.

## Status lifecycle

`status: skeleton` → `status: enriched` (via `status: seeded` for notes drafted
from a case but not yet reviewed). Flip to `enriched` ONLY when the definition
of done below is met AND the batch was approved in review. Never flip status
in the same commit that drafts the content.

## Definition of done (per note type)

- **check**: "What it validates" explains the parameter's role in plain TSA
  language; "When it fails" lists concrete symptoms with wikilinks to at least
  one Finding (create a stub Finding if none exists); size-scaling behavior
  stated; no threshold quoted without production_size context.
- **artifact**: parse guidance an agent can execute (which fields, which order,
  what "normal" looks like); at least one link to a check or component.
- **component**: role, its log families in [[EM-Log]], its checks, and a
  "Known findings" list (may be empty but must say so explicitly).
- **finding**: a `## Signature` section with exact grep-able strings; archive
  paths where it appears; links to ≥1 root cause.
- **root-cause / resolution**: verification steps that use ONLY files present
  in an HCU archive; resolutions include a verification step and a KA
  placeholder if the KA number is unknown (`KA: [TBD]`).

## Content rules

- **Sanitization is absolute.** No customer hostnames, domains, account names,
  IPs, or case numbers anywhere. Use `<hostname>`, `<EM_HOME>`, `<n>`, `<ts>`.
  If source material contains them, strip while drafting — not in a later pass.
- **Wikilinks are the graph.** Every enriched note links to ≥2 other notes.
  New notes must be reachable from a MOC or another linked note — no orphans.
  Link format: `[[Note-Name]]`, matching filename exactly (case-sensitive).
- **Chains are directional.** Finding → RootCause → Resolution, with backlinks
  stated in prose. One note per concept — if a root cause serves two findings,
  link it from both; don't duplicate it.
- **No invented facts.** Product behavior claims must come from: the sample
  archive data already in the vault, material Darrell provides in-session
  (cases, KAs, docs), or clearly flagged as `> [UNVERIFIED — confirm against
  docs]`. When unsure, write the flag, not a guess.
- Version-specific behavior gets tagged inline: `(9.0.22.x)`. The sample
  baseline is EM 9.0.22.100.
- Thresholds scale with production_size (Small/Medium/Large). Always say which
  size a number belongs to.

## New notes

- Findings/RootCauses/Resolutions: copy the matching `90-Templates/tpl-*.md`,
  name as `Finding-<short-symptom>`, `RootCause-<short-mechanism>`,
  `Resolution-<short-action>` (hyphenated, no spaces).
- After adding any note, update the relevant MOC list in `00-Index/HCU-MOC.md`
  and, for findings, consider a row in `Diagnostic-Playbooks-MOC.md`.

## Never

- Never delete or rename existing notes without explicit instruction (renames
  break wikilinks — if approved, update every backlink in the same commit).
- Never edit `90-Templates/` or `_tools/` during enrichment sessions.
- Never commit directly after drafting a batch without the review stop.
- Never pull content from the internet into notes without flagging the source
  for review — this vault must stay authoritative, not scraped.
- Never touch `.obsidian/` settings.

## Validation before each commit

Run a link check: every `[[target]]` in changed notes resolves to an existing
file (templates' placeholder links like `[[Finding-...]]` are exempt, but only
inside 90-Templates). Report any dangling links in the batch summary instead
of silently creating stubs — stub creation is a review decision.
