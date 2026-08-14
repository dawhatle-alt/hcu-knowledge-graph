---
type: archive-section
section: db/postgresql
status: skeleton
tags:
  - hcu
  - section
---

# db-postgresql

PostgreSQL state: `pg_settings` (server config), `pg_stat_activity` (sessions at collection time), `pg_locks`, `pg_stat_all_Tables`/`indexes` (bloat/vacuum/scan stats), `pg_class`, `pg_database`, tablespaces, users, `pg_service.conf`, data/home size captures, and `pg_log/`.

**Parent:** [[db]]

## File inventory (normalized)

- `PgFileList.txt`
- `pg_class-table.csv`
- `pg_database-table.csv`
- `pg_locks-table.csv`
- `pg_namespace-table.csv`
- `pg_service.conf`
- `pg_settings-table.csv`
- `pg_stat_activity-table.csv`
- `pg_stat_all_Tables-table.csv`
- `pg_stat_all_indexes-table.csv`
- `pg_tablespace-table.csv`
- `pg_user-table.csv`
- `size-pgsql-data.txt`
- `size-pgsql-home.txt`
