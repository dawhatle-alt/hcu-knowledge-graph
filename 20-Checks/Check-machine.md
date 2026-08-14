---
type: check
check_name: machine
product: EM
status: skeleton
tags:
  - hcu
  - check
---

# Check — machine

**Section:** [[EM-check_config_results]] · **Report:** [[Artifact-check_config_report-json]]

**Components:** —

> Sample environment: version 9.0.22.100, production size **Medium** (110,198 jobs / 145,293 executions / 15 users). Minimums below are the thresholds check_config applied at this size — they scale with production size.

## Parameters

| Parameter | Minimum expected | Example detected | Source path | Note |
|---|---|---|---|---|
| `RAM (GB)` | 32 | 32.87 | `` |  |
| `free disk space (GB)` | 5 | 41.23 | `` |  |

## What it validates

Host-level capacity of the EM machine itself — the floor under every other
check:

- `RAM (GB)` — total physical memory on the EM host. This is the budget that
  all the JVM heaps validated by [[Check-site_config]] (plus Tomcat, services,
  PostgreSQL and the OS) must fit inside. Note the sample environment passes
  with almost no margin (32.87 detected vs 32 minimum) — a *passing* value can
  still be worth flagging when heap settings are being raised to fix other
  checks, because the RAM to back them has to exist.
- `free disk space (GB)` — free space on the EM installation filesystem.
  The 5 GB minimum is a floor for logs, temp files and normal operation, not a
  sizing recommendation.

Both minimums are the Medium-size thresholds from the sample archive and
**scale with `production_size`** — larger environments require more RAM;
always quote the size with the number.

## When it fails

A failed `machine` check means the host is under-provisioned regardless of how
well EM is tuned — fix this before (or alongside) any parameter tuning, since
raising heaps on a RAM-starved host trades one failure for another. Correlate
with:

- [[OS-Memory]] captures — swap in use / low available memory on the host.
- [[OS-Disk]] and [[Artifact-disk-benchmark]] — filesystem fill level and I/O
  behavior; a nearly-full disk also risks abrupt component stops when logs
  can't be written.
- Component-level symptoms that follow from the shortage, e.g.
  [[Finding-em-jvm-heap-exhaustion]] when heaps can't be raised because the
  RAM isn't there.

Symptoms → [[Finding-em-host-resource-shortage]]
