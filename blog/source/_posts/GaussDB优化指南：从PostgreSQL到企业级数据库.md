---
title: GaussDB优化指南：从PostgreSQL到企业级数据库
date: 2026-07-04
tags: [GaussDB, openGauss, 查询优化, 性能调优, 信创]
categories: [数据库优化]
description: 全面解析华为GaussDB数据库优化策略，涵盖与PostgreSQL的差异、Ustore存储引擎、MOT内存表、NUMA优化、SQL Hints与执行计划控制。
---

## 1. GaussDB 与 PostgreSQL 的关系

### 1.1 GaussDB 产品线概览

华为 GaussDB 并非单一产品，而是一个数据库家族：

```
GaussDB 产品家族
├── GaussDB(for MySQL)      -- 云原生分布式，兼容 MySQL 协议
├── GaussDB(openGauss)      -- 基于 openGauss 内核，信创主流
│   ├── 单机版
│   ├── 主备版（一主多备）
│   └── 分布式版（Sharding）
└── GaussDB(DWS)            -- 数据仓库，面向 OLAP
```

**本文聚焦 GaussDB(openGauss)**——这是国内信创项目中替换 Oracle/PostgreSQL 的主力方案。

### 1.2 与 PostgreSQL 的兼容性和差异

openGauss 从 PostgreSQL 9.2 内核 fork 而来，但经过大量改造：

| 方面 | PostgreSQL | GaussDB(openGauss) |
|------|-----------|-------------------|
| 内核版本 | 9.2 → 17 持续演进 | 基于 PG 9.2，独立演进 |
| 进程/线程模型 | 多进程（每连接一个进程） | 多线程（线程池） |
| 存储引擎 | Heap only | ASTORE / Ustore / MOT |
| MVCC | 多版本堆 + VACUUM | ASTORE 类似 PG；Ustore 原地更新 |
| 优化器 | PostgreSQL 原生 | 增强 + SQL Hints |
| NUMA 支持 | 有限 | 原生 NUMA 感知 |

### 1.3 为什么选择 GaussDB

- **信创合规**：国产化替代的核心选型，适配主流信创硬件（鲲鹏、飞腾）
- **线程模型**：相比 PG 的多进程，线程模型在高并发下内存开销更低
- **Ustore 引擎**：原地更新，避免 PG 的表膨胀问题
- **NUMA 深度优化**：鲲鹏服务器多核架构下的性能保障
- **企业级特性**：WDR 诊断报告、SQL Hints、内置安全加固

---

## 2. 存储引擎选择

GaussDB 提供三种存储引擎，这是它与 PostgreSQL 最大的架构差异。

### 2.1 ASTORE（Append-Only Store）

类似 PostgreSQL 默认的 Heap 存储，使用追加写方式实现 MVCC：

```
ASTORE 写入流程（类似 PG Heap）:
┌──────────┐     UPDATE     ┌──────────┐
│ 旧版本行  │ ──────────────→│ 新版本行  │
│ (被标记为 │               │ (追加写入 │
│  旧版本)  │               │  当前版本)│
└──────────┘               └──────────┘
       │
       └── 需要 VACUUM 清理旧版本
```

适用场景：读多写少、兼容 PostgreSQL 习惯的场景。

### 2.2 Ustore（In-place Update Store）

Ustore 是 GaussDB 的核心差异化特性——原地更新，大幅减少表膨胀：

```
Ustore 写入流程（原地更新）:
┌──────────┐     UPDATE     ┌──────────┐
│ 原始行位置 │ ──────────────→│ 同一位置  │
│          │               │ 直接覆盖  │
└──────────┘               └──────────┘
       │
       └── 旧版本写入 UNDO 空间（可回滚，自动清理）
```

启用 Ustore：

```sql
-- 建表时指定
CREATE TABLE orders (
    order_id    BIGINT PRIMARY KEY,
    user_id     BIGINT,
    amount      DECIMAL(12,2),
    status      VARCHAR(20),
    created_at  TIMESTAMP DEFAULT now()
) WITH (STORAGE_TYPE = USTORE);

-- 查看表的存储引擎
SELECT relname, reloptions FROM pg_class WHERE relname = 'orders';

-- 设置全局默认引擎（需重启）
ALTER SYSTEM SET default_storage_type = 'ustore';
```

