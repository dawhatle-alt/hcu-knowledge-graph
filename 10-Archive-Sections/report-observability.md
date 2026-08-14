---
type: archive-section
section: report/observability
status: skeleton
tags:
  - hcu
  - section
---

# report-observability

Metrics Validator CLI output (`metrics_validation_EM_*.{txt,json,html}`): connects to the EM DB, enumerates configured metrics, and validates custom observability metrics against thresholds. Warnings about custom metrics with 'no rows for current EM SQL filters' usually indicate hostname-parameter mismatches in custom metric SQL.

**Parent:** [[report]]

## File inventory (normalized)

- `metrics_validation_EM_<n>_<n>.html`
- `metrics_validation_EM_<n>_<n>.json`
- `metrics_validation_EM_<n>_<n>.txt`
