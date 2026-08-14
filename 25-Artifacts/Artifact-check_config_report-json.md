---
type: artifact
status: skeleton
tags:
  - hcu
  - artifact
---

# check_config_report JSON

**Archive path:** `EM/check_config_results/check_config_report_<ts>.json` · **Section:** [[EM-check_config_results]]

Structured health check results. Top level: `product`, `location` (EM_HOME), `version`, `production_size` {jobs, executions, users, size} — thresholds scale with `size` (Small/Medium/Large). `results[]`: one entry per check with `check_name`, `status` (bool), `passed_check[]`/`failed_check[]` param entries {parameter_name, value_detected, minimum_expected, optional actual_parameter_name (XPath-ish source), optional message, components[]}, plus optional `location` and `user_override_file`.

**Agent rule:** always parse the *latest* JSON; the CSV is a flattened view of the same data. `production_size` must be read first — it is the context for every minimum.
