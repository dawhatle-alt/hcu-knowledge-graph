---
type: check
check_name: site_config
product: EM
status: skeleton
tags:
  - hcu
  - check
---

# Check — site_config

**Section:** [[EM-check_config_results]] · **Report:** [[Artifact-check_config_report-json]]

**Config source:** `/ctrlmdata/ctmem/ctm_em/ini/EMSiteConfig.ini`

**Components:** [[Component-Configuration-Server-CMS]] · [[Component-GUI-Server-GSR]] · [[Component-Gateway-GTW]] · Configuration Agent · EM Util · Forecast · SLA Management · Self Service

> Sample environment: version 9.0.22.100, production size **Medium** (110,198 jobs / 145,293 executions / 15 users). Minimums below are the thresholds check_config applied at this size — they scale with production size.

## Parameters

| Parameter | Minimum expected | Example detected | Source path | Note |
|---|---|---|---|---|
| `jvm_properties/AutoIncHeapTimes` | 3 | 5 | `` |  |
| `jvm_properties/AutoIncHeapSize` | 250 | 300 | `` |  |
| `jvm_properties/HeapGSR` | 512 | 2048 | `` |  |
| `jvm_properties/HeapUTIL` | 2048 | 4096 | `` |  |
| `jvm_properties/HeapCMS` | 512 | 1024 | `` |  |
| `jvm_properties/HeapGTW` | 512 | 1024 | `` |  |

## What it validates

JVM heap sizing for the core EM server components, read from the `jvm_properties`
section of [[Artifact-EMSiteConfig-ini]]:

- `HeapGSR` / `HeapCMS` / `HeapGTW` — maximum Java heap (MB) for the
  [[Component-GUI-Server-GSR]], [[Component-Configuration-Server-CMS]] and
  [[Component-Gateway-GTW]] processes. Undersized heaps on these three are the
  most common self-inflicted cause of EM sluggishness: the JVM spends its time
  in garbage collection instead of serving requests.
- `HeapUTIL` — maximum heap for EM utility processes (e.g. batch utilities run
  under EM Util). Utilities that walk large job/definition sets need this
  headroom even when the always-on servers are healthy.
- `AutoIncHeapTimes` / `AutoIncHeapSize` — the automatic heap-increase
  mechanism: how many times a component's heap may be auto-increased, and by
  how many MB each step. > [UNVERIFIED — confirm against docs] the increase is
  applied when EM restarts a component after it exhausts its configured heap.

The minimums check_config applies here **scale with `production_size`** — the
values in the table above are the Medium-size thresholds from the sample
archive (110,198 jobs / 15 users). A Large environment is held to higher
minimums; never quote these numbers without stating the size they belong to
(read `production_size` from [[Artifact-check_config_report-json]] first).

## When it fails

A failed `site_config` check means one or more components are running with less
heap than check_config expects for the environment's size. Concrete symptoms
to look for in the same archive:

- Heap usage at or near the configured maximum in
  [[Artifact-java_memory-csv]] for the flagged component.
- GC-heavy behavior or `OutOfMemoryError` entries in that component's
  `jvm-*` / `_exceptions` logs in [[EM-Log]], often with component restarts.
- Client-visible sluggishness routed through the "Memory / OOM" row of
  [[Diagnostic-Playbooks-MOC]].

Symptoms → [[Finding-em-jvm-heap-exhaustion]]
