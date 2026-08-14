---
type: artifact
status: skeleton
tags:
  - hcu
  - artifact
---

# metrics_validation_EM report

**Archive path:** `report/observability/metrics_validation_EM_<ts>.{txt,json,html}` · **Section:** [[report-observability]]

Metrics Validator CLI: connects to the EM DB, lists configured metrics, validates custom observability metrics against a difference threshold. 'No rows for current EM SQL filters' warnings usually mean hostname-parameter mismatch in custom metric SQL.
