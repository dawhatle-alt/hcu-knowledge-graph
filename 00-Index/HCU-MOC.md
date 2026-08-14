---
type: moc
status: skeleton
tags:
  - hcu
  - moc
---

# HCU Knowledge Graph — Map of Content

Source of truth for interpreting **Control-M Health Check Utility (`ctm_data_collector`)**
archives. Built from an EM 9.0.22.100 sample; extend with Server-side samples.

**Agent entry protocol:**
1. Read [[About-This-Vault]] for schema and retrieval rules.
2. Orient in the archive via [[HCU-Archive-Root]] and the section notes.
3. For pass/fail state, parse the latest [[Artifact-check_config_report-json]] — read
   `production_size` first, then `results[]`, and map each check to its note below.
4. Judge archive completeness via [[Artifact-hcu-collector-log]] before concluding
   anything from a *missing* file.
5. Route symptoms via [[Diagnostic-Playbooks-MOC]].

## Health checks (check_config)
- [[Check-machine]]
- [[Check-communication]]
- [[Check-defaults_rsc]]
- [[Check-controlm-web-context]]
- [[Check-reporting-facility-context]]
- [[Check-system_parameters]]
- [[Check-tomcat_config]]
- [[Check-tomcat_server]]
- [[Check-automation_api_properties]]
- [[Check-site_config]]

## Archive sections
- [[HCU-Archive-Root]]
- [[EM]]
- [[EM-AAPI]]
- [[EM-Client_Update]]
- [[EM-DBT]]
- [[EM-EMWEB]]
- [[EM-KAFKA]]
- [[EM-LDAP]]
- [[EM-Log]]
- [[EM-Mail]]
- [[EM-ReportingFacility]]
- [[EM-Rsc]]
- [[EM-SCH]]
- [[EM-SSO]]
- [[EM-Services]]
- [[EM-TBL]]
- [[EM-WI]]
- [[EM-check_config_results]]
- [[EM-ini]]
- [[Install]]
- [[OS]]
- [[OS-Disk]]
- [[OS-Hardware]]
- [[OS-Java]]
- [[OS-Memory]]
- [[OS-Network]]
- [[OS-Performance]]
- [[OS-Processes]]
- [[OS-StartUp]]
- [[Thrift]]
- [[db]]
- [[db-DBUData]]
- [[db-DBUtils]]
- [[db-postgresql]]
- [[hcu_logs]]
- [[report]]
- [[report-observability]]

## Components
- [[Component-GUI-Server-GSR]]
- [[Component-Gateway-GTW]]
- [[Component-Configuration-Server-CMS]]
- [[Component-GCS]]
- [[Component-controlm-web]]
- [[Component-em-scheduling-service]]
- [[Component-em-ctm-request-service]]
- [[Component-em-mft-updates-service]]
- [[Component-aisrv-web-Jett-AI]]
- [[Component-authorization-service]]
- [[Component-Kafka-ZooKeeper]]
- [[Component-Tomcat-EMWEB]]
- [[Component-Reporting-Facility]]
- [[Component-Automation-API]]
- [[Component-PostgreSQL]]

## Key artifacts
- [[Artifact-check_config_report-json]]
- [[Artifact-check_config-txt]]
- [[Artifact-EMSiteConfig-ini]]
- [[Artifact-Defaults-rsc]]
- [[Artifact-communication-xml]]
- [[Artifact-metric-csvs]]
- [[Artifact-db-perf-sort-report]]
- [[Artifact-disk-benchmark]]
- [[Artifact-metrics-validation]]
- [[Artifact-java_memory-csv]]
- [[Artifact-table-size-csvs]]
- [[Artifact-pg_stat_activity]]
- [[Artifact-pg_settings]]
- [[Artifact-DBUCheck]]
- [[Artifact-hcu-collector-log]]

## Diagnostic chains
- [[Finding-aisrv-web-connection-refused]] → [[RootCause-missing-lsof-prerequisite]] → [[Resolution-install-lsof-restart-ai]]
- [[Finding-em-jvm-heap-exhaustion]] → _(root cause pending)_
- [[Finding-gtw-update-backlog]] → _(root cause pending)_
- [[Finding-em-host-resource-shortage]] → _(root cause pending)_
- _(enrichment pending — add chains as cases are worked)_
