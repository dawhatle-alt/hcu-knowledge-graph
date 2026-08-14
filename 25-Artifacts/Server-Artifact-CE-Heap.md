---
type: artifact
product: Server
status: skeleton
tags:
  - hcu
  - artifact
---

# CE_Heap.txt

**Archive path:** `report/CE_Heap.txt` · **Section:** [[Server-report]]

`ctmipc -DEST CE -MSGID JMX -DATA HEAP` output: max/committed/used heap of the [[Server-Component-CE]] JVM. used≈max is the Server-side analogue of EM heap exhaustion.