Ustore 关键参数：

```sql
-- UNDO 空间大小（类似 Oracle 的 UNDO 表空间）
ALTER SYSTEM SET undo_space_limit_size = 10GB;

-- UNDO 保留时间（秒），控制旧版本保留多久
ALTER SYSTEM SET ustore_undo_limit_size = 1024;

-- UNDO 回收策略
ALTER SYSTEM SET ustore_attr = 'ustore_attr_check_enable=on';
```

### 2.3 MOT（Memory-Optimized Table）

纯内存存储引擎，数据完全驻留内存，面向极致 OLTP 场景：

```sql
-- 创建 MOT 表
CREATE FOREIGN TABLE session_cache (
    session_id  VARCHAR(64) PRIMARY KEY,
    user_id     BIGINT,
    login_time  TIMESTAMP,
    data        TEXT
) USING MOT;

-- MOT 不支持所有 SQL，限制：
-- - 不支持外键
-- - 不支持 GIN/GiST 索引
-- - 不支持大对象（LOB）
-- - 仅支持行存，不支持列存
```

### 2.4 存储引擎选择策略

```
选择决策树：

业务特征？
├── 写入密集（UPDATE 频繁）
│   ├── 数据量小、可全内存  → MOT
│   └── 数据量大、需持久化  → Ustore
├── 读多写少
│   ├── 需要兼容 PG 行为    → ASTORE
│   └── 需要减少膨胀        → Ustore
└── 混合负载
    └── 核心热表用 Ustore，冷数据用 ASTORE
```

| 特性 | ASTORE | Ustore | MOT |
|------|--------|--------|-----|
| 写入方式 | 追加写 | 原地更新 | 内存原地更新 |
| 表膨胀 | 有（需 VACUUM） | 极小 | 无 |
| 持久化 | 是 | 是 | 是（WAL + 检查点） |
| 索引类型 | 全部支持 | 全部支持 | 仅 T-Tree / HASH |
| 适用场景 | 通用 OLTP | 频繁 UPDATE | 极致低延迟 |

---

## 3. 执行计划与 SQL Hints

### 3.1 EXPLAIN ANALYZE

GaussDB 的执行计划输出与 PostgreSQL 类似，但有扩展：

```sql
EXPLAIN ANALYZE
SELECT o.order_id, u.username, o.amount
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.created_at > '2026-01-01'
  AND o.status = 'PAID'
ORDER BY o.amount DESC
LIMIT 100;
```

输出解读（关注 GaussDB 特有字段）：

```
Limit  (cost=100.00..102.50 rows=100 width=48) (actual time=1.234..1.567 rows=100 loops=1)
  ->  Sort  (cost=100.00..150.00 rows=5000 width=48) (actual time=1.234..1.500 rows=100 loops=1)
        Sort Key: o.amount DESC
        Sort Method: top-N heapsort  Memory: 32kB
        ->  Hash Join  (cost=50.00..200.00 rows=5000 width=48) (actual time=0.500..1.200 rows=4800 loops=1)
              ->  Index Scan using idx_orders_created on orders o  (cost=0.42..120.00 rows=5000 width=24)
                    Filter: (status = 'PAID')        -- 注意：过滤条件未走索引
                    Rows Removed by Filter: 3200     -- GaussDB 扩展：显示被过滤的行数
              ->  Hash  (cost=30.00..30.00 rows=2000 width=28)
                    ->  Seq Scan on users u  (cost=0.00..30.00 rows=2000 width=28)
```

### 3.2 SQL Hints（GaussDB 特有）

这是 GaussDB 相比 PostgreSQL 最实用的优化工具——直接在 SQL 中控制执行计划，无需改配置。

**索引 Hint：**

```sql
-- 强制使用指定索引
SELECT /*+ IndexScan(orders idx_orders_status) */
    order_id, amount
FROM orders
WHERE status = 'PAID'
  AND created_at > '2026-01-01';

-- 强制全表扫描（绕过错误索引选择）
SELECT /*+ SeqScan(orders) */
    order_id, amount
FROM orders
WHERE status = 'PAID';

-- 强制 Bitmap 索引扫描
SELECT /*+ BitmapScan(orders idx_orders_status) */
    order_id, amount
FROM orders
WHERE status IN ('PAID', 'SHIPPED');
```

