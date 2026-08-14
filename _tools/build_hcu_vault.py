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
    python3 build_hcu_vault.py <extracted_hcu_root> <output_vault_dir> [product]

`product` is one of EM (default), Server, Agent. EM note names keep no prefix
(backward compatible with the original EM-only vault); Server/Agent notes are
prefixed `Server-` / `Agent-`. All notes carry `product:` frontmatter.

Non-EM runs generate ONLY that product's section/check/artifact/component notes
plus a `<Product>-MOC` index note — they never touch templates, the seed chain,
About-This-Vault, the playbooks, or another product's notes. The master
`HCU-MOC` is maintained by hand once the vault is multi-product.

Re-runnable against future HCU archives. Enrichment (findings, root causes,
resolutions) is done afterwards, note by note, on top of this skeleton.
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------- sanitization

HOSTNAME_RE = re.compile(
    r"[A-Za-z][\w-]*\.[\w.-]+\.(?:local|com|net|org|corp|internal|edu|gov|mil|io|co|us|uk|de)")
SIMPLE_HOST_RE = re.compile(r"\blrdcc[\w.]*\b", re.IGNORECASE)  # sample-specific
PID_TS_RE = re.compile(r"\d{6,}")

# Tokens scrubbed in addition to the generic patterns; populated per run from
# the archive folder name (hostname + account fields) by register_archive_tokens().
EXTRA_TOKEN_RES = []

ARCHIVE_NAME_RE = re.compile(
    r"^(?:ctm_data_collector|_data)_\d{8}_\d{6}_[A-Za-z]+_(?P<host>[\w.-]+)_(?P<user>[\w-]+)$")


def register_archive_tokens(archive_dirname: str):
    """Derive customer-identifying tokens (hostname, run account) from the
    archive folder name and add them to the scrub list."""
    m = ARCHIVE_NAME_RE.match(archive_dirname)
    if not m:
        return
    host, user = m.group("host"), m.group("user")
    # hostname (and its short form) -> <hostname>
    EXTRA_TOKEN_RES.append((re.compile(re.escape(host), re.IGNORECASE), "<hostname>"))
    short = host.split(".")[0]
    if short and short != host:
        EXTRA_TOKEN_RES.append((re.compile(re.escape(short), re.IGNORECASE), "<hostname>"))
    if user:
        EXTRA_TOKEN_RES.append((re.compile(re.escape(user), re.IGNORECASE), "<user>"))


def sanitize(text: str) -> str:
    text = HOSTNAME_RE.sub("<hostname>", text)
    text = SIMPLE_HOST_RE.sub("<hostname>", text)
    for rx, repl in EXTRA_TOKEN_RES:
        text = rx.sub(repl, text)
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

# ------------------------------------------------------- product model registry
# Server/Agent curated dicts are filled in after the section-list review.
# Non-EM note names inside these dicts are written ALREADY PREFIXED
# ("Server-LOG_INFO", "Agent-Artifact-ag_diag_comm", ...) — the `prefix` entry
# is applied only to generated names (Check-* notes and the <Product>-MOC).

