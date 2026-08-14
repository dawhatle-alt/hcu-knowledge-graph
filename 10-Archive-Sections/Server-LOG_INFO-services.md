---
type: archive-section
section: LOG_INFO/services
product: Server
status: skeleton
tags:
  - hcu
  - section
---

# Server-LOG_INFO-services

ctms microservices configuration: `ctms-*-application.yml` per service, gateway properties, and `config/custom/` user overrides (`BootPropertiesUserOverride.yml`) which win over shipped defaults. See [[Server-Component-ctms-services]].

**Parent:** [[Server-LOG_INFO]]

## File inventory (normalized)

- `config/ctm-hybrid-communication-proxy-application.yml`
- `config/ctms-api-gateway-service-application.yml`
- `config/ctms-api-gateway-stand-alone.properties`
- `config/ctms-api-gateway.properties`
- `config/ctms-app-updates-service-application.yml`
- `config/ctms-job-info-service-application.yml`
- `config/ctms-order-service-application.yml`
- `config/custom/BootPropertiesUserOverride.yml`
- `config/diagnosedoc/kafka_readme.txt`
- `config/https_client_server.properties`
- `config/kafdrop/kafdrop-SASL.properites`
- `config/kafdrop/kafdrop-SASL.sh`
- `config/kafdrop/kafdrop-tenant.sh`
- `config/kafdrop/refresh-api-services.sh`
- `config/log4j.kafka`
- `config/log4j.zookeeper`
- `config/log4j2.ctm-hybrid-communication-proxy`
- `config/log4j2.ctms-api-gateway-service`
- `config/log4j2.ctms-app-updates-service`
- `config/log4j2.ctms-job-info-service`
- `config/log4j2.ctms-order-service`
- `config/log4j2.kafka-client`
- `config/log4j2.periodic-backup-service`
- `config/log4j2.scheduling-service`
- `config/log4j2.services-configuration-agent`
- `config/log4j2.services-configuration-agent-cli`
- `config/log4j2.services-health-monitor`
- `config/periodic-backup-service-application.yml`
- `config/scheduling-service-application.yml`
- `config/services-configuration-agent-application.yml`
- `config/services-health-monitor-application.yml`
- `config/services.yml`
- `config/services_template.yml`
- `context/apache-kafka.yml`
- `context/apache-zookeeper.yml`
- `context/ctm-hybrid-communication-proxy.yml`
- `context/ctms-api-gateway-service.yml`
- `context/ctms-app-updates-service.yml`
- `context/ctms-job-info-service.yml`
- `context/ctms-order-service.yml`
- `context/periodic-backup-service.yml`
- `context/scheduling-service.yml`
- `context/services-health-monitor.yml`
- `desired_state/apache-kafka-desired-state.yml`
- `desired_state/apache-zookeeper-desired-state.yml`
- `desired_state/ctm-hybrid-communication-proxy-desired-state.yml`
- `desired_state/ctms-api-gateway-service-desired-state.yml`
- `desired_state/ctms-app-updates-service-desired-state.yml`
- `desired_state/ctms-job-info-service-desired-state.yml`
- `desired_state/ctms-order-service-desired-state.yml`
- `desired_state/periodic-backup-service-desired-state.yml`
- `desired_state/scheduling-service-desired-state.yml`
- `desired_state/services-health-monitor-desired-state.yml`
- `init_template/services.yml`
- `jaas_config/client_jaas.conf`
