---
type: archive-section
section: EM/Log
status: skeleton
tags:
  - hcu
  - section
---

# EM-Log

All EM component logs. Largest section of the archive by far (individual service logs reach 100 MB). Families include GTW/GSR/GCS logs and diag snapshots, `Services/` microservice logs with paired `*_exceptions` logs and `jvm-*` GC logs, Tomcat catalina/access logs, REST server logs, SSL logs, and wrapper output. See the per-family inventory below and [[Diagnostic-Playbooks-MOC]] for routing.

**Parent:** [[EM]]

## File inventory (normalized)

- `GCS_LOG.12403.<n>.<n>`
- `SSL_Logs/cert/.ess.txt`
- `SSL_Logs/cert/.ess.txt_<n>_<n>.bak`
- `SSL_Logs/cert/cmsg.plc`
- `SSL_Logs/cert/cmsg.plc_<n>_<n>.bak`
- `SSL_Logs/cert/ctmkeystore.p12`
- `SSL_Logs/cert/ctmkeystore.p12_<n>_<n>.bak`
- `SSL_Logs/cert/ctmkeytool_activated.txt`
- `SSL_Logs/cert/em.plc`
- `SSL_Logs/cert/em.plc_<n>_<n>.bak`
- `SSL_Logs/cert/ess_key.txt`
- `SSL_Logs/cert/ess_key.txt_<n>_<n>.bak`
- `SSL_Logs/cert/gtw.plc`
- `SSL_Logs/cert/gtw.plc_<n>_<n>.bak`
- `SSL_Logs/cert/openssl.cnf`
- `SSL_Logs/cert/site.plc`
- `SSL_Logs/cert/site.plc_<n>_<n>.bak`
- `SSL_Logs/cert/site_essv6.plc`
- `SSL_Logs/log/cmsg_ssl.log`
- `SSL_Logs/log/ctmkeytool_<n>_<n>.log`
- `Services/AiSrcServiceStart.log`
- `Services/aisrv-web.log`
- `Services/aisrv-web1.log`
- `Services/aisrv-web2.log`
- `Services/aisrv-web3.log`
- `Services/aisrv-web4.log`
- `Services/aisrv-web5.log`
- `Services/aisrv-web_exceptions.log`
- `Services/apache_kafka_config.log`
- `Services/apache_kafka_health.log`
- `Services/apache_kafka_health.log.<n>`
- `Services/apache_kafka_start.log`
- `Services/apache_kafka_stop.log`
- `Services/apache_zookeeper_health.log`
- `Services/apache_zookeeper_health.log.<n>`
- `Services/apache_zookeeper_start.log`
- `Services/apache_zookeeper_stop.log`
- `Services/authorization-service.log`
- `Services/authorization-service1.log`
- `Services/authorization-service2.log`
- `Services/authorization-service3.log`
- `Services/authorization-service4.log`
- `Services/authorization-service5.log`
- `Services/authorization-service_exceptions.log`
- `Services/commands.log`
- `Services/controlm-web.log`
- `Services/controlm-web1.log`
- `Services/controlm-web2.log`
- `Services/controlm-web3.log`
- `Services/controlm-web4.log`
- `Services/controlm-web5.log`
- `Services/controlm-web_exceptions.log`
- `Services/ctm_web_debug.log`
- `Services/ctm_web_logins.log`
- `Services/ctm_web_logins1.log`
- `Services/ctm_web_logins2.log`
- `Services/em-ctm-request-service-<n>.log`
- `Services/em-ctm-request-service.log`
- `Services/em-ctm-request-service_exceptions.log`
- `Services/em-mft-updates-service-<n>.log`
- … 159 more