SERVER_SECTION_INFO = {
    "": ("Server-Archive-Root",
         "Top level of a Control-M/Server `ctm_data_collector` archive: "
         "`ctm_data_collector_<YYYYMMDD>_<HHMMSS>_<OS>_<hostname>_<user>`. "
         "Sample baseline: Server 9.0.21.300 on Linux, **Oracle**-backed. This sample "
         "contains **no check_config results** — pass/fail health checks are not "
         "available for Server until a sample that ran them is added."),
    "CNF_INFO": ("Server-CNF_INFO",
        "Core Control-M/Server configuration captures: `data/*.dat` snapshots "
        "(`config.dat`, `local_config.dat`, `parammap.dat`, `env_details.dat`, "
        "`OAP.dat`, `SAP.dat`, `TimeZone.dat`, `rt_ip_address.dat`, `shAdress.dat`, "
        "`ajf_show_net.dat`, `DBUMonitor.dat`, ...) plus `FileList*.txt` inventories."),
    "CNF_INFO/SSL": ("Server-CNF_INFO-SSL",
        "SSL policy/certificate captures (`cert/*.plc`) for server↔agent and related "
        "channels."),
    "CNF_INFO/REMEDY": ("Server-CNF_INFO-REMEDY",
        "Remedy integration configuration (`RemedyConf.xml`, configure script, schema)."),
    "CNF_INFO/versions": ("Server-CNF_INFO-versions",
        "`installed-versions.txt` — full PIM install/upgrade history (package, platform, "
        "dates, version, type). Primary source for [[Server-Artifact-installed-versions]]."),
    "CNF_INFO/tmp_dir": ("Server-CNF_INFO-tmp_dir",
        "Working/diagnostic files: log4j scanner output, `ctmcheckdb.<n>`, `CS_dbglvl.txt`, "
        "`C_time_stamps.txt`, `NS_*.txt` working captures."),
    "LOG_INFO": ("Server-LOG_INFO",
        "Control-M/Server log root — the subsections below hold process logs, services "
        "logs/configs, embedded Kafka, and job status files."),
    "LOG_INFO/proclog": ("Server-LOG_INFO-proclog",
        "Process logs (`proclog`). Families by prefix: `CE.*` (engine, incl. periodic "
        "pstack snapshots), `TR*` (tracker), `CS<pid>*`, `CA.*` (Configuration Agent, "
        "with per-thread `_CO_`/`_CSE_`/`_CSU_`/`_DBC_`/`_EX_` logs), `RT*`, `WD*`, "
        "`U_SQL*`, `CTMIPC*`, plus `agents_availability_*`. **Note:** the rotated "
        "`LOG_INFO/proclog.save/` copies are covered by this note too (deliberate "
        "deviation from one-note-per-directory)."),
    "LOG_INFO/log": ("Server-LOG_INFO-log",
        "Services operation logs (`log/services/`): `apache_kafka_*` / "
        "`apache_zookeeper_*` health, start, stop logs, and `commands.log`."),
    "LOG_INFO/services": ("Server-LOG_INFO-services",
        "ctms microservices configuration: `ctms-*-application.yml` per service, "
        "gateway properties, and `config/custom/` user overrides "
        "(`BootPropertiesUserOverride.yml`) which win over shipped defaults. "
        "See [[Server-Component-ctms-services]]."),
    "LOG_INFO/kafka": ("Server-LOG_INFO-kafka",
        "Embedded Kafka/ZooKeeper for Server-side services: broker/controller configs, "
        "JAAS configs, and `kafka_data/log/` (largest file count in the Server archive)."),
    "LOG_INFO/status": ("Server-LOG_INFO-status",
        "Per-job status files named `<n>_<n>.<ts>_<n>` — presence/volume is the useful "
        "signal at skeleton stage."),
    "AG_TBL_CTM": ("Server-AG_TBL_CTM",
        "Agent-related Server DB tables as CSV: `AGENT_DISCOVERY(_ACTIVE)`, `CMR_NODES`, "
        "`CMS_AGPRM` — the Server-side registry of agents and node parameters."),
    "HA_TBL_CTM": ("Server-HA_TBL_CTM",
        "High-availability tables: `CMR_LIFE_CHECK_MESSAGES`, `CMS_FILE_SYNC`, "
        "`CMS_HA_PARAMS`, `CMS_HA_SYSPRM`, `CMS_HA_TIMESTAMP` — primary/failover state."),
    "TBL_INFO": ("Server-TBL_INFO",
        "Database-side diagnostics: `ctmdbcheck.txt` ([[Server-Artifact-ctmdbcheck]]), "
        "`ctmdbcount.txt`, `ctm_ora_readiness.txt` (Oracle readiness), `dbversion.txt`."),
    "FNC_INFO": ("Server-FNC_INFO",
        "Functional diagnostics run by the collector: `ctm_agstat.txt` (agent "
        "availability — [[Server-Artifact-agent-availability]]), `ctmlog.txt`, "
        "`ctmdbcount.txt`, `check_schema.txt`."),
    "BMCINSTALL": ("Server-BMCINSTALL",
        "Install/upgrade history: `CtmInstalledVersions.<n>.log` snapshots, per-product "
        "install logs in `log/`, java reports, external java path files. Cross-reference "
        "when symptoms began at an install/upgrade window."),
    "MIG_INFO": ("Server-MIG_INFO",
        "Migration working area (`logs/`, `temp/`) — empty in the sample; populated "
        "during platform/DB migrations."),
    "db": ("Server-db",
        "Database diagnostics root. This sample is **Oracle**-backed — no PostgreSQL "
        "section; see the subsections for Oracle client config and DBU outputs."),
    "db/oracle": ("Server-db-oracle",
        "Oracle client/network config: `tnsnames.ora`, `sqlnet.ora`, `ojdbc.properties`, "
        "`oracle-nls-sort.csv`. **Note:** `db/oracle_check_req/` (Oracle requirements "
        "check output) is covered by this note too (deliberate deviation)."),
    "db/DBUtils": ("Server-db-DBUtils",
        "Control-M database utility outputs: `DBUCheck`, `DBUStatus`, `DBUShow`, "
        "`DBUVersion`, `DBUTransactions` — same format family as the EM-side "
        "[[Artifact-DBUCheck]]."),
    "db/DBUData": ("Server-db-DBUData",
        "DBU working data and scheduled check logs (`dbu_show_privs_*`, mirror checks)."),
    "OS": ("Server-OS",
        "OS diagnostics for the Control-M/Server host. Same capture families as the EM "
        "host — interpret via the EM-side notes: [[OS-Performance]], [[OS-Network]], "
        "[[OS-Memory]], [[OS-Processes]], [[OS-Java]], [[OS-Hardware]], [[OS-StartUp]]. "
        "Differences in this sample: `FileSystem.txt`/`KernelParameters.txt` at the OS "
        "root, no separate `Disk/` folder."),
    "report": ("Server-report",
        "**HCU-generated Server analyses**: [[Server-Artifact-SYSPRM-csv]], "
        "[[Server-Artifact-new_day-csv]], [[Server-Artifact-download-csv]], "
        "[[Server-Artifact-jobs_count-csv]], [[Server-Artifact-CE-Heap]], "
        "[[Server-Artifact-thread-pools]], [[Server-Artifact-db-performance-csvs]], "
        "`java_memory.csv`, `disk-benchmark.txt`, `dns_report.txt`, and CMR order/request "
        "status CSVs."),
    "hcu_logs": ("Server-hcu_logs",
        "The collector's own execution log for this Server run — the completeness gate. "
        "Same format as the EM-side [[Artifact-hcu-collector-log]]; read it before "
        "concluding anything from a missing file."),
}

