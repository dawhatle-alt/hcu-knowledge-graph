---
type: check
check_name: system_parameters
product: EM
status: skeleton
tags:
  - hcu
  - check
---

# Check — system_parameters

**Section:** [[EM-check_config_results]] · **Report:** [[Artifact-check_config_report-json]]

**Config source:** `DB: PARAMS`

**Components:** [[Component-Gateway-GTW]]

> Sample environment: version 9.0.22.100, production size **Medium** (110,198 jobs / 145,293 executions / 15 users). Minimums below are the thresholds check_config applied at this size — they scale with production size.

## Parameters

| Parameter | Minimum expected | Example detected | Source path | Note |
|---|---|---|---|---|
| `GtwNumUpdateThreads` | 6 | 12 | `` |  |

## What it validates

EM system parameters stored in the database (`PARAMS` table) rather than in a
config file — currently a single parameter:

- `GtwNumUpdateThreads` — the number of update-processing threads in the
  [[Component-Gateway-GTW]]. The Gateway is the funnel through which every job
  state change from Control-M/Server reaches EM; this thread pool determines
  how many of those updates it can process in parallel.
  > [UNVERIFIED — confirm against docs] these threads write the updates to the
  > EM database, so raising the value also raises concurrent DB write load.

The minimum **scales with `production_size`**: 6 is the Medium-size threshold
from the sample archive (110,198 jobs / 145,293 executions). Environments with
higher execution volume are held to higher minimums — always state the size
with the number.

Note the config source: because this lives in the database, it is changed with
EM system-parameter tooling, not by editing a file in the archive.

## When it fails

Too few update threads for the environment's execution volume means the
Gateway falls behind the stream of job updates. Symptoms in the archive:

- Sustained growth in GTW queue/pending-update metrics in
  [[Artifact-metric-csvs]] (`GTW_by_type/date.csv`) — the primary
  early-warning signal.
- The GUI showing job states lagging behind reality (updates arrive late, not
  never), with `gtw_log.<DC>.*` in [[EM-Log]] showing the Gateway busy but not
  erroring.
- Often fails alongside [[Check-defaults_rsc]], since both size Gateway
  throughput.

Symptoms → [[Finding-gtw-update-backlog]]
