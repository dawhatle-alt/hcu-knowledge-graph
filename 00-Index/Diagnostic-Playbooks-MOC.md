---
type: moc
status: skeleton
tags:
  - hcu
  - moc
---

# Diagnostic Playbooks — MOC

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
