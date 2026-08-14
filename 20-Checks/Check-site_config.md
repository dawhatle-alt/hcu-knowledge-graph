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

_(enrichment pending)_

## When it fails

_(enrichment pending — link findings here)_