SERVER_COMPONENTS = {
    "Server-Component-CE": (
        "Control-M/Server Engine (CE)",
        "Java engine process. Heap reported by [[Server-Artifact-CE-Heap]]; internal "
        "thread pools (RequestDispatcher etc., with their CONFIG.* sizing parameters) "
        "reported by [[Server-Artifact-thread-pools]].",
        ["Server-LOG_INFO-proclog", "Server-report"],
        "Logs: `CE.*` proclogs (largest family, incl. `CE_periodic_pstack_snapshot`)."),
    "Server-Component-CS": (
        "CS process family",
        "Main Control-M/Server process family (`CS<pid>*` proclogs). "
        "> [UNVERIFIED — confirm against docs] exact role split vs CE.",
        ["Server-LOG_INFO-proclog"], ""),
    "Server-Component-CA": (
        "Configuration Agent (CA)",
        "Server-side configuration agent; `CA.<pid>` proclogs carry per-thread logs "
        "(`_CO_`, `_CSE_`, `_CSU_`, `_CS_`, `_DBC_`, `_EX_`).",
        ["Server-LOG_INFO-proclog"], ""),
    "Server-Component-TR": (
        "Tracker (TR)",
        "Job tracking process family — second-largest proclog family in the sample. "
        "> [UNVERIFIED — confirm against docs] tracks job execution state changes.",
        ["Server-LOG_INFO-proclog"], ""),
    "Server-Component-RT": (
        "RT process",
        "`RT*` proclog family. > [UNVERIFIED — confirm against docs] router/real-time "
        "communication role.",
        ["Server-LOG_INFO-proclog"], ""),
    "Server-Component-WD": (
        "Watchdog (WD)",
        "`WD*` proclog family. > [UNVERIFIED — confirm against docs] monitors/restarts "
        "Server processes.",
        ["Server-LOG_INFO-proclog"], ""),
    "Server-Component-NS": (
        "NS (agent communication)",
        "Agent-communication subsystem; per-agent thread pools reported in "
        "[[Server-Artifact-thread-pools]] (`NsThreadPool`, `Ns_PrintAll`), working "
        "captures `NS_*.txt` in [[Server-CNF_INFO-tmp_dir]]. "
        "> [UNVERIFIED — confirm against docs] runs inside the CE JVM.",
        ["Server-CNF_INFO-tmp_dir", "Server-report"], ""),
    "Server-Component-Kafka-Server": (
        "Kafka / ZooKeeper (Server side)",
        "Embedded messaging for Server-side ctms services.",
        ["Server-LOG_INFO-kafka", "Server-LOG_INFO-log"],
        "Health/start/stop logs in [[Server-LOG_INFO-log]]; broker configs and logs in "
        "[[Server-LOG_INFO-kafka]]."),
    "Server-Component-ctms-services": (
        "ctms microservices",
        "Server-side microservices seen in the sample: `ctms-api-gateway`, `ctms-order`, "
        "`ctms-job-info`, `ctms-app-updates`, `ctm-hybrid-communication-proxy` (plus "
        "kafdrop tooling). Configs (and `custom/BootPropertiesUserOverride.yml`) in "
        "[[Server-LOG_INFO-services]]. Split into per-service notes when enrichment "
        "needs it.",
        ["Server-LOG_INFO-services", "Server-LOG_INFO-log"], ""),
}

