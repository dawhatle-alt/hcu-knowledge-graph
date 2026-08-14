---
type: artifact
status: skeleton
tags:
  - hcu
  - artifact
---

# db-perf-sort-report.txt

**Archive path:** `report/db-perf-sort-report.txt` · **Section:** [[report]]

Output of `em gtw -db_perf`: a fixed battery of DB operation tests (insert/update iterations, bulk inserts, etc.) with elapsed and AVG per operation, plus DB major release. The AVG values are the comparable numbers across environments and over time; elevated averages indicate DB-side latency affecting all EM DB writers.
