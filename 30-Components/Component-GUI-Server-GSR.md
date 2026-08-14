---
type: component
status: skeleton
tags:
  - hcu
  - component
---

# GUI Server (GSR)

Serves EM client/GUI sessions. Worker pool sized by `GSR NumWorkers` in `communication.xml` ([[Check-communication]]); heap sized by `HeapGSR` in EMSiteConfig.ini ([[Check-site_config]]).

**Archive sections:** [[EM-Log]] · [[Thrift]] · [[EM-ini]]

Logs: `gsr_diag.*` snapshots in [[EM-Log]]; metrics in [[Artifact-metric-csvs|GSR_by_type/date.csv]].

## Known findings

_(enrichment pending)_
