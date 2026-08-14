---
type: component
status: skeleton
tags:
  - hcu
  - component
---

# Gateway (GTW)

Per-datacenter gateway between EM and Control-M/Server. Download batch size from `dwl_batch_size` in Defaults.rsc ([[Check-defaults_rsc]]); update threads from `GtwNumUpdateThreads` system parameter ([[Check-system_parameters]]); heap from `HeapGTW` ([[Check-site_config]]).

**Archive sections:** [[EM-Log]] · [[EM-Rsc]] · [[EM-DBT]]

Logs: `gtw_log.<DC>.*` and `gtw_diag.*` in [[EM-Log]]; metrics in GTW_by_type/date.csv; db latency via [[Artifact-db-perf-sort-report]] (run through GTW).

## Known findings

_(enrichment pending)_
