---
type: archive-section
section: AG_CNF
product: Agent
status: skeleton
tags:
  - hcu
  - section
---

# Agent-AG_CNF

Agent configuration: `data/` holds ~60 parameter/state `.dat` files (`CONFIG.dat` — see [[Agent-Artifact-CONFIG-dat]] — plus `ag_ver.dat`, `AG_PREREQ.dat`, `JAVACONF.dat`, application-plugin maps, SSL material, `CFG_BACKUP/`, `remote_utils/`, `rhdetails/`), with `versions/` and `Agent_dependencies.txt` alongside. **Note:** `AG_CNF/data/` is covered by this note (deliberate deviation from one-note-per-directory).

**Parent:** [[Agent-Archive-Root]]

## File inventory (normalized)

- `Agent_dependencies.txt`
- `data/AG_PREREQ.dat`
- `data/ag_ver.dat`
- `data/Agent.64-bit.txt`
- `data/AI.dat`
- `data/APPLMAP.dat`
- `data/change_password_mapping.dat`
- `data/CONFIG.dat`
- `data/config.ini`
- `data/CONFUPLD.dat`
- `data/ctm_agent_status.dat`
- `data/daily_report.dat`
- `data/FILE_TRANS.dat`
- `data/GC_LOCALE.dat`
- `data/get_cpu_specs.dat`
- `data/get_cpu_specs_encrypted.dat`
- `data/JAVA_REQ.dat`
- `data/JAVACONF.dat`
- `data/LOCALE.dat`
- `data/MSGTBL.dat`
- `data/MSGTBLNK.dat`
- `data/OS.dat`
- `data/PARAMMAP.dat`
- `data/PASSWRDS.dat`
- `data/readme.txt`
- `data/remote_utils/AG_wrapper.sh`
- `data/remote_utils/CACert.pem`
- `data/remote_utils/ctmag-util-executor.py`
- `data/remote_utils/ctmag-util-executor_2.py`
- `data/remote_utils/ctmag-util-fw.py`
- `data/remote_utils/ctmag-util-fw_2.py`
- `data/remote_utils/FW_wrapper.sh`
- `data/remote_utils/get_matching_file_attributes.py`
- `data/remote_utils/get_matching_file_attributes_2.py`
- `data/remote_utils/python_ver.bat`
- `data/remote_utils/python_ver.sh`
- `data/remote_utils/RemoteUtil.jar`
- `data/remote_utils/RU_fileWatcher.bmcvbs`
- `data/remote_utils/RU_runner.bmcvbs`
- `data/remote_utils/RU_runner.COM`
- `data/remote_utils/RU_runner.sh`
- `data/remote_utils/RU_runner_py.bmcvbs`
- `data/REQUESTS.dat`
- `data/RHCONF.dat`
- `data/rhdetails/<hostname>.txt`
- `data/SAASCONF.dat`
- `data/SSL/cert/ag.plc`
- `data/SSL/cert/agkeystore.plc`
- `data/SSL/cert/ru.plc`
- `data/SSL/cert/ruj.plc`
- `data/SSL/cert/site.plc`
- `data/UDA.dat`
- `data/UDA_BMC.dat`
- `data/version.ini`
- `FileList.txt`
- `SSH_Courier_Status.txt`
- `versions/installed-versions.txt`
