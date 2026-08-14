---
type: archive-section
section: LOG_INFO/proclog
product: Server
status: skeleton
tags:
  - hcu
  - section
---

# Server-LOG_INFO-proclog

Process logs (`proclog`). Families by prefix: `CE.*` (engine, incl. periodic pstack snapshots), `TR*` (tracker), `CS<pid>*`, `CA.*` (Configuration Agent, with per-thread `_CO_`/`_CSE_`/`_CSU_`/`_DBC_`/`_EX_` logs), `RT*`, `WD*`, `U_SQL*`, `CTMIPC*`, plus `agents_availability_*`. **Note:** the rotated `LOG_INFO/proclog.save/` copies are covered by this note too (deliberate deviation from one-note-per-directory).

**Parent:** [[Server-LOG_INFO]]

## File inventory (normalized)

- `agents_availability_<n>.txt`
- `agents_availability_<n>.txt.lck`
- `CA.<n>.log`
- `CA.<n>_CO_<n>.log`
- `CA.<n>_CS_<n>.log`
- `CA.<n>_CSE_<n>.log`
- `CA.<n>_CSU_<n>.log`
- `CA.<n>_DBC_<n>.log`
- `CA.<n>_EX_<n>.log`
- `CA.<n>_EX_<n>.log.<n>`
- `CA.<n>_FS_<n>.log`
- `CA.<n>_MON_SCA_<n>.log`
- `CA.<n>_RQ_<n>.log`
- `CA.<n>_RQ_<n>.log.<n>`
- `CA.<n>_TSW_<n>.log`
- `CE.<n>_<n>.log`
- `CE.<n>_<n>.log.lck`
- `CE.<n>_0_memory.log`
- `CE.<n>_0_memory.log.lck`
- `CE.<n>_1_memory.log`
- `CE.<n>_2_memory.log`
- `CE.<n>_3_memory.log`
- `CE.<n>_4_memory.log`
- `CE.<n>_5_memory.log`
- `CE.<n>_6_memory.log`
- `CE.<n>_7_memory.log`
- `CE.<n>_8_memory.log`
- `CE.<n>_9_memory.log`
- `CE_periodic_pstack_snapshot.<n>_<n>.txt`
- `CE_periodic_pstack_snapshot.<n>_<n>.txt.lck`
- `CS<n>.<n>.log`
- `CS<n>.<n>.log.<n>`
- `CTMIPC<n>.<n>.log`
- `ctms_0_exceptions.log`
- `ctms_0_exceptions.log.lck`
- `dump_tr_memory.txt`
- `filehfSIYS`
- `filelrCPg5`
- `fileNHTrOv`
- `fileNNB4Vl`
- `p_ctmce.stdout.<n>`
- `ps_start_ca.txt`
- `ps_start_ctm.txt`
- `RT.<n>.log`
- `RT.<n>.log.<n>`
- `SU.<n>.log`
- `SYSTEM_LOG`
- `TR.<n>.log`
- `TR.<n>.log.<n>`
- `TR.<n>_CO_<n>.log`
- `TR.<n>_CO_<n>.log.<n>`
- `TR.<n>_TSW_<n>.log`
- `TR.<n>_W_<n>.log`
- `TR.<n>_W_<n>.log.<n>`
- `trace_<n>.txt`
- `trace_<n>.txt.lck`
- `U_CTM_AGSTAT.<n>.log`
- `u_ctmlog<n>.<n>.log`
- `u_ctmlog<n>.<n>.log.<n>`
- `u_ecaprflag.<n>.log`
- … 4 more
