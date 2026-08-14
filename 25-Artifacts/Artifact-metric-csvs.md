---
type: artifact
status: skeleton
tags:
  - hcu
  - artifact
---

# Component metric CSVs (report/)

**Archive path:** `report/{GSR,GTW,Environment,db_performance}_by_{type,date}.csv` · **Section:** [[report]]

Time-series metric extracts per component. Columns (GSR/GTW): `name, comp_name, hostname, value, metric_time, pid` — e.g. GSR 'Pending Updates' per connected component over time. `_by_type` groups by metric name; `_by_date` is chronological. Sustained growth in queue/pending metrics is a primary early-warning signal.