**连接方式 Hint：**

```sql
-- 强制使用 Hash Join
SELECT /*+ HashJoin(orders users) */
    o.order_id, u.username
FROM orders o
JOIN users u ON o.user_id = u.user_id;

-- 强制使用 Nested Loop（小表驱动大表时）
SELECT /*+ NestLoop(users orders) */
    u.username, o.amount
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE u.user_id = 12345;

-- 强制使用 Merge Join（已排序数据）
SELECT /*+ MergeJoin(orders users) */
    o.order_id, u.username
FROM orders o
JOIN users u ON o.user_id = u.user_id;
```

**并行查询 Hint：**

```sql
-- 设置并行度
SELECT /*+ Parallel(orders 4) */
    status, COUNT(*), SUM(amount)
FROM orders
GROUP BY status;
```

**Set Hint（会话级参数覆盖）：**

```sql
-- 在单条 SQL 中临时调整参数，不影响其他查询
SELECT /*+ Set(enable_seqscan off) Set(work_mem '256MB') */
    o.order_id, u.username, o.amount
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.created_at > '2026-01-01';
```

### 3.3 实战：用 Hints 解决优化器选错索引

场景：`orders` 表有 `idx_orders_created` 和 `idx_orders_status` 两个索引，但优化器在 `status = 'PAID'` 条件下错误选择了 `idx_orders_created`，导致大量回表。

```sql
-- 问题 SQL：优化器选错索引，执行 3.2 秒
SELECT order_id, user_id, amount
FROM orders
WHERE status = 'PAID'
  AND created_at > '2026-06-01';

-- 方案 1：强制使用正确的索引（推荐）
SELECT /*+ IndexScan(orders idx_orders_status) */
    order_id, user_id, amount
FROM orders
WHERE status = 'PAID'
  AND created_at > '2026-06-01';
-- 执行时间：0.15 秒

-- 方案 2：创建复合索引，一劳永逸
CREATE INDEX idx_orders_status_created ON orders(status, created_at);
-- 执行时间：0.08 秒（不需要 Hint 了）
```

---

## 4. NUMA 感知优化

### 4.1 NUMA 架构的影响

鲲鹏服务器通常是多 NUMA 节点架构，跨 NUMA 内存访问延迟是本地访问的 1.5-2 倍：

```
典型双路鲲鹏服务器 NUMA 布局：

NUMA Node 0                    NUMA Node 1
┌─────────────────┐           ┌─────────────────┐
│ CPU 0-63        │           │ CPU 64-127      │
│ Local Memory    │  ← 慢 →   │ Local Memory    │
│ 128GB           │  跨节点   │ 128GB           │
└─────────────────┘           └─────────────────┘
  本地访问: ~80ns               本地访问: ~80ns
  跨节点: ~140ns               跨节点: ~140ns
```

### 4.2 GaussDB NUMA 配置

```sql
-- 启用 NUMA 感知（鲲鹏服务器推荐开启）
ALTER SYSTEM SET enable_numa = on;

-- 查看当前 NUMA 配置
SHOW enable_numa;

-- 线程池配置（与 NUMA 配合）
ALTER SYSTEM SET thread_pool_attr = '16, 4, (cpubind:0-63)(cpubind:64-127)';
-- 格式：'线程数, 组数, (绑定策略)'
```

### 4.3 NUMA 绑核实战

```sql
-- 查看当前数据库进程的 NUMA 分布
SELECT * FROM pg_stat_activity;

-- 手动绑定后端线程到 NUMA 节点
-- 在 postgresql.conf 中配置：
-- thread_pool_attr = '32, 2, (cpubind:0-31)(cpubind:32-63)'
-- 表示：32 个工作线程，分为 2 组，分别绑定到不同 NUMA 节点

-- 验证绑定效果
SELECT nodeid, count(*)
FROM pg_thread_wait_status
GROUP BY nodeid;
```

---

## 5. 关键参数调优

### 5.1 内存参数

