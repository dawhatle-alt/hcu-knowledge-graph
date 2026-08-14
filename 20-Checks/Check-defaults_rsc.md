---
type: check
check_name: defaults_rsc
product: EM
status: skeleton
tags:
  - hcu
  - check
---

# Check — defaults_rsc

**Section:** [[EM-check_config_results]] · **Report:** [[Artifact-check_config_report-json]]

**Config source:** `/ctrlmdata/ctmem/ctm_em/etc/resource/Defaults.rsc`

**Components:** [[Component-Gateway-GTW]]

> Sample environment: version 9.0.22.100, production size **Medium** (110,198 jobs / 145,293 executions / 15 users). Minimums below are the thresholds check_config applied at this size — they scale with production size.

## Parameters

| Parameter | Minimum expected | Example detected | Source path | Note |
|---|---|---|---|---|
| `dwl_batch_size` | 1200 | 1600 | `` |  |

## What it validates

Gateway download batching, read from [[Artifact-Defaults-rsc]]:

- `dwl_batch_size` — the batch size the [[Component-Gateway-GTW]] uses when
  downloading the active jobs net from Control-M/Server to EM. Larger batches
  mean fewer round trips to move the same net, so download/sync completes
  faster on large actives.
  > [UNVERIFIED — confirm against docs] the unit is jobs per download batch.

The minimum **scales with `production_size`**: 1200 is the Medium-size
threshold from the sample archive (110,198 jobs). Larger environments — bigger
active nets — are held to higher minimums; state the size with the number.

## When it fails

An undersized download batch drags out net download and Gateway
synchronization, which users experience as EM being slow to reflect the
Control-M/Server state (most visible after New Day, a Gateway restart, or
reconnect). Look for:

- Long or repeated download cycles in `gtw_log.<DC>.*` / `gtw_diag.*` in
  [[EM-Log]].
- GTW pending/queue metrics climbing during download windows in
  [[Artifact-metric-csvs]].
- Often fails alongside [[Check-system_parameters]]
  (`GtwNumUpdateThreads`) — both size Gateway throughput, and check_config
  flags them together when a growing environment has outgrown its Gateway
  tuning.

Symptoms → [[Finding-gtw-update-backlog]]