SERVER_ARTIFACTS = {
    "Server-Artifact-SYSPRM-csv": (
        "SYSPRM.csv",
        "report/SYSPRM.csv",
        "Single-row snapshot of Control-M/Server system parameters plus runtime state "
        "(versions, New Day time `DAYTIME`, AJF/log retention settings, MAXJOBLOG/"
        "MAXAJFREC/MAXTRY, SSL_ENBL, MIRRORDB, PRIMARY_MIRROR, CURRENT_STATE/"
        "DESIRED_STATE). The Server-side equivalent of EM's PARAMS dump — read it first "
        "for any Server tuning question.",
        "Server-report"),
    "Server-Artifact-new_day-csv": (
        "new_day.csv",
        "report/new_day.csv",
        "New Day procedure timings per run: `TOTAL` plus phase breakdown "
        "(`IOALOG_CLEAN`, `STATISTICS_CLEAN`, `AJF_CLEAN`, `SYSTEM_DAILY`). "
        "> [UNVERIFIED — confirm against docs] units are milliseconds. Rising totals "
        "or a dominant phase localize New Day slowness.",
        "Server-report"),
    "Server-Artifact-download-csv": (
        "download.csv",
        "report/download.csv",
        "Per-download timings and volumes: `SEND_TIME`, `TOTAL_TIME`, `JOBS`, "
        "`CONDITIONS`, `Q_RESOURCES`, `CTL_RESOURCES` — the Server-side view of the "
        "net download that EM's Gateway consumes ([[Check-defaults_rsc]]).",
        "Server-report"),
    "Server-Artifact-jobs_count-csv": (
        "jobs_count.csv",
        "report/jobs_count.csv",
        "Job counts by state over time (`TIME`, `STATE`, `COUNT`) — the quick view of "
        "AJF size and state mix.",
        "Server-report"),
    "Server-Artifact-CE-Heap": (
        "CE_Heap.txt",
        "report/CE_Heap.txt",
        "`ctmipc -DEST CE -MSGID JMX -DATA HEAP` output: max/committed/used heap of the "
        "[[Server-Component-CE]] JVM. used≈max is the Server-side analogue of EM heap "
        "exhaustion.",
        "Server-report"),
    "Server-Artifact-thread-pools": (
        "Thread pool reports (CtmThreadPool / NsThreadPool / Ns_PrintAll)",
        "report/{CtmThreadPool,NsThreadPool,Ns_PrintAll}.txt",
        "`ctmipc ... CTL` outputs. `CtmThreadPool`: per-pool queue/threads/active/runs/"
        "peak/max with the CONFIG.* parameter that sizes each pool (e.g. "
        "`CTM_REQUEST_THREAD_POOL_SIZE`). `NsThreadPool`/`Ns_PrintAll`: per-agent "
        "running/pending communication threads. peak==max with queueing suggests an "
        "undersized pool.",
        "Server-report"),
    "Server-Artifact-db-performance-csvs": (
        "DB performance CSVs",
        "report/{primary_db_performance,mirror_db_performance,db_updates}.csv",
        "Collector-run DB operation benchmarks against primary (and mirror, if "
        "configured) plus update-rate stats — the Server-side analogue of EM's "
        "[[Artifact-db-perf-sort-report]].",
        "Server-report"),
    "Server-Artifact-ctmdbcheck": (
        "ctmdbcheck.txt",
        "TBL_INFO/ctmdbcheck.txt",
        "Control-M/Server database space/health check output; pair with "
        "`ctm_ora_readiness.txt` and `dbversion.txt` in [[Server-TBL_INFO]].",
        "Server-TBL_INFO"),
    "Server-Artifact-installed-versions": (
        "Installed versions history",
        "CNF_INFO/versions/installed-versions.txt (+ BMCINSTALL/CtmInstalledVersions.<n>.log)",
        "Complete PIM install/upgrade history: package, platform, package date, install "
        "date, version, install type. First stop for 'what changed and when' — "
        "correlate with [[Server-BMCINSTALL]] install logs.",
        "Server-CNF_INFO-versions"),
    "Server-Artifact-agent-availability": (
        "Agent availability reports",
        "FNC_INFO/ctm_agstat.txt (+ AG_TBL_CTM/AGENT_DISCOVERY*.csv)",
        "`agent_list` health-check output plus the AGENT_DISCOVERY table dumps: which "
        "agents the Server knows, and their availability state at collection time. "
        "Start here for agent-unavailable symptoms before reading proclogs.",
        "Server-FNC_INFO"),
}

