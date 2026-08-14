---
type: check
check_name: communication
product: EM
status: skeleton
tags:
  - hcu
  - check
---

# Check — communication

**Section:** [[EM-check_config_results]] · **Report:** [[Artifact-check_config_report-json]]

**Config source:** `/ctrlmdata/ctmem/ctm_em/etc/domains/communication.xml`

**Components:** [[Component-Configuration-Server-CMS]] · [[Component-GUI-Server-GSR]]

> Sample environment: version 9.0.22.100, production size **Medium** (110,198 jobs / 145,293 executions / 15 users). Minimums below are the thresholds check_config applied at this size — they scale with production size.

## Parameters

| Parameter | Minimum expected | Example detected | Source path | Note |
|---|---|---|---|---|
| `GSR NumWorkers` | 200 | 400 | `./scope[@name='GSR']/variable[@name='NumWorkers']###value` |  |
| `CMS NumWorkers` | 65 | 100 | `./scope[@name='CMS']/variable[@name='NumWorkers']###value` |  |

## What it validates

_(enrichment pending)_

## When it fails

_(enrichment pending — link findings here)_
