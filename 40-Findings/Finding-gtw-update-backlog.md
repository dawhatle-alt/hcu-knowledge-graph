---
type: finding
status: skeleton
tags:
  - hcu
  - finding
---

# Finding — Gateway update backlog / slow download

**Seen in:** `report/GTW_by_{type,date}.csv`, `EM/Log/gtw_log.<DC>.*` · **Components:** [[Component-Gateway-GTW]]

Job state updates from Control-M/Server reach the EM GUI late, and/or net
download after New Day or Gateway restart takes conspicuously long. The
Gateway is busy but not erroring — a throughput problem, not an outage.

_(stub — created from [[Check-system_parameters]] / [[Check-defaults_rsc]]
enrichment; signature strings and archive examples pending a worked case)_

## Signature

- Sustained growth of GTW pending/queue metrics in
  [[Artifact-metric-csvs]] (`GTW_by_type/date.csv`)

_(exact metric names and grep-able log strings pending)_

## Where in the HCU archive

- [[Artifact-metric-csvs]] — GTW time series; growth trend is the signal
- `gtw_log.<DC>.*` and `gtw_diag.*` in [[EM-Log]]
- Tuning in force: [[Check-system_parameters]] (`GtwNumUpdateThreads`) and
  [[Check-defaults_rsc]] (`dwl_batch_size`)
- DB-side latency: [[Artifact-db-perf-sort-report]] (runs through GTW)

## Interpretation

Distinguish undersized Gateway tuning (check failures above) from a slow EM
database ([[Artifact-db-perf-sort-report]] latencies): more threads won't help
if every DB write is slow. Confirm which side is the bottleneck before
recommending parameter changes.

## Root causes

- _(pending — link RootCause when a case is worked)_
