---
type: archive-section
section: EM/Services
status: skeleton
tags:
  - hcu
  - section
---

# EM-Services

EM microservices layer configuration: per-service `log4j2.*` logging configs, `*-application.yml` service configs, `services_template.yml`, desired-state and init templates, JAAS configs, and — critically — `config/custom/` user overrides (e.g. `BootPropertiesUserOverride.yml`) which win over shipped defaults and are referenced by several [[Check-controlm-web-context|context checks]].

**Parent:** [[EM]]

## File inventory (normalized)

- `config/aisrv-web-application.yml`
- `config/authorization-service-application.yml`
- `config/controlm-web-application.yml`
- `config/custom/BootPropertiesUserOverride.yml`
- `config/custom/authorization-service-custom.yml`
- `config/custom/em-ctm-request-service-custom.yml`
- `config/custom/em-mft-updates-service-custom.yml`
- `config/custom/em-scheduling-service-custom.yml`
- `config/custom/em-scheduling-service.yml`
- `config/custom/services-common-application-custom.yml`
- `config/custom/validation-service-custom.yml`
- `config/diagnosedoc/kafka_readme.txt`
- `config/drain_services_list.json`
- `config/dynamic/protocol-translator-8088.yml`
- `config/em-ctm-request-service-application.yml`
- `config/em-mft-updates-service-application.yml`
- `config/em-scheduling-service-application.yml`
- `config/https_client_server.properties`
- `config/https_client_server.properties_<n>_<n>.bak`
- `config/kafka_added.properties`
- `config/log4j.controller`
- `config/log4j.kafka`
- `config/log4j.zookeeper`
- `config/log4j2.aisrv-web`
- `config/log4j2.authorization-service`
- `config/log4j2.controlm-web`
- `config/log4j2.em-ctm-request-service`
- `config/log4j2.em-mft-updates-service`
- `config/log4j2.em-scheduling-service`
- `config/log4j2.kafka-client`
- `config/log4j2.protocol-translator`
- `config/log4j2.reporting-facility`
- `config/log4j2.services-configuration-agent`
- `config/log4j2.services-configuration-agent-cli`
- `config/log4j2.services-health-monitor`
- `config/log4j2.validation-service`
- `config/protocol-translator-application.yml`
- `config/reporting-facility-application.yml`
- `config/sched/currentProcesses.txt`
- `config/sched/schedConfig_ONPREM_EM.yml`
- `config/services-common-application.yml`
- `config/services-configuration-agent-application.yml`
- `config/services-health-monitor-application.yml`
- `config/services.yml`
- `config/services_template.yml`
- `config/validation-service-application.yml`
- `config/versionInfo/features.txt`
- `context/aisrv-web.yml`
- `context/apache-kafka.yml`
- `context/apache-zookeeper.yml`
- `context/authorization-service.yml`
- `context/controlm-web.yml`
- `context/em-ctm-request-service.yml`
- `context/em-mft-updates-service.yml`
- `context/em-scheduling-service.yml`
- `context/protocol-translator.yml`
- `context/reporting-facility.yml`
- `context/services-health-monitor.yml`
- `context/validation-service.yml`
- `desired_state/aisrv-web-desired-state.yml`
- … 14 more
