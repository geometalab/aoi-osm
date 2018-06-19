# ALTER SYSTEM config for PostgreSQL here
# recommended: use https://pgtune.leopard.in.ua/

# DB Version: 10
# OS Type: linux
# DB Type: web
# Total Memory (RAM): 6 GB
# CPUs num: 2
# Hard drive type: ssd

ALTER SYSTEM SET
 max_connections = '200';
ALTER SYSTEM SET
 shared_buffers = '1536MB';
ALTER SYSTEM SET
 effective_cache_size = '4608MB';
ALTER SYSTEM SET
 maintenance_work_mem = '384MB';
ALTER SYSTEM SET
 checkpoint_completion_target = '0.7';
ALTER SYSTEM SET
 wal_buffers = '16MB';
ALTER SYSTEM SET
 default_statistics_target = '100';
ALTER SYSTEM SET
 random_page_cost = '1.1';
ALTER SYSTEM SET
 effective_io_concurrency = '200';
ALTER SYSTEM SET
 work_mem = '7864kB';
ALTER SYSTEM SET
 min_wal_size = '1GB';
ALTER SYSTEM SET
 max_wal_size = '2GB';
ALTER SYSTEM SET
 max_worker_processes = '2';
ALTER SYSTEM SET
 max_parallel_workers_per_gather = '1';
ALTER SYSTEM SET
 max_parallel_workers = '2';
