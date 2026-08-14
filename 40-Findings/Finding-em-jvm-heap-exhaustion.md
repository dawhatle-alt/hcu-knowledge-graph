---
type: finding
status: skeleton
tags:
  - hcu
  - finding
---

# Finding — EM component JVM heap exhaustion

**Seen in:** `EM/TBL/java_memory.csv`, `EM/Log/jvm-*` and `*_exceptions*` logs · **Components:** [[Component-GUI-Server-GSR]] · [[Component-Configuration-Server-CMS]] · [[Component-Gateway-GTW]]

An EM server component (GSR/CMS/GTW) or utility runs at or near its configured
maximum heap: sluggish responses, GC-dominated behavior, and in the worst case
`OutOfMemoryError` with component restarts.

_(stub — created from [[Check-site_config]] enrichment; signature strings and
archive examples pending a worked case)_

## Signature

- `OutOfMemoryError` in the component's `jvm-*` / `*_exceptions*` logs
- Heap-used ≈ heap-max for the component's row in [[Artifact-java_memory-csv]]

_(exact grep-able strings pending)_

## Where in the HCU archive

- [[Artifact-java_memory-csv]] (`EM/TBL/java_memory.csv`) — per-process snapshot
- `jvm-*` GC logs and `*_exceptions*` logs in [[EM-Log]]
- Heap settings that were in force: [[Check-site_config]] / [[Artifact-EMSiteConfig-ini]]

## Interpretation

Cross-check the flagged component's actual usage against its `Heap*` setting
before concluding the heap is undersized — and check [[Check-machine]] before
recommending an increase: on a RAM-tight host
([[Finding-em-host-resource-shortage]]) raising heaps moves the problem to the
OS.

## Root causes

- _(pending — link RootCause when a case is worked)_
