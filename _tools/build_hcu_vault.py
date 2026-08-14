#!/usr/bin/env python3
"""
build_hcu_vault.py — Generate an Obsidian knowledge-graph vault documenting the
Control-M Health Check Utility (ctm_data_collector) archive format.

Deterministic skeleton builder:
  - Enumerates archive sections from the extracted tree (file inventories included)
  - Enumerates check_config checks/parameters from the latest JSON report
  - Emits component, artifact, and template notes with wikilinks
  - Strips customer-identifying hostnames/domains

Usage:
    python3 build_hcu_vault.py <extracted_hcu_root> <output_vault_dir>

Re-runnable against future HCU archives (EM or Server). Enrichment (findings,
root causes, resolutions) is done afterwards, note by note, on top of this skeleton.
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------- sanitization

HOSTNAME_RE = re.compile(r"[A-Za-z][\w-]*\.[\w.-]+\.(?:local|com|net|org|corp|internal)")
SIMPLE_HOST_RE = re.compile(r"\blrdcc[\w.]*\b", re.IGNORECASE)  # sample-specific
PID_TS_RE = re.compile(r"\d{6,}")


def sanitize(text: str) -> str:
    text = HOSTNAME_RE.sub("<hostname>", text)
    text = SIMPLE_HOST_RE.sub("<hostname>", text)
    return text


def normalize_filename(name: str) -> str:
    """Collapse rotation numbers / timestamps / pids so log families dedupe."""
    n = sanitize(name)
    n = re.sub(r"\d{4}[-_]\d{2}[-_]\d{2}[^./]*", "<ts>", n)
    n = PID_TS_RE.sub("<n>", n)
    n = re.sub(r"(\.|-|_)\d+(\.log|\.txt|\.std|\.err|$)", r"\1<n>\2", n)
    n = re.sub(r"\.log\.\d+$", ".log.<n>", n)
    n = re.sub(r"#\d+", "#<n>", n)
    return n


# ---------------------------------------------------------------- note writing

def fm(**kw) -> str:
    lines = ["---"]
    for k, v in kw.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            lines.extend(f"  - {x}" for x in v)
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


class Vault:
    def __init__(self, root: Path):
        self.root = root
        self.notes = {}  # name -> (folder, content)

    def add(self, folder: str, name: str, content: str):
        self.notes[name] = (folder, content)

    def write(self):
        for name, (folder, content) in self.notes.items():
            d = self.root / folder
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{name}.md").write_text(content, encoding="utf-8")

    def link_report(self):
        """Return (defined, linked) to detect orphans."""
        defined = set(self.notes)
        linked = set()
        for _, (_, content) in self.notes.items():
            linked |= set(re.findall(r"\[\[([^\]|#]+)", content))
        return defined, linked


# ---------------------------------------------------------------- curated model

SECTION_INFO = {
    "": ("HCU-Archive-Root",
         "Top level of a `ctm_data_collector` archive. The folder name encodes run "
         "timestamp, OS, hostname, and the account that ran the collector: "
         "`ctm_data_collector_<YYYYMMDD>_<HHMMSS>_<OS>_<hostname>_<user>`."),
    "EM": ("EM",
           "Everything collected from the Control-M/Enterprise Manager installation: "
           "health checks, configuration files, database table dumps, table statistics, "
           "microservice configs, and component logs."),
    "EM/check_config_results": ("EM-check_config_results",
        "Output of the **check_config** health check utility (`em_check_config.sh -st all`). "
        "This is the closest thing in the archive to a formal pass/fail health report. "
        "Contains `check_config.txt` (invocation summary: checks performed / failed) plus one "
        "CSV + JSON report per historical run. Parse the **latest JSON** first — it is the "
        "structured source of truth for check results. See [[Artifact-check_config_report-json]]."),
    "EM/AAPI": ("EM-AAPI",
        "Application Integrator / Automation API plugin deployments. One folder per deployed "
        "AI job type, one subfolder per version (`v0`, `v1`, ...), each holding the plugin XML, "
        "zip, protobuf definitions, and descriptor dictionary JSON. Useful for verifying which "
        "AI job type versions are deployed when diagnosing AI job issues."),
    "EM/Services": ("EM-Services",
        "EM microservices layer configuration: per-service `log4j2.*` logging configs, "
        "`*-application.yml` service configs, `services_template.yml`, desired-state and "
        "init templates, JAAS configs, and — critically — `config/custom/` user overrides "
        "(e.g. `BootPropertiesUserOverride.yml`) which win over shipped defaults and are "
        "referenced by several [[Check-controlm-web-context|context checks]]."),
    "EM/ini": ("EM-ini",
        "Classic EM configuration: [[Artifact-EMSiteConfig-ini|EMSiteConfig.ini]] (JVM heap "
        "settings per component — checked by [[Check-site_config]]), `mcs.ini`, `config.ini`, "
        "`version.ini`, `CONFREG.INI`, per-component `*_DiagLvls.ini` diagnostic levels, and "
        "subfolders for SSL, FIPS keys, SAML, and local overrides."),
    "EM/DBT": ("EM-DBT",
        "Dumps of EM database tables as CSV/TXT: `PARAMS` (system parameters — input to "
        "[[Check-system_parameters]]), `confreg`/`commreg` registries, GCS tables, active "
        "users, LDAP groups, Reporting Facility user reports, add-ons, AI repository, and "
        "more. When a check references `DB: PARAMS`, this is where the raw data lives."),
    "EM/TBL": ("EM-TBL",
        "Table-level statistics: `*-size.csv` row/size counts per EM table (growth outliers "
        "surface here), `primary_db_performance.csv`, `java_memory.csv` (per-process JVM "
        "memory), `check_schema.txt`, and `compare.txt`."),
    "EM/EMWEB": ("EM-EMWEB",
        "EM web server (Tomcat) configuration: `server.xml`, `web.xml`, `tomcat_config.xml` "
        "(checked by [[Check-tomcat_config]] and [[Check-tomcat_server]]), keystores, HA "
        "variants, and timestamped backups of previous configs (useful for spotting what "
        "changed and when)."),
    "EM/KAFKA": ("EM-KAFKA",
        "Embedded Kafka/ZooKeeper (messaging backbone for EM services): broker and "
        "controller configs, JAAS configs, and `Log/` with server logs, GC logs, state-change "
        "and log-cleaner logs. First stop for Workflow Insights / service messaging issues."),
    "EM/Log": ("EM-Log",
        "All EM component logs. Largest section of the archive by far (individual service "
        "logs reach 100 MB). Families include GTW/GSR/GCS logs and diag snapshots, "
        "`Services/` microservice logs with paired `*_exceptions` logs and `jvm-*` GC logs, "
        "Tomcat catalina/access logs, REST server logs, SSL logs, and wrapper output. "
        "See the per-family inventory below and [[Diagnostic-Playbooks-MOC]] for routing."),
    "EM/LDAP": ("EM-LDAP", "LDAP integration config: `ldap.conf`, directory service type, SSL keystore PEM."),
    "EM/SSO": ("EM-SSO", "Single sign-on configuration (empty in this sample — presence varies by environment)."),
    "EM/WI": ("EM-WI", "Workflow Insights artifacts (empty in this sample — populated when WI is deployed)."),
    "EM/Mail": ("EM-Mail", "SMTP configuration variants: `mail.properties` plus defaults and TLS/no-auth templates."),
    "EM/Rsc": ("EM-Rsc",
        "`Defaults.rsc` — component resource defaults, including Gateway `dwl_batch_size` "
        "checked by [[Check-defaults_rsc]]."),
    "EM/SCH": ("EM-SCH", "Scheduling service metric tables: `metric`, `metric_conf`, `net_report`, `net_report_data`."),
    "EM/ReportingFacility": ("EM-ReportingFacility",
        "Reporting Facility server config (`RF-Server.xml`, `reporting.properties`, template "
        "metadata, config log). Memory sizing checked by [[Check-reporting-facility-context]]."),
    "EM/Client_Update": ("EM-Client_Update",
        "Client deployment/update configuration: repository and target XML, Java properties, "
        "web server params, and the installed client update package list."),
    "OS": ("OS",
        "Operating system diagnostics for the EM host: swap, filesystem, block devices, "
        "uptime, plus the subsections below. Interpret EM symptoms against this baseline — "
        "many 'EM problems' are host problems."),
    "OS/Performance": ("OS-Performance",
        "Host performance: `iostat`, `vmstat`, `nfsstat`, `uptime`, and `SAR/` binary + text "
        "sar files covering multiple days — the primary source for retrospective CPU/IO/memory "
        "pressure correlation with EM incidents."),
    "OS/Network": ("OS-Network",
        "Network state: hostname/DNS resolution (`Nslookup*`), interface and routing config, "
        "`Netstat`/`ss` socket state (including deep and timer variants), ping self-test, and "
        "`etc/` network config files. First stop for connectivity-class symptoms."),
    "OS/Processes": ("OS-Processes", "Process listings and limits at collection time."),
    "OS/Java": ("OS-Java", "Java version inventory: system Java vs EM's JAVA_HOME (`check_java_versions.txt`)."),
    "OS/Memory": ("OS-Memory", "Memory state (`free`, meminfo-style captures)."),
    "OS/Hardware": ("OS-Hardware", "CPU/hardware inventory."),
    "OS/Disk": ("OS-Disk", "Disk capacity and mounts."),
    "OS/StartUp": ("OS-StartUp", "Boot/init configuration (`rc/StartUp.txt`)."),
    "db": ("db",
        "Database diagnostics: PostgreSQL catalog/stat dumps, DBUtils outputs, and DBU data "
        "logs. Note: on external/remote DB deployments (like this sample) the local `pgsql/data` "
        "folders don't exist and the collector logs 'Source folder does not exist' — expected, "
        "not an error. See [[hcu_logs]]."),
    "db/postgresql": ("db-postgresql",
        "PostgreSQL state: `pg_settings` (server config), `pg_stat_activity` (sessions at "
        "collection time), `pg_locks`, `pg_stat_all_Tables`/`indexes` (bloat/vacuum/scan "
        "stats), `pg_class`, `pg_database`, tablespaces, users, `pg_service.conf`, data/home "
        "size captures, and `pg_log/`."),
    "db/DBUtils": ("db-DBUtils",
        "Control-M database utility outputs: `DBUCheck` (integrity check), `DBUStatus`, "
        "`DBUShow`, `DBUVersion`, `DBUTransactions`."),
    "db/DBUData": ("db-DBUData", "DBU working data and check logs."),
    "Install": ("Install",
        "Installation and upgrade logs (`Install/Log`, `Install/DBUData_Log`). Cross-reference "
        "when a symptom began at or after an install/upgrade window."),
    "report": ("report",
        "**HCU-generated analyses** — the collector doesn't just copy files, it runs "
        "diagnostics: component metric extracts as CSV ([[Artifact-metric-csvs|GSR/GTW/"
        "Environment/db_performance by type and by date]]), the "
        "[[Artifact-db-perf-sort-report|database performance benchmark]], "
        "[[Artifact-disk-benchmark|disk benchmark]], observability client output, and the "
        "[[report-observability|metrics validation report]]."),
    "report/observability": ("report-observability",
        "Metrics Validator CLI output (`metrics_validation_EM_*.{txt,json,html}`): connects to "
        "the EM DB, enumerates configured metrics, and validates custom observability metrics "
        "against thresholds. Warnings about custom metrics with 'no rows for current EM SQL "
        "filters' usually indicate hostname-parameter mismatches in custom metric SQL."),
    "hcu_logs": ("hcu_logs",
        "The collector's own execution log plus working data. Read this to judge archive "
        "**completeness**: 'Permission denied' and 'Source folder does not exist' entries "
        "explain why sections are missing or empty (e.g. remote DB → no local pgsql data; "
        "no OpenSearch → no observability store folders). A missing section is only "
        "meaningful if the collector actually tried and failed to collect it."),
    "Thrift": ("Thrift",
        "Inter-component communication configuration: `communication.xml` (checked by "
        "[[Check-communication]] for GSR/CMS worker counts) and its DTD."),
}

COMPONENTS = {
    "Component-GUI-Server-GSR": (
        "GUI Server (GSR)",
        "Serves EM client/GUI sessions. Worker pool sized by `GSR NumWorkers` in "
        "`communication.xml` ([[Check-communication]]); heap sized by `HeapGSR` in "
        "EMSiteConfig.ini ([[Check-site_config]]).",
        ["EM-Log", "Thrift", "EM-ini"],
        "Logs: `gsr_diag.*` snapshots in [[EM-Log]]; metrics in [[Artifact-metric-csvs|GSR_by_type/date.csv]]."),
    "Component-Gateway-GTW": (
        "Gateway (GTW)",
        "Per-datacenter gateway between EM and Control-M/Server. Download batch size from "
        "`dwl_batch_size` in Defaults.rsc ([[Check-defaults_rsc]]); update threads from "
        "`GtwNumUpdateThreads` system parameter ([[Check-system_parameters]]); heap from "
        "`HeapGTW` ([[Check-site_config]]).",
        ["EM-Log", "EM-Rsc", "EM-DBT"],
        "Logs: `gtw_log.<DC>.*` and `gtw_diag.*` in [[EM-Log]]; metrics in GTW_by_type/date.csv; "
        "db latency via [[Artifact-db-perf-sort-report]] (run through GTW)."),
    "Component-Configuration-Server-CMS": (
        "Configuration Server (CMS)",
        "Configuration management service. Worker pool sized by `CMS NumWorkers` in "
        "`communication.xml` ([[Check-communication]]); heap via `HeapCMS` ([[Check-site_config]]).",
        ["Thrift", "EM-ini"], ""),
    "Component-GCS": (
        "Global Conditions Server (GCS)",
        "Distributes global conditions across datacenters.",
        ["EM-Log", "EM-DBT"],
        "Logs: `GCS_LOG.*` and `gcs_diag_*` in [[EM-Log]]; `gcs_*` tables in [[EM-DBT]]."),
    "Component-controlm-web": (
        "controlm-web",
        "Main web application service. Min/max memory from its context yml, subject to "
        "`BootPropertiesUserOverride.yml` ([[Check-controlm-web-context]]).",
        ["EM-Services", "EM-Log"],
        "Logs: `controlm-web*.log` + exceptions + `jvm-controlm-web*` GC logs in [[EM-Log]]."),
    "Component-em-scheduling-service": (
        "em-scheduling-service", "Scheduling microservice.",
        ["EM-Services", "EM-Log", "EM-SCH"], ""),
    "Component-em-ctm-request-service": (
        "em-ctm-request-service",
        "Handles EM→CTM request traffic; among the largest log producers in the archive.",
        ["EM-Services", "EM-Log"], ""),
    "Component-em-mft-updates-service": (
        "em-mft-updates-service", "MFT update processing microservice; heavy log producer.",
        ["EM-Services", "EM-Log"], ""),
    "Component-aisrv-web-Jett-AI": (
        "aisrv-web (Jett AI)",
        "AI service web component. Startup depends on host prerequisites (e.g. `lsof` present); "
        "startup failures can masquerade as network errors toward the Primary EM web server.",
        ["EM-Services", "EM-Log"],
        "Logs: `aisrv-web*.log`, `aisrv-web_exceptions*.log`, `AiSrcServiceStart*.log` in [[EM-Log]]. "
        "See [[Finding-aisrv-web-connection-refused]] for a known misleading-symptom chain."),
    "Component-authorization-service": (
        "authorization-service", "AuthN/AuthZ microservice.", ["EM-Services", "EM-Log"], ""),
    "Component-Kafka-ZooKeeper": (
        "Kafka / ZooKeeper",
        "Embedded messaging backbone for EM microservices.",
        ["EM-KAFKA", "EM-Log"],
        "Health/start/stop logs in [[EM-Log]] `Services/apache_kafka_*`, `apache_zookeeper_*`; "
        "broker/GC logs in [[EM-KAFKA]]."),
    "Component-Tomcat-EMWEB": (
        "Tomcat (EMWEB)",
        "EM web container. `max_memory` via tomcat_config.xml ([[Check-tomcat_config]]); "
        "`Connector maxThreads` via server.xml ([[Check-tomcat_server]]).",
        ["EM-EMWEB", "EM-Log"],
        "Logs: `tomcat/catalina*.log`, `tomcat/access_log*.log` in [[EM-Log]]."),
    "Component-Reporting-Facility": (
        "Reporting Facility",
        "Report generation service; memory sizing per [[Check-reporting-facility-context]].",
        ["EM-ReportingFacility", "EM-Services", "EM-Log"], ""),
    "Component-Automation-API": (
        "Automation API (AAPI/CAPI)",
        "REST automation layer. JVM sizing via `aapi.xmx.size`/`capi.xmx.size` "
        "([[Check-automation_api_properties]]); deployed AI plugins under [[EM-AAPI]].",
        ["EM-AAPI", "EM-Log"],
        "Logs: `emrestsrv*`, `emconfigrestsrv*` in [[EM-Log]]."),
    "Component-PostgreSQL": (
        "PostgreSQL (EM database)",
        "EM database server (local or remote; remote in this sample). Performance measured by "
        "[[Artifact-db-perf-sort-report]]; state in [[db-postgresql]]; integrity via "
        "[[db-DBUtils|DBUCheck]].",
        ["db-postgresql", "db-DBUtils"], ""),
}

ARTIFACTS = {
    "Artifact-check_config_report-json": (
        "check_config_report JSON",
        "EM/check_config_results/check_config_report_<ts>.json",
        "Structured health check results. Top level: `product`, `location` (EM_HOME), "
        "`version`, `production_size` {jobs, executions, users, size} — thresholds scale with "
        "`size` (Small/Medium/Large). `results[]`: one entry per check with `check_name`, "
        "`status` (bool), `passed_check[]`/`failed_check[]` param entries "
        "{parameter_name, value_detected, minimum_expected, optional actual_parameter_name "
        "(XPath-ish source), optional message, components[]}, plus optional `location` and "
        "`user_override_file`.\n\n**Agent rule:** always parse the *latest* JSON; the CSV is a "
        "flattened view of the same data. `production_size` must be read first — it is the "
        "context for every minimum.",
        "EM-check_config_results"),
    "Artifact-check_config-txt": (
        "check_config.txt",
        "EM/check_config_results/check_config.txt",
        "Invocation summary of the health check run: command line, profile, checks performed, "
        "failed count, and the path of the report file it produced.",
        "EM-check_config_results"),
    "Artifact-EMSiteConfig-ini": (
        "EMSiteConfig.ini",
        "EM/ini/EMSiteConfig.ini",
        "Site-wide EM configuration including `jvm_properties`: HeapGSR/HeapGTW/HeapCMS/"
        "HeapUTIL, AutoIncHeapTimes, AutoIncHeapSize — all validated by [[Check-site_config]].",
        "EM-ini"),
    "Artifact-Defaults-rsc": (
        "Defaults.rsc",
        "EM/Rsc/Defaults.rsc",
        "Component resource defaults; source of Gateway `dwl_batch_size` "
        "([[Check-defaults_rsc]]).",
        "EM-Rsc"),
    "Artifact-communication-xml": (
        "communication.xml",
        "Thrift/communication.xml (live: <EM_HOME>/etc/domains/communication.xml)",
        "Per-scope communication settings; source of `GSR NumWorkers` and `CMS NumWorkers` "
        "([[Check-communication]]).",
        "Thrift"),
    "Artifact-metric-csvs": (
        "Component metric CSVs (report/)",
        "report/{GSR,GTW,Environment,db_performance}_by_{type,date}.csv",
        "Time-series metric extracts per component. Columns (GSR/GTW): "
        "`name, comp_name, hostname, value, metric_time, pid` — e.g. GSR 'Pending Updates' "
        "per connected component over time. `_by_type` groups by metric name; `_by_date` is "
        "chronological. Sustained growth in queue/pending metrics is a primary early-warning "
        "signal.",
        "report"),
    "Artifact-db-perf-sort-report": (
        "db-perf-sort-report.txt",
        "report/db-perf-sort-report.txt",
        "Output of `em gtw -db_perf`: a fixed battery of DB operation tests (insert/update "
        "iterations, bulk inserts, etc.) with elapsed and AVG per operation, plus DB major "
        "release. The AVG values are the comparable numbers across environments and over time; "
        "elevated averages indicate DB-side latency affecting all EM DB writers.",
        "report"),
    "Artifact-disk-benchmark": (
        "disk-benchmark.txt",
        "report/disk-benchmark.txt",
        "Collector-run disk throughput benchmark for the EM host filesystem.",
        "report"),
    "Artifact-metrics-validation": (
        "metrics_validation_EM report",
        "report/observability/metrics_validation_EM_<ts>.{txt,json,html}",
        "Metrics Validator CLI: connects to the EM DB, lists configured metrics, validates "
        "custom observability metrics against a difference threshold. 'No rows for current EM "
        "SQL filters' warnings usually mean hostname-parameter mismatch in custom metric SQL.",
        "report-observability"),
    "Artifact-java_memory-csv": (
        "java_memory.csv",
        "EM/TBL/java_memory.csv",
        "Per-JVM-process memory snapshot — cross-check against heap settings from "
        "[[Check-site_config]] and service context checks.",
        "EM-TBL"),
    "Artifact-table-size-csvs": (
        "Table size CSVs",
        "EM/TBL/*-size.csv",
        "Row/size stats per EM table. Outlier growth (gcs_msgs, audit_*, download, "
        "exception_alerts, global_cond, ...) points at retention/cleanup issues that degrade "
        "DB performance.",
        "EM-TBL"),
    "Artifact-pg_stat_activity": (
        "pg_stat_activity dump",
        "db/postgresql/pg_stat_activity-table.csv",
        "Active DB sessions at collection time: states, wait events, long-running queries. "
        "Pair with pg_locks for blocking analysis.",
        "db-postgresql"),
    "Artifact-pg_settings": (
        "pg_settings dump",
        "db/postgresql/pg_settings-table.csv",
        "Full PostgreSQL server configuration as-running — the reference for tuning reviews.",
        "db-postgresql"),
    "Artifact-DBUCheck": (
        "DBUCheck output",
        "db/DBUtils/DBUCheck.txt",
        "Control-M database integrity check output.",
        "db-DBUtils"),
    "Artifact-hcu-collector-log": (
        "Collector execution log",
        "hcu_logs/ctm_data_collector_<run-id>.log",
        "Timestamped record of every collection step: parameters resolved, files copied, and "
        "— importantly — what could NOT be collected and why (permissions, non-existent "
        "sources). The completeness gate for the whole archive.",
        "hcu_logs"),
}

SEED_CHAIN = {
    "Finding-aisrv-web-connection-refused": (
        "Finding — aisrv-web TTransportException / Connection refused",
        "finding",
        "`aisrv-web.log` shows `TTransportException` / `Connection refused` toward the "
        "Primary EM Web Server (TCP 18080) while network diagnostics (curl, DNS, routing) "
        "from the same host all pass.\n\n**Where in the HCU archive:** "
        "`EM/Log/Services/aisrv-web*.log`, `aisrv-web_exceptions*.log`, "
        "`AiSrcServiceStart*.log`; correlate with [[OS-Network]] captures.\n\n"
        "**Interpretation:** TCP 18080 is the EM Web Server port, not a dedicated AI port — "
        "the exception naming that endpoint does not by itself indicate a network fault. If "
        "no local AI process is running/listening, treat as failed local startup, not "
        "connectivity.\n\nRoot cause: [[RootCause-missing-lsof-prerequisite]]",
        ["Component-aisrv-web-Jett-AI"]),
    "RootCause-missing-lsof-prerequisite": (
        "Root cause — `lsof` missing on minimal RHEL-family host",
        "root-cause",
        "A Jett AI Python startup script shells out to `lsof`, which is absent on "
        "base/minimal RHEL-family installs (RHEL/AlmaLinux/Rocky/Oracle). The startup script "
        "fails silently before AI services initialize; the only visible error is the "
        "misleading outbound connect failure described in "
        "[[Finding-aisrv-web-connection-refused]].\n\n**HCU verification:** check "
        "[[OS-Processes]] for absent AI processes and OS package inventory for `lsof`.\n\n"
        "Resolution: [[Resolution-install-lsof-restart-ai]]",
        ["Component-aisrv-web-Jett-AI"]),
    "Resolution-install-lsof-restart-ai": (
        "Resolution — install lsof and restart AI services",
        "resolution",
        "Install the `lsof` package (`dnf install -y lsof` on RHEL-family 8+), verify with "
        "`lsof -v`, restart Control-M AI services, and confirm the exceptions no longer "
        "appear in `aisrv-web.log` and the AI Service registers with the Primary EM.\n\n"
        "Applies to: [[RootCause-missing-lsof-prerequisite]]",
        ["Component-aisrv-web-Jett-AI"]),
}

TEMPLATES = {
    "tpl-check": ("check", """# Check — <name>

