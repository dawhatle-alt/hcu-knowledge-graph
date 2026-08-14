---
type: archive-section
section: db
status: skeleton
tags:
  - hcu
  - section
---

# db

Database diagnostics: PostgreSQL catalog/stat dumps, DBUtils outputs, and DBU data logs. Note: on external/remote DB deployments (like this sample) the local `pgsql/data` folders don't exist and the collector logs 'Source folder does not exist' — expected, not an error. See [[hcu_logs]].

**Parent:** [[HCU-Archive-Root]]

## File inventory (normalized)

- `DBUData/log/DBUCheck<n>.log`
- `DBU_params.dat`
- `DBUtils/DBUCheck.txt`
- `DBUtils/DBUShow.txt`
- `DBUtils/DBUStatus.txt`
- `DBUtils/DBUTransactions.txt`
- `DBUtils/DBUVersion.txt`
- `postgresql/PgFileList.txt`
- `postgresql/pg_class-table.csv`
- `postgresql/pg_database-table.csv`
- `postgresql/pg_locks-table.csv`
- `postgresql/pg_namespace-table.csv`
- `postgresql/pg_service.conf`
- `postgresql/pg_settings-table.csv`
- `postgresql/pg_stat_activity-table.csv`
- `postgresql/pg_stat_all_Tables-table.csv`
- `postgresql/pg_stat_all_indexes-table.csv`
- `postgresql/pg_tablespace-table.csv`
- `postgresql/pg_user-table.csv`
- `postgresql/size-pgsql-data.txt`
- `postgresql/size-pgsql-home.txt`
