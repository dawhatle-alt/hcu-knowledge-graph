---
type: resolution
status: seeded
tags:
  - hcu
  - resolution
---

# Resolution — install lsof and restart AI services

Install the `lsof` package (`dnf install -y lsof` on RHEL-family 8+), verify with `lsof -v`, restart Control-M AI services, and confirm the exceptions no longer appear in `aisrv-web.log` and the AI Service registers with the Primary EM.

Applies to: [[RootCause-missing-lsof-prerequisite]]

**Components:** [[Component-aisrv-web-Jett-AI]]
