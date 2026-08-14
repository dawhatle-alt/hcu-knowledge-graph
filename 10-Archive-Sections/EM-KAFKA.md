---
type: archive-section
section: EM/KAFKA
status: skeleton
tags:
  - hcu
  - section
---

# EM-KAFKA

Embedded Kafka/ZooKeeper (messaging backbone for EM services): broker and controller configs, JAAS configs, and `Log/` with server logs, GC logs, state-change and log-cleaner logs. First stop for Workflow Insights / service messaging issues.

**Parent:** [[EM]]

## File inventory (normalized)

- `Log/kafka-authorizer.log`
- `Log/kafka-request.log`
- `Log/kafka.err`
- `Log/kafka.std`
- `Log/kafka_controller.log`
- `Log/kafka_controller.log.<n>`
- `Log/kafka_log-cleaner.log`
- `Log/kafka_log-cleaner.log.<n>`
- `Log/kafka_server.log`
- `Log/kafka_server_gc.log`
- `Log/kafka_server_gc.log.<n>`
- `Log/kafka_state-change.log`
- `Log/kraft_controller.err`
- `Log/kraft_controller.log`
- `Log/kraft_controller.std`
- `Log/zookeeper.err`
- `Log/zookeeper.std`
- `Log/zookeeper_gc.log`
- `Log/zookeeper_gc.log.<n>`
- `Log/zookeeper_server.log`
- `Log/zookeeper_server.log.<n>`
- `config/bmc.controller.properties`
- `config/bmc.server.properties`
- `config/bmc.zookeeper.properties`
- `config/connect-console-sink.properties`
- `config/connect-console-source.properties`
- `config/connect-distributed.properties`
- `config/connect-file-sink.properties`
- `config/connect-file-source.properties`
- `config/connect-log4j.properties`
- `config/connect-mirror-maker.properties`
- `config/connect-standalone.properties`
- `config/consumer.properties`
- `config/kraft/broker.properties`
- `config/kraft/controller.properties`
- `config/kraft/server.properties`
- `config/log4j.properties`
- `config/mode.new.server.properties`
- `config/mode.old.server.properties`
- `config/producer.properties`
- `config/server.properties`
- `config/tools-log4j.properties`
- `config/trogdor.conf`
- `config/zookeeper.properties`
- `jaas_config/client_jaas.prop`
- `jaas_config/server_jaas.conf`
- `jaas_config/zookeeper_jaas.conf`
