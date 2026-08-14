---
type: finding
status: skeleton
tags:
  - hcu
  - finding
---

# Finding — EM host RAM / disk shortage

**Seen in:** `EM/check_config_results/*`, `OS/Memory/*`, `OS/Disk/*` · **Components:** — (host-level)

The EM host fails or barely passes the [[Check-machine]] minimums: total RAM
below (or with no margin over) the size-scaled threshold, or free disk space
near the floor. Everything running on the host inherits the shortage.

_(stub — created from [[Check-machine]] enrichment; signature strings and
archive examples pending a worked case)_

## Signature

- `machine` in `failed_check[]` of [[Artifact-check_config_report-json]]
- Swap usage / low available memory in [[OS-Memory]] captures

_(exact grep-able strings pending)_

## Where in the HCU archive

- [[Artifact-check_config_report-json]] — the failed `machine` entry with
  detected vs minimum values
- [[OS-Memory]], [[OS-Disk]], [[OS-Hardware]] captures
- [[Artifact-disk-benchmark]] for I/O behavior of the affected filesystem

## Interpretation

Treat as a prerequisite failure: parameter tuning (heaps, thread pools) on a
starved host redistributes the shortage rather than fixing it. Downstream
symptoms often surface as [[Finding-em-jvm-heap-exhaustion]].

## Root causes

- _(pending — link RootCause when a case is worked)_
