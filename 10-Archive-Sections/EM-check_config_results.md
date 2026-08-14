---
type: archive-section
section: EM/check_config_results
status: skeleton
tags:
  - hcu
  - section
---

# EM-check_config_results

Output of the **check_config** health check utility (`em_check_config.sh -st all`). This is the closest thing in the archive to a formal pass/fail health report. Contains `check_config.txt` (invocation summary: checks performed / failed) plus one CSV + JSON report per historical run. Parse the **latest JSON** first — it is the structured source of truth for check results. See [[Artifact-check_config_report-json]].

**Parent:** [[EM]]

**Checks:** [[Check-machine]] · [[Check-communication]] · [[Check-defaults_rsc]] · [[Check-controlm-web-context]] · [[Check-reporting-facility-context]] · [[Check-system_parameters]] · [[Check-tomcat_config]] · [[Check-tomcat_server]] · [[Check-automation_api_properties]] · [[Check-site_config]]

## File inventory (normalized)

- `check_config.txt`
- `check_config_report_<ts>.csv`
- `check_config_report_<ts>.json`