AGENT_SECTION_INFO = {
    "": ("Agent-Archive-Root",
         "Top level of a Control-M/Agent `ctm_data_collector` archive. **Naming differs "
         "from EM/Server**: `_data_<YYYYMMDD>_<HHMMSS>_<os>_<hostname>_<user>`. Sample "
         "baseline: Agent 9.0.21.300 on Linux. No check_config results exist for Agent "
         "archives in this sample."),
    "AG_CNF": ("Agent-AG_CNF",
        "Agent configuration: `data/` holds ~60 parameter/state `.dat` files "
        "(`CONFIG.dat` — see [[Agent-Artifact-CONFIG-dat]] — plus `ag_ver.dat`, "
        "`AG_PREREQ.dat`, `JAVACONF.dat`, application-plugin maps, SSL material, "
        "`CFG_BACKUP/`, `remote_utils/`, `rhdetails/`), with `versions/` and "
        "`Agent_dependencies.txt` alongside. **Note:** `AG_CNF/data/` is covered by "
        "this note (deliberate deviation from one-note-per-directory)."),
    "AG_LOG": ("Agent-AG_LOG",
        "Agent log root: `locks/` (lock and semaphore files), `pid/`/`procid/`, "
        "`onstmt/`, `capdef/`, `runtime/`, `temp/`, plus the two big subsections below."),
    "AG_LOG/proclog": ("Agent-AG_LOG-proclog",
        "Agent process logs by prefix: `AG_`, `AS_` (largest family), `AT_`, `ATW`, "
        "`AC_`, `WK_`, `WD_`, `ctmcfg_`, `ctmjavareq_`, `uploader_`, `updstd_`, "
        "start/shutdown logs — plus `Metrics/` and `MemoryDump/`."),
    "AG_LOG/dailylog": ("Agent-AG_LOG-dailylog",
        "`daily_ctmag_<date>.log` — one file per day of agent activity; the first place "
        "to establish a timeline for agent-side symptoms."),
    "AG_UTIL": ("Agent-AG_UTIL",
        "Utility diagnostic outputs: [[Agent-Artifact-ag_diag_comm]] (`ag_diag_comm.txt`), "
        "`ctmdllver.txt`, `java_version.txt`, `permission_check.txt`, `shagent.txt`."),
    "report": ("Agent-report",
        "HCU-generated Agent analyses: [[Agent-Artifact-env-report]], "
        "[[Agent-Artifact-io_benchmark]], `daily_report.dat`, and the `measure/` "
        "subsection below."),
    "report/measure": ("Agent-report-measure",
        "Per-process resource measurements: daily CSVs per process family "
        "(`<date>_{AG,AGJ,AS,AT,ATW,DS,UPLD}.csv`), `AGENTAPP_<date>.csv`, and "
        "per-PID snapshots. See [[Agent-Artifact-measure-csvs]]."),
    "hcu_logs": ("Agent-hcu_logs",
        "Collector execution log for this Agent run (completeness gate — same format as "
        "[[Artifact-hcu-collector-log]]) plus `data/` with per-plugin XML captures "
        "(`CNF_CM*.xml` for each installed application plugin, `BSS_AG.xml`, "
        "`CNF_AG.xml`)."),
    "OS": ("Agent-OS",
        "OS diagnostics for the Agent host — same capture families as the EM host "
        "(interpret via [[OS-Performance]], [[OS-Network]], [[OS-Memory]], "
        "[[OS-Processes]], [[OS-Java]], [[OS-Hardware]], [[OS-StartUp]]), plus a "
        "`SystemLog/` extra (`SystemLog.txt`, `SystemWarnings.txt`) not present in the "
        "EM sample."),
}

