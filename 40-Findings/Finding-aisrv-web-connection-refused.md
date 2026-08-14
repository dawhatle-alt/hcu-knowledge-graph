---
type: finding
status: seeded
tags:
  - hcu
  - finding
---

# Finding — aisrv-web TTransportException / Connection refused

`aisrv-web.log` shows `TTransportException` / `Connection refused` toward the Primary EM Web Server (TCP 18080) while network diagnostics (curl, DNS, routing) from the same host all pass.

**Where in the HCU archive:** `EM/Log/Services/aisrv-web*.log`, `aisrv-web_exceptions*.log`, `AiSrcServiceStart*.log`; correlate with [[OS-Network]] captures.

**Interpretation:** TCP 18080 is the EM Web Server port, not a dedicated AI port — the exception naming that endpoint does not by itself indicate a network fault. If no local AI process is running/listening, treat as failed local startup, not connectivity.

Root cause: [[RootCause-missing-lsof-prerequisite]]

**Components:** [[Component-aisrv-web-Jett-AI]]