**Section:** [[EM-check_config_results]] · **Config source:** `<path>` · **Components:** <links>

## What it validates
## Parameters
| Parameter | Minimum (by size) | Source |
|---|---|---|
## When it fails
Symptoms → [[Finding-...]]
## Notes
"""),
    "tpl-finding": ("finding", """# Finding — <symptom>

**Seen in:** `<archive path(s)>` · **Components:** <links>

## Signature
Exact strings / patterns to search for.
## Where in the HCU archive
## Interpretation
## Root causes
- [[RootCause-...]]
"""),
    "tpl-root-cause": ("root-cause", """# Root cause — <name>

## Mechanism
## How to verify from the HCU archive
## Findings that point here
- [[Finding-...]]
## Resolutions
- [[Resolution-...]]
"""),
    "tpl-resolution": ("resolution", """# Resolution — <name>

## Steps
## Verification
## KA references
## Root causes addressed
- [[RootCause-...]]
"""),
}


# ---------------------------------------------------------------- builders

def build_section_notes(v: Vault, src: Path):
    for rel, (note_name, desc) in SECTION_INFO.items():
        p = src / rel if rel else src
        inventory = []
        if p.is_dir():
            seen = set()
            for f in sorted(p.rglob("*")):
                if f.is_file():
                    n = normalize_filename(str(f.relative_to(p)))
                    if n not in seen:
                        seen.add(n)
                        inventory.append(n)
        # log families for EM/Log come from filelist since bodies were excluded
        parent = "[[HCU-MOC]]" if rel == "" else f"[[{SECTION_INFO.get(str(Path(rel).parent) if str(Path(rel).parent) != '.' else '', SECTION_INFO[''])[0]}]]"
        related_checks = [f"[[{c}]]" for c in CHECK_NOTE_NAMES] if rel == "EM/check_config_results" else []
        body = fm(type="archive-section", section=(rel or "/"), status="skeleton",
                  tags=["hcu", "section"]) 
        body += f"# {note_name}\n\n{desc}\n\n**Parent:** {parent}\n"
        if related_checks:
            body += "\n**Checks:** " + " · ".join(related_checks) + "\n"
        if inventory:
            shown = inventory[:60]
            body += "\n## File inventory (normalized)\n\n"
            body += "\n".join(f"- `{n}`" for n in shown)
            if len(inventory) > len(shown):
                body += f"\n- … {len(inventory) - len(shown)} more"
            body += "\n"
        v.add("10-Archive-Sections", note_name, body)


CHECK_NOTE_NAMES = []

def build_check_notes(v: Vault, report: dict):
    size = report.get("production_size", {})
    ctx = (f"Sample environment: version {report.get('version')}, production size "
           f"**{size.get('size')}** ({size.get('jobs'):,} jobs / "
           f"{size.get('executions'):,} executions / {size.get('users')} users). "
           f"Minimums below are the thresholds check_config applied at this size — "
           f"they scale with production size.")
    comp_map = {
        "GUI Server": "Component-GUI-Server-GSR", "Gateway": "Component-Gateway-GTW",
        "Configuration Server": "Component-Configuration-Server-CMS",
        "controlm-web": "Component-controlm-web",
        "reporting-facility": "Component-Reporting-Facility",
    }
    for r in report["results"]:
        name = r["check_name"]
        note = f"Check-{name}"
        CHECK_NOTE_NAMES.append(note)
        comps = set()
        rows = []
        for kind in ("passed_check", "failed_check"):
            for p in r.get(kind, []):
                for c in p.get("components", []):
                    comps.add(comp_map.get(c, None) or c)
                src = sanitize(p.get("actual_parameter_name", "") or "")
                msg = sanitize(p.get("message", "") or "")
                rows.append((p["parameter_name"], p.get("minimum_expected", ""),
                             p.get("value_detected", ""), src, msg))
        loc = sanitize(str(r.get("location", "")))
        override = sanitize(str(r.get("user_override_file", "")))
        comp_links = " · ".join(f"[[{c}]]" if c.startswith("Component-") else c for c in sorted(comps)) or "—"
        body = fm(type="check", check_name=name, product=report.get("product", "EM"),
                  status="skeleton", tags=["hcu", "check"])
        body += f"# Check — {name}\n\n"
        body += f"**Section:** [[EM-check_config_results]] · **Report:** [[Artifact-check_config_report-json]]\n\n"
        if loc:
            body += f"**Config source:** `{loc}`\n\n"
        if override:
            body += f"**User override file:** `{override}` (overrides win over shipped defaults)\n\n"
        body += f"**Components:** {comp_links}\n\n"
        body += f"> {ctx}\n\n"
        body += "## Parameters\n\n| Parameter | Minimum expected | Example detected | Source path | Note |\n|---|---|---|---|---|\n"
        for pn, mn, vd, src, msg in rows:
            body += f"| `{pn}` | {mn} | {vd} | `{src}` | {msg} |\n"
        body += ("\n## What it validates\n\n_(enrichment pending)_\n\n"
                 "## When it fails\n\n_(enrichment pending — link findings here)_\n")
        v.add("20-Checks", note, body)


def build_component_notes(v: Vault):
    for note, (title, desc, sections, extra) in COMPONENTS.items():
        body = fm(type="component", status="skeleton", tags=["hcu", "component"])
        body += f"# {title}\n\n{desc}\n\n"
        body += "**Archive sections:** " + " · ".join(f"[[{s}]]" for s in sections) + "\n"
        if extra:
            body += f"\n{extra}\n"
        body += "\n## Known findings\n\n_(enrichment pending)_\n"
        v.add("30-Components", note, body)


def build_artifact_notes(v: Vault):
    for note, (title, path, desc, section) in ARTIFACTS.items():
        body = fm(type="artifact", status="skeleton", tags=["hcu", "artifact"])
        body += f"# {title}\n\n**Archive path:** `{sanitize(path)}` · **Section:** [[{section}]]\n\n{desc}\n"
        v.add("25-Artifacts", note, body)


def build_seed_chain(v: Vault):
    folders = {"finding": "40-Findings", "root-cause": "50-Root-Causes",
               "resolution": "60-Resolutions"}
    for note, (title, kind, body_text, comps) in SEED_CHAIN.items():
        body = fm(type=kind, status="seeded", tags=["hcu", kind])
        body += f"# {title}\n\n{body_text}\n\n"
        body += "**Components:** " + " · ".join(f"[[{c}]]" for c in comps) + "\n"
        v.add(folders[kind], note, body)


def build_templates(v: Vault):
    for name, (kind, text) in TEMPLATES.items():
        v.add("90-Templates", name, fm(type="template", template_for=kind) + text)


def build_index(v: Vault, report: dict):
    checks = "\n".join(f"- [[{c}]]" for c in CHECK_NOTE_NAMES)
    sections = "\n".join(f"- [[{n}]]" for _, (n, _) in sorted(SECTION_INFO.items()) if n != "HCU-Archive-Root")
    comps = "\n".join(f"- [[{c}]]" for c in COMPONENTS)
    arts = "\n".join(f"- [[{a}]]" for a in ARTIFACTS)
    moc = fm(type="moc", status="skeleton", tags=["hcu", "moc"])
    moc += f"""# HCU Knowledge Graph — Map of Content

