---
type: check
check_name: controlm-web-context
product: EM
status: skeleton
tags:
  - hcu
  - check
---

# Check — controlm-web-context

**Section:** [[EM-check_config_results]] · **Report:** [[Artifact-check_config_report-json]]

**Config source:** `/ctrlmdata/ctmem/ctm_em/services/context/controlm-web.yml`

**User override file:** `/ctrlmdata/ctmem/ctm_em/services/config/custom/BootPropertiesUserOverride.yml` (overrides win over shipped defaults)

**Components:** [[Component-controlm-web]]

> Sample environment: version 9.0.22.100, production size **Medium** (110,198 jobs / 145,293 executions / 15 users). Minimums below are the thresholds check_config applied at this size — they scale with production size.

## Parameters

| Parameter | Minimum expected | Example detected | Source path | Note |
|---|---|---|---|---|
| `max_memory` | 3072 | 6164 | `` | Used user override from BootPropertiesUserOverride.yml |
| `min_memory` | 512 | 512 | `` | Used user override from BootPropertiesUserOverride.yml |

## What it validates

_(enrichment pending)_

## When it fails

_(enrichment pending — link findings here)_
