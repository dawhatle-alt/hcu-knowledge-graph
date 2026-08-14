---
type: artifact
product: Server
status: skeleton
tags:
  - hcu
  - artifact
---

# Thread pool reports (CtmThreadPool / NsThreadPool / Ns_PrintAll)

**Archive path:** `report/{CtmThreadPool,NsThreadPool,Ns_PrintAll}.txt` · **Section:** [[Server-report]]

`ctmipc ... CTL` outputs. `CtmThreadPool`: per-pool queue/threads/active/runs/peak/max with the CONFIG.* parameter that sizes each pool (e.g. `CTM_REQUEST_THREAD_POOL_SIZE`). `NsThreadPool`/`Ns_PrintAll`: per-agent running/pending communication threads. peak==max with queueing suggests an undersized pool.