```sql
-- 共享缓冲区（类似 PG 的 shared_buffers）
-- 建议：物理内存的 25%-40%
ALTER SYSTEM SET shared_buffers = '8GB';

-- 列存缓冲区（GaussDB 特有，列存表使用）
ALTER SYSTEM SET cstore_buffers = '2GB';

-- 工作内存（排序、Hash 操作用）
-- 每个连接独立分配，注意总消耗 = work_mem × 并发数
ALTER SYSTEM SET work_mem = '64MB';

-- 维护操作内存（VACUUM、CREATE INDEX 等）
ALTER SYSTEM SET maintenance_work_mem = '1GB';

-- 内存表引擎缓冲区（MOT 使用）
ALTER SYSTEM SET mot_global_memory = '4GB';
ALTER SYSTEM SET mot_session_memory = '128MB';
```

### 5.2 连接与线程

```sql
-- 最大连接数（线程模型，比 PG 进程模型更省资源）
-- GaussDB 可以比同配置 PG 支持更多连接
ALTER SYSTEM SET max_connections = 1000;

-- 线程池（GaussDB 特有，替代 PG 的 per-connection 进程模型）
-- 格式：'线程数, 组数, (绑定策略)'
ALTER SYSTEM SET thread_pool_attr = '64, 8, (cpubind:0-7)(cpubind:8-15)...';

-- 优雅关闭等待时间
ALTER SYSTEM SET thread_pool_graceful_wait = 30;
```

### 5.3 WAL 与持久化

```sql
-- 同步提交（生产环境建议 on，对性能有约 5% 影响）
ALTER SYSTEM SET synchronous_commit = on;

-- WAL 级别（逻辑复制需要 logical，否则 replica 足够）
ALTER SYSTEM SET wal_level = replica;

-- WAL 缓冲区
ALTER SYSTEM SET wal_buffers = '64MB';
```

### 5.4 Ustore 专用参数

```sql
-- UNDO 空间总限制
ALTER SYSTEM SET undo_space_limit_size = 10GB;

-- 单事务 UNDO 限制
ALTER SYSTEM SET ustore_undo_limit_size = 2048;

-- UNDO 回收间隔（毫秒）
ALTER SYSTEM SET ustore_attr = 'undo_recycle_enable=on';
```

---

## 6. 监控与诊断工具

### 6.1 pg_stat_statements（与 PG 一致）

```sql
-- 确保已加载
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top 10 慢 SQL（按总执行时间排序）
SELECT
    queryid,
    calls,
    round(total_exec_time::numeric, 2) AS total_time_ms,
    round(mean_exec_time::numeric, 2) AS avg_time_ms,
    rows,
    round((shared_blks_hit::numeric / NULLIF(shared_blks_hit + shared_blks_read, 0)) * 100, 2) AS cache_hit_pct,
    left(query, 80) AS query_preview
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 重置统计
SELECT pg_stat_statements_reset();
```

### 6.2 GS_STAT 视图（GaussDB 扩展）

```sql
-- 查看锁等待信息
SELECT
    pid,
    wait_event_type,
    wait_event,
    state,
    left(query, 60) AS query
FROM pg_stat_activity
WHERE wait_event IS NOT NULL AND state = 'active';

-- 查看表级别的 IO 统计
SELECT
    relname,
    seq_scan, seq_tup_read,
    idx_scan, idx_tup_fetch,
    n_tup_ins, n_tup_upd, n_tup_del,
    n_live_tup, n_dead_tup,
    round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;
```

### 6.3 WDR 诊断报告

WDR（Workload Diagnosis Report）是 GaussDB 特有的诊断工具，可生成 HTML 格式的性能分析报告：

```sql
-- 1. 启用 WDR 快照（需 superuser）
ALTER SYSTEM SET enable_wdr_snapshot = on;

-- 2. 手动创建快照
SELECT create_wdr_snapshot();

-- 3. 生成两个快照之间的对比报告
-- 快照信息存储在 snapshot 表中
SELECT * FROM snapshot.snapshot LIMIT 10;

-- 4. 通过命令行生成 HTML 报告
-- gs_wdr -i <snapshot_id_start> -e <snapshot_id_end> -o report.html
```

### 6.4 慢 SQL 诊断流程