Source of truth for interpreting **Control-M Health Check Utility (`ctm_data_collector`)**
archives. Built from an EM {report.get('version')} sample; extend with Server-side samples.

**Agent entry protocol:**
1. Read [[About-This-Vault]] for schema and retrieval rules.
2. Orient in the archive via [[HCU-Archive-Root]] and the section notes.
3. For pass/fail state, parse the latest [[Artifact-check_config_report-json]] — read
   `production_size` first, then `results[]`, and map each check to its note below.
4. Judge archive completeness via [[Artifact-hcu-collector-log]] before concluding
   anything from a *missing* file.
5. Route symptoms via [[Diagnostic-Playbooks-MOC]].

## Health checks (check_config)
{checks}

## Archive sections
- [[HCU-Archive-Root]]
{sections}

## Components
{comps}

## Key artifacts
{arts}

## Diagnostic chains
- [[Finding-aisrv-web-connection-refused]] → [[RootCause-missing-lsof-prerequisite]] → [[Resolution-install-lsof-restart-ai]]
- _(enrichment pending — add chains as cases are worked)_
"""
    v.add("00-Index", "HCU-MOC", moc)

    playbooks = fm(type="moc", status="skeleton", tags=["hcu", "moc"])
    playbooks += """# Diagnostic Playbooks — MOC