AGENT_COMPONENTS = {
    "Agent-Component-AG": (
        "AG process",
        "Agent listener/communication process. > [UNVERIFIED — confirm against docs] "
        "receives Server requests.",
        ["Agent-AG_LOG-proclog", "Agent-report-measure"],
        "Logs: `AG_*` proclogs; resource usage in `<date>_AG.csv`."),
    "Agent-Component-AS": (
        "AS process",
        "Largest proclog family in the sample. > [UNVERIFIED — confirm against docs] "
        "job submission/execution role.",
        ["Agent-AG_LOG-proclog", "Agent-report-measure"],
        "Logs: `AS_*` proclogs; resource usage in `<date>_AS.csv`."),
    "Agent-Component-AT": (
        "AT process (tracker)",
        "> [UNVERIFIED — confirm against docs] tracks submitted job state and reports "
        "back to the Server.",
        ["Agent-AG_LOG-proclog", "Agent-report-measure"],
        "Logs: `AT_*` proclogs; resource usage in `<date>_AT.csv`."),
    "Agent-Component-ATW": (
        "ATW process",
        "> [UNVERIFIED — confirm against docs] tracker worker.",
        ["Agent-AG_LOG-proclog", "Agent-report-measure"],
        "Logs: `ATW*` proclogs; resource usage in `<date>_ATW.csv`."),
    "Agent-Component-AGJ": (
        "AGJ process",
        "Java-side agent process; own measure CSVs incl. per-PID snapshots. "
        "> [UNVERIFIED — confirm against docs] exact role.",
        ["Agent-AG_LOG-proclog", "Agent-report-measure"],
        "Resource usage in `<date>_AGJ.csv` and `AGJ_<n>_<ts>.csv`. Other observed "
        "process families (UPLD, DS, WD, AC, WK) are described in "
        "[[Agent-AG_LOG-proclog]] until they warrant their own notes."),
}

AGENT_ARTIFACTS = {
    "Agent-Artifact-ag_diag_comm": (
        "ag_diag_comm.txt",
        "AG_UTIL/ag_diag_comm.txt",
        "Control-M/Agent Communication Diagnostic Report: agent user/directory/platform, "
        "authorized Server hosts, ports, SSL state, version/fixpack. The single most "
        "information-dense file for agent↔server connectivity issues — parse it before "
        "any proclog.",
        "Agent-AG_UTIL"),
    "Agent-Artifact-CONFIG-dat": (
        "CONFIG.dat",
        "AG_CNF/data/CONFIG.dat",
        "Agent parameter file — the agent-side source of truth for communication, "
        "tracker, and job-handling settings.",
        "Agent-AG_CNF"),
    "Agent-Artifact-measure-csvs": (
        "Process measure CSVs",
        "report/measure/<date>_{AG,AGJ,AS,AT,ATW,DS,UPLD}.csv (+ AGENTAPP_<date>.csv)",
        "Daily per-process resource usage series for each agent process family — the "
        "agent-side analogue of EM's [[Artifact-metric-csvs]]; sustained growth is the "
        "early-warning signal.",
        "Agent-report-measure"),
    "Agent-Artifact-io_benchmark": (
        "io_benchmark.txt",
        "report/io_benchmark.txt",
        "Collector-run I/O benchmark of the agent host filesystem — the agent-side "
        "analogue of [[Artifact-disk-benchmark]].",
        "Agent-report"),
    "Agent-Artifact-env-report": (
        "env-report.txt",
        "report/env-report.txt (+ report/daily_report.dat)",
        "Environment summary generated by the collector for the agent host.",
        "Agent-report"),
}

