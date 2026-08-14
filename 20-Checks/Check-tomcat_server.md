---
type: check
check_name: tomcat_server
product: EM
status: skeleton
tags:
  - hcu
  - check
---

# Check — tomcat_server

**Section:** [[EM-check_config_results]] · **Report:** [[Artifact-check_config_report-json]]

**Config source:** `/ctrlmdata/ctmem/ctm_em/etc/emweb/tomcat/conf/server.xml`

**Components:** Tomcat

> Sample environment: version 9.0.22.100, production size **Medium** (110,198 jobs / 145,293 executions / 15 users). Minimums below are the thresholds check_config applied at this size — they scale with production size.

## Parameters

| Parameter | Minimum expected | Example detected | Source path | Note |
|---|---|---|---|---|
| `Connector maxThreads` | 500 | 1200 | `./Service/Connector[@scheme='https']###maxThreads` |  |

## What it validates

_(enrichment pending)_

## When it fails

_(enrichment pending — link findings here)_