```
慢 SQL 诊断流程：

1. 发现问题
   └── pg_stat_statements Top N

2. 分析执行计划
   └── EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <SQL>
   └── 关注：SeqScan 大表、Nested Loop 驱动表错误、sort 外存

3. 检查统计信息
   └── ANALYZE <table>;  -- 更新统计信息
   └── pg_stats 查看列的 ndistinct / most_common_vals

4. 使用 Hints 微调
   └── IndexScan / HashJoin / Set(work_mem)
   └── 验证效果后固化为索引或参数

5. 持续监控
   └── WDR 报告对比优化前后
```

实战诊断示例：

```sql
-- 步骤 1：找到疑似慢 SQL
SELECT queryid, calls, mean_exec_time, query
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- 平均超过 1 秒
ORDER BY mean_exec_time DESC
LIMIT 5;

-- 步骤 2：分析执行计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE user_id = 12345 AND status = 'PENDING';

-- 步骤 3：更新统计信息
ANALYZE orders;

-- 步骤 4：如果优化器仍选错，用 Hint 干预
SELECT /*+ IndexScan(orders idx_orders_user_status) */
    * FROM orders
WHERE user_id = 12345 AND status = 'PENDING';

-- 步骤 5：如果效果好，创建合适的索引
CREATE INDEX CONCURRENTLY idx_orders_user_status
ON orders(user_id) WHERE status = 'PENDING';
```

---

## 7. GaussDB vs PostgreSQL vs MySQL 优化差异总结

| 维度 | PostgreSQL | GaussDB(openGauss) | MySQL(InnoDB) |
|------|-----------|-------------------|---------------|
| **存储引擎** | Heap only | ASTORE / Ustore / MOT | InnoDB / MyISAM / ... |
| **MVCC 实现** | Heap 追加写 + VACUUM | ASTORE 类 PG；Ustore UNDO 段 | Undo Log + Purge |
| **表膨胀处理** | VACUUM（可能延迟） | Ustore 几乎无膨胀 | 自动 Purge |
| **索引类型** | B-tree / GIN / GiST / BRIN / Hash | B-tree / GIN / GiST / Hash / PSort | B-tree / Hash / Full-text |
| **列存** | 需扩展（cstore_fdw） | 原生支持（PSort 列存索引） | 不支持（需 OLAP 引擎） |
| **执行计划控制** | 仅参数级（enable_seqscan 等） | SQL Hints（IndexScan/HashJoin/Set） | Optimizer Hints（不同语法） |
| **进程模型** | 多进程（fork per connection） | 多线程（线程池） | 多线程 |
| **NUMA 支持** | 有限（PG 16+ 改善） | 原生 enable_numa + 绑核 | 有限 |
| **内存表** | 不支持 | MOT 引擎（纯内存 OLTP） | MEMORY 引擎（已废弃） |
| **慢 SQL 诊断** | pg_stat_statements + auto_explain | pg_stat_statements + WDR 报告 | slow_log + Performance Schema |
| **连接管理** | 连接池（pgbouncer 外挂） | 内置线程池 | 内置线程池 |
| **参数调整粒度** | 数据库/用户/会话级 | 数据库/用户/会话级 + Hint 级 | 全局/会话级 |

### 优化策略选择速查

```
如果你来自 PostgreSQL：
├── VACUUM 问题严重 → 考虑迁移到 Ustore 引擎
├── 需要控制执行计划 → 使用 SQL Hints（比 PG 的参数控制更灵活）
├── 高并发连接多 → 享受线程池红利，无需 pgbouncer
└── NUMA 硬件 → 开启 enable_numa 配合绑核

如果你来自 MySQL：
├── 需要复杂查询能力 → GaussDB 优化器更强，窗口函数/CTE 更完整
├── 需要列存分析 → GaussDB 原生 PSort 列存
├── 需要信创合规 → GaussDB 是首选
└── 担心迁移成本 → openGauss 提供 MySQL 兼容模式
```

---

**总结**：GaussDB 的优化核心在于三大差异化能力——Ustore 解决存储膨胀、SQL Hints 精准控制执行计划、NUMA 感知释放多核性能。掌握这三点，就能在信创场景下发挥出 GaussDB 相比 PostgreSQL 和 MySQL 的真正优势。