MODELS = {
    "EM": {
        "sections": SECTION_INFO, "components": COMPONENTS, "artifacts": ARTIFACTS,
        "prefix": "", "root_note": "HCU-Archive-Root",
        "check_section_note": "EM-check_config_results",
        "check_report_glob": "EM/check_config_results/check_config_report_*.json",
    },
    "Server": {
        "sections": SERVER_SECTION_INFO, "components": SERVER_COMPONENTS,
        "artifacts": SERVER_ARTIFACTS,
        "prefix": "Server-", "root_note": "Server-Archive-Root",
        "check_section_note": None,
        # no check_config in the Server sample archive; set when a sample has one
        "check_report_glob": None,
    },
    "Agent": {
        "sections": AGENT_SECTION_INFO, "components": AGENT_COMPONENTS,
        "artifacts": AGENT_ARTIFACTS,
        "prefix": "Agent-", "root_note": "Agent-Archive-Root",
        "check_section_note": None,
        "check_report_glob": None,
    },
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

def build_section_notes(v: Vault, src: Path, product: str):
    model = MODELS[product]
    sections = model["sections"]
    for rel, (note_name, desc) in sections.items():
        p = src / rel if rel else src
        inventory = []
        if p.is_dir():
            seen = set()
            for f in sorted(p.rglob("*")):
                if f.is_file():
                    n = normalize_filename(str(f.relative_to(p)).replace("\\", "/"))
                    if n not in seen:
                        seen.add(n)
                        inventory.append(n)
        # log families for EM/Log come from filelist since bodies were excluded
        moc = f"[[{product}-MOC]]" if product != "EM" else "[[HCU-MOC]]"
        parent = moc if rel == "" else f"[[{sections.get(str(Path(rel).parent) if str(Path(rel).parent) != '.' else '', sections[''])[0]}]]"
        related_checks = [f"[[{c}]]" for c in CHECK_NOTE_NAMES] if (
            model["check_section_note"] and note_name == model["check_section_note"]) else []
        body = fm(type="archive-section", section=(rel or "/"), product=product,
                  status="skeleton", tags=["hcu", "section"])
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

def build_check_notes(v: Vault, report: dict, product: str):
    prefix = MODELS[product]["prefix"]
    section_note = MODELS[product]["check_section_note"]
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
        note = f"{prefix}Check-{name}"
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
        body = fm(type="check", check_name=name, product=product,
                  status="skeleton", tags=["hcu", "check"])
        body += f"# Check — {name}\n\n"
        body += f"**Section:** [[{section_note}]] · **Report:** [[Artifact-check_config_report-json]]\n\n"
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


def build_component_notes(v: Vault, product: str):
    for note, (title, desc, sections, extra) in MODELS[product]["components"].items():
        body = fm(type="component", product=product, status="skeleton",
                  tags=["hcu", "component"])
        body += f"# {title}\n\n{desc}\n\n"
        body += "**Archive sections:** " + " · ".join(f"[[{s}]]" for s in sections) + "\n"
        if extra:
            body += f"\n{extra}\n"
        body += "\n## Known findings\n\n_(enrichment pending)_\n"
        v.add("30-Components", note, body)


def build_artifact_notes(v: Vault, product: str):
    for note, (title, path, desc, section) in MODELS[product]["artifacts"].items():
        body = fm(type="artifact", product=product, status="skeleton",
                  tags=["hcu", "artifact"])
        body += f"# {title}\n\n**Archive path:** `{sanitize(path)}` · **Section:** [[{section}]]\n\n{desc}\n"
        v.add("25-Artifacts", note, body)


def build_seed_chain(v: Vault):
    folders = {"finding": "40-Findings", "root-cause": "50-Root-Causes",
               "resolution": "60-Resolutions"}
    for note, (title, kind, body_text, comps) in SEED_CHAIN.items():
        body = fm(type=kind, product="EM", status="seeded", tags=["hcu", kind])
        body += f"# {title}\n\n{body_text}\n\n"
        body += "**Components:** " + " · ".join(f"[[{c}]]" for c in comps) + "\n"
        v.add(folders[kind], note, body)


def build_templates(v: Vault):
    for name, (kind, text) in TEMPLATES.items():
        v.add("90-Templates", name, fm(type="template", template_for=kind) + text)


def build_index(v: Vault, report: dict, product: str):
    model = MODELS[product]
    checks = "\n".join(f"- [[{c}]]" for c in CHECK_NOTE_NAMES) or "- _(no check_config report in this product's sample archive)_"
    sections = "\n".join(f"- [[{n}]]" for _, (n, _) in sorted(model["sections"].items()) if n != model["root_note"])
    comps = "\n".join(f"- [[{c}]]" for c in model["components"])
    arts = "\n".join(f"- [[{a}]]" for a in model["artifacts"])
    version = report.get("version") if report else "(unknown)"
    moc = fm(type="moc", product=product, status="skeleton", tags=["hcu", "moc"])
    if product == "EM":
        moc += f"""# EM — Map of Content

Everything for interpreting the **EM side** of an HCU archive. Built from an EM
{version} sample. Master index: [[HCU-MOC]].

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
    else:
        moc += f"""# {product} — Map of Content

Everything for interpreting the **Control-M/{product} side** of an HCU archive.
Master index: [[HCU-MOC]] · Schema: [[About-This-Vault]].

## Health checks (check_config)
{checks}

## Archive sections
- [[{model["root_note"]}]]
{sections}

## Components
{comps}

## Key artifacts
{arts}

## Diagnostic chains
- _(enrichment pending — add chains as cases are worked)_
"""
    v.add("00-Index", f"{product}-MOC", moc)

    if product != "EM":
        return  # playbooks/About are vault-wide, maintained with the EM build

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
- **Product prefixing:** every note carries `product:` frontmatter (EM / Server /
  Agent). EM note names keep **no prefix** (the vault started EM-only — backward
  compatibility). Server and Agent notes are name-prefixed `Server-` / `Agent-`
  (e.g. `Server-LOG_INFO`, `Agent-Check-...`). Index entry points:
  [[HCU-MOC]] (master) → [[EM-MOC]] · [[Server-MOC]] · [[Agent-MOC]].
- `status: skeleton` = structure generated deterministically from a real archive,
  enrichment pending. `status: seeded` / `status: enriched` after review.
- All customer identifiers are sanitized (`<hostname>`, `<user>`, `<n>`, `<ts>`).
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
    product = sys.argv[3] if len(sys.argv) > 3 else "EM"
    if product not in MODELS:
        sys.exit(f"Unknown product {product!r}; expected one of {sorted(MODELS)}")
    register_archive_tokens(src.name)
    model = MODELS[product]

    report = None
    if model["check_report_glob"]:
        reports = sorted(src.glob(model["check_report_glob"]))
        if reports:
            report = json.loads(reports[-1].read_text())
    if product == "EM" and report is None:
        sys.exit("No check_config report found — refusing to build EM skeleton without it")

    v = Vault(out)
    CHECK_NOTE_NAMES.clear()
    if report:
        build_check_notes(v, report, product)   # populates CHECK_NOTE_NAMES first
    build_section_notes(v, src, product)
    build_component_notes(v, product)
    build_artifact_notes(v, product)
    if product == "EM":
        build_seed_chain(v)
        build_templates(v)
    build_index(v, report, product)
    v.write()
    defined, linked = v.link_report()
    dangling = sorted(x for x in linked if x not in defined)
    orphans = sorted(x for x in defined if x not in linked and not x.startswith("tpl-"))
    print(f"Product: {product}; notes written: {len(v.notes)}")
    print(f"Dangling links (targets outside this run or not yet created): {dangling or 'none'}")
    print(f"Orphan notes (nothing links to them): {orphans or 'none'}")


if __name__ == "__main__":
    main()
