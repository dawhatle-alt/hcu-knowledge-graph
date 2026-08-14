---
type: root-cause
status: seeded
tags:
  - hcu
  - root-cause
---

# Root cause — `lsof` missing on minimal RHEL-family host

A Jett AI Python startup script shells out to `lsof`, which is absent on base/minimal RHEL-family installs (RHEL/AlmaLinux/Rocky/Oracle). The startup script fails silently before AI services initialize; the only visible error is the misleading outbound connect failure described in [[Finding-aisrv-web-connection-refused]].

**HCU verification:** check [[OS-Processes]] for absent AI processes and OS package inventory for `lsof`.

Resolution: [[Resolution-install-lsof-restart-ai]]

**Components:** [[Component-aisrv-web-Jett-AI]]