Symptom-class routing into the archive. Each row will grow into a playbook note during
enrichment.

| Symptom class | Start here | Then |
|---|---|---|
| EM slow / general sluggishness | [[Artifact-db-perf-sort-report]], [[OS-Performance]] | [[Artifact-metric-csvs]], [[Artifact-java_memory-csv]] |
| Check failures reported | [[Artifact-check_config_report-json]] | The matching `Check-*` note |
| Component down / won't start | [[EM-Log]] (service + `_exceptions` + `jvm-*` logs) | [[Artifact-hcu-collector-log]], [[OS-Processes]] |
| Connectivity errors | [[OS-Network]] | [[Thrift]], component log family |
| DB growth / bloat | [[Artifact-table-size-csvs]] | [[db-postgresql]], [[Artifact-pg_stat_activity]] |
| Memory / OOM | [[Artifact-java_memory-csv]], [[Check-site_config]] | Service context checks, `jvm-*` GC logs in [[EM-Log]] |
| Kafka / messaging issues | [[EM-KAFKA]] | `apache_kafka_*` health logs in [[EM-Log]] |
| AI / Jett issues | [[Component-aisrv-web-Jett-AI]] | [[Finding-aisrv-web-connection-refused]] |
| Upgrade-adjacent symptoms | [[Install]] | Timestamped backups in [[EM-EMWEB]] |
"""
    v.add("00-Index", "Diagnostic-Playbooks-MOC", playbooks)

    about = fm(type="meta", status="skeleton", tags=["hcu", "meta"])
    about += """# About This Vault

