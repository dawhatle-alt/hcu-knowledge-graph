---
type: archive-section
section: EM/ini
status: skeleton
tags:
  - hcu
  - section
---

# EM-ini

Classic EM configuration: [[Artifact-EMSiteConfig-ini|EMSiteConfig.ini]] (JVM heap settings per component — checked by [[Check-site_config]]), `mcs.ini`, `config.ini`, `version.ini`, `CONFREG.INI`, per-component `*_DiagLvls.ini` diagnostic levels, and subfolders for SSL, FIPS keys, SAML, and local overrides.

**Parent:** [[EM]]

## File inventory (normalized)

- `CONFIG_HA.INI`
- `CONFREG.INI`
- `EMSiteConfig.ini`
- `SSL/elastic_ca.pem`
- `SSL/elastic_ca_key.pem`
- `SSL/genDemoP12openssl.cfg`
- `SSL/out/out_<n>_<n>_<n>/rootCA_cert.pem`
- `SSL/out/out_<n>_<n>_<n>/rootCA_cert.srl`
- `SSL/out/out_<n>_<n>_<n>/rootCA_key.pem`
- `SSL/out/out_<n>_<n>_<n>/server.csr`
- `SSL/out/out_<n>_<n>_<n>/server_cert.pem`
- `SSL/out/out_<n>_<n>_<n>/server_key.pem`
- `SSL/out/out_<n>_<n>_<n>/tomcat.ini`
- `SSL/out/out_<n>_<n>_<n>/tomcat.p12`
- `SSL/out/out_<n>_<n>_<n>/v3ext.txt`
- `SSL/tomcat.ini`
- `SSL/tomcat.ini_bak<n>`
- `SSL/tomcat.p12`
- `SSL/tomcat.p12_bak<n>`
- `attrs_to_adjust_before_compare.ini`
- `bim_DiagLvls.ini`
- `cha_DiagLvls.ini`
- `cms_DiagLvls.ini`
- `cmsg_DiagLvls.ini`
- `config.ini`
- `emThriftAPI.properties`
- `emdef_DiagLvls.ini`
- `emmftcli.logging.properties`
- `env.ini`
- `fips/KeyAliases.properties`
- `fips/backup/transient_key_<ts>.txt`
- `fips/ctm_key.txt`
- `fips/db_enc_key.txt`
- `fips/storage_key.txt`
- `fips/transfer_key.txt`
- `fips/transient_key.txt`
- `forecast_DiagLvls.ini`
- `gcs.logging.properties`
- `general_signals.ini`
- `gsa.logging.properties`
- `gsr_DiagLvls.ini`
- `gsr_DiagLvls.ini_backup`
- `gsr_DiagLvls.ini_for_debugging`
- `gtw_DiagLvls.ini`
- `idp-valve-ext.properties`
- `idp-valve-redirect.properties`
- `idp-valve.properties`
- `locale.ini`
- `log4j2.rplan_wrapper.xml`
- `maint_DiagLvls.ini`
- `mcs.ini`
- `migratedc_DiagLvls.ini`
- `python_scripts_log_conf.ini`
- `rep.ini`
- `saml/idp-metadata.xml`
- `saml/idp-valve-keystore.jks`
- `server_conf_to_upgrade.xml`
- `services-proxy.properties`
- `sls_DiagLvls.ini`
- `ssl_tomcat_ciphers.xml`
- … 3 more
