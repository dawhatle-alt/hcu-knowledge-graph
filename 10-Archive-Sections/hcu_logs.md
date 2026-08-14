---
type: archive-section
section: hcu_logs
status: skeleton
tags:
  - hcu
  - section
---

# hcu_logs

The collector's own execution log plus working data. Read this to judge archive **completeness**: 'Permission denied' and 'Source folder does not exist' entries explain why sections are missing or empty (e.g. remote DB → no local pgsql data; no OpenSearch → no observability store folders). A missing section is only meaningful if the collector actually tried and failed to collect it.

**Parent:** [[HCU-Archive-Root]]

## File inventory (normalized)

- `<hostname>_ctmem.log`
- `disk-benchmark-remove.txt`