## Purpose
Source of truth for AI agents (and humans) interpreting Control-M HCU
(`ctm_data_collector`) archives during diagnosis.

## Note types (frontmatter `type`)
| type | folder | one note per |
|---|---|---|
| `archive-section` | 10-Archive-Sections | directory in the HCU archive |
| `check` | 20-Checks | check_config health check |
| `artifact` | 25-Artifacts | key file/report format |
| `component` | 30-Components | EM/Control-M component |
| `finding` | 40-Findings | observable abnormal pattern |
| `root-cause` | 50-Root-Causes | underlying mechanism |
| `resolution` | 60-Resolutions | fix procedure |

## Conventions
- Wikilinks are the graph. Findings link → root causes link → resolutions; checks and
  artifacts link to components and sections.
- `status: skeleton` = structure generated deterministically from a real archive,
  enrichment pending. `status: seeded` / `status: enriched` after review.
- All customer identifiers are sanitized (`<hostname>`, `<n>`, `<ts>`).
- Thresholds in check notes are **size-dependent** — never quote a minimum without the
  `production_size` context.

## Retrieval rules for agents
1. Prefer structured sources (check_config JSON, metric CSVs) over prose logs.
2. Before reasoning about a missing file, verify collection succeeded in
   [[Artifact-hcu-collector-log]].
3. Match symptoms against `Finding-*` signatures first; only free-form log analysis when
   no finding matches — and propose a new Finding note when done.
"""
    v.add("00-Index", "About-This-Vault", about)


def main():
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    reports = sorted((src / "EM/check_config_results").glob("check_config_report_*.json"))
    report = json.loads(reports[-1].read_text())
    v = Vault(out)
    build_check_notes(v, report)          # populates CHECK_NOTE_NAMES first
    build_section_notes(v, src)
    build_component_notes(v)
    build_artifact_notes(v)
    build_seed_chain(v)
    build_templates(v)
    build_index(v, report)
    v.write()
    defined, linked = v.link_report()
    dangling = sorted(x for x in linked if x not in defined)
    orphans = sorted(x for x in defined if x not in linked and not x.startswith("tpl-"))
    print(f"Notes written: {len(v.notes)}")
    print(f"Dangling links (targets not yet created): {dangling or 'none'}")
    print(f"Orphan notes (nothing links to them): {orphans or 'none'}")


if __name__ == "__main__":
    main()
