---
title: MySQL性能调优：连接池配置、Buffer Pool与参数优化
date: 2026-07-03
tags: [MySQL, 性能调优, 连接池, Buffer Pool, 参数优化]
categories: [数据库优化]
description: 全面解析MySQL性能调优核心配置，涵盖连接池选型与参数、InnoDB Buffer Pool优化、关键系统参数调优与监控指标。
---

## MySQL 性能调优全景

MySQL 性能调优分为三个层次：

```
┌─────────────────────────────────────┐
│           应用层调优                  │  SQL 优化、索引设计、缓存策略
├─────────────────────────────────────┤
│           配置层调优                  │  连接池、Buffer Pool、日志参数
├─────────────────────────────────────┤
│           架构层调优                  │  读写分离、分库分表、缓存架构
└─────────────────────────────────────┘
```

本文聚焦**配置层调优**——不改代码，不改架构，通过合理的参数配置提升性能。

## 连接池

### 为什么需要连接池？

每次执行 SQL 都经历：建立 TCP 连接 → MySQL 认证 → 执行 SQL → 关闭连接。这个过程耗时约 **3-5ms**，在高并发下成为瓶颈。

连接池的作用：**复用连接，避免反复创建和销毁**。

```
无连接池：
请求1 → 建立连接 → 执行SQL → 关闭连接
请求2 → 建立连接 → 执行SQL → 关闭连接
请求3 → 建立连接 → 执行SQL → 关闭连接

有连接池：
初始化：创建 N 个连接放入池中
请求1 → 从池中取连接 → 执行SQL → 归还连接
请求2 → 从池中取连接 → 执行SQL → 归还连接
请求3 → 从池中取连接 → 执行SQL → 归还连接
```

### 主流连接池对比

| 连接池 | 性能 | 监控 | 稳定性 | 推荐度 |
|--------|------|------|--------|--------|
| **HikariCP** | 最高 | 基础 | 高 | ⭐⭐⭐⭐⭐ |
| Druid | 中等 | 最强 | 高 | ⭐⭐⭐⭐ |
| DBCP2 | 较低 | 中等 | 中 | ⭐⭐⭐ |
| C3P0 | 最低 | 低 | 低 | ⭐ |

**推荐**：
- 追求性能 → **HikariCP**（Spring Boot 2.x+ 默认）
- 需要 SQL 监控和防火墙 → **Druid**

### HikariCP 核心参数

```yaml
# Spring Boot 配置
spring:
  datasource:
    hikari:
      # 最小空闲连接数（默认 10）
      minimum-idle: 10
      # 最大连接池大小（默认 10）
      maximum-pool-size: 20
      # 连接超时时间（默认 30s）
      connection-timeout: 30000
      # 空闲连接最大存活时间（默认 10min）
      idle-timeout: 600000
      # 连接最大存活时间（默认 30min）
      max-lifetime: 1800000
      # 连接测试查询
      connection-test-query: SELECT 1
```

#### maximum-pool-size 怎么定？

**经验公式**：

```
最大连接数 = CPU 核心数 * 2 + 磁盘数
```

例如 4 核 CPU + 1 块磁盘 → `4 * 2 + 1 = 9`，取整为 **10**。

**实际建议**：
- 普通业务：**10-20**
- 高并发业务：**20-50**（不建议超过 50）
- MySQL 默认最大连接数 `max_connections = 151`，所有应用共享

> **连接数不是越大越好**：过多连接导致上下文切换频繁、内存占用高，反而降低性能。

#### 连接泄漏检测

```yaml
# HikariCP 泄漏检测
hikari:
  # 连接超过此时间未归还，打印泄漏日志（默认 0=不检测）
  leak-detection-threshold: 60000  # 60秒
```

日志输出：
```
WARNING: Connection leak detection triggered for connection xxx, stack trace follows
```

### Druid 连接池核心参数

```yaml
spring:
  datasource:
    druid:
      # 初始化连接数
      initial-size: 5
      # 最小空闲连接数
      min-idle: 5
      # 最大连接数
      max-active: 20
      # 获取连接最大等待时间
      max-wait: 3000
      # 空闲连接检测间隔
      time-between-eviction-runs-millis: 60000
      # 连接最小存活时间
      min-evictable-idle-time-millis: 300000
      # 监控页面
      stat-view-servlet:
        enabled: true
        url-pattern: /druid/*
        login-username: admin
        login-password: admin
```

### 连接池监控

#### HikariCP JMX 监控

```java
HikariPoolMXBean poolMXBean = dataSource.getHikariPoolMXBean();

System.out.println("活跃连接: " + poolMXBean.getActiveConnections());
System.out.println("空闲连接: " + poolMXBean.getIdleConnections());
System.out.println("总连接数: " + poolMXBean.getTotalConnections());
System.out.println("等待线程: " + poolMXBean.getThreadsAwaitingConnection());
```

#### Druid 内置监控

Druid 提供 Web 监控页面，包含：
- SQL 执行统计（执行次数、耗时、慢 SQL）
- 连接池状态（活跃、空闲、最大连接数）
- 数据源信息
- SQL 防火墙

## InnoDB Buffer Pool

### 什么是 Buffer Pool？

Buffer Pool 是 InnoDB 最重要的内存组件，用于**缓存磁盘上的数据页和索引页**。

```
┌─────────────────────────────────┐
│         Buffer Pool              │
│  ┌──────────┐  ┌──────────┐    │
│  │ 数据页    │  │ 索引页    │    │
│  │ (data     │  │ (index   │    │
│  │  pages)   │  │  pages)  │    │
│  └──────────┘  └──────────┘    │
│  ┌──────────┐  ┌──────────┐    │
│  │ 自适应哈希│  │ Change   │    │
│  │ 索引      │  │ Buffer   │    │
│  └──────────┘  └──────────┘    │
└─────────────────────────────────┘
         ↕ 读写（内存速度）
┌─────────────────────────────────┐
│         磁盘（数据文件）          │
└─────────────────────────────────┘
```

**查询流程**：
1. 查询数据时，先在 Buffer Pool 中查找
2. 命中 → 直接从内存返回（**内存读**，极快）
3. 未命中 → 从磁盘读取数据页到 Buffer Pool（**磁盘读**，慢）

### Buffer Pool 大小设置

```sql
-- 查看当前大小
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- 设置大小（在线修改，MySQL 5.7+）
SET GLOBAL innodb_buffer_pool_size = 8 * 1024 * 1024 * 1024;  -- 8GB

-- my.cnf 永久配置
-- innodb_buffer_pool_size = 8G
```

**设置原则**：
- **专用数据库服务器**：物理内存的 **60%-80%**
- **混合部署**：物理内存的 **50%** 左右
- **最小值**：至少 128MB

| 物理内存 | 建议 Buffer Pool |
|----------|-----------------|
| 4 GB | 2-3 GB |
| 8 GB | 5-6 GB |
| 16 GB | 10-12 GB |
| 32 GB | 20-24 GB |
| 64 GB | 40-50 GB |

### Buffer Pool 命中率

```sql
-- 查看 Buffer Pool 命中率
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';

-- 计算公式
-- 命中率 = 1 - (Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests)
-- 目标：> 99%

SELECT
    (1 - Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests) * 100 AS hit_rate
FROM (
    SELECT
        VARIABLE_VALUE AS Innodb_buffer_pool_reads
    FROM performance_schema.global_status
    WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads'
) a, (
    SELECT
        VARIABLE_VALUE AS Innodb_buffer_pool_read_requests
    FROM performance_schema.global_status
    WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests'
) b;
```

**命中率低于 99% 说明 Buffer Pool 太小**，需要增加内存。

### Buffer Pool 多实例

```sql
-- 查看实例数
SHOW VARIABLES LIKE 'innodb_buffer_pool_instances';

-- 设置实例数（my.cnf）
-- innodb_buffer_pool_instances = 8
```

**设置原则**：
- Buffer Pool ≥ 1GB 时，建议设置多个实例
- 实例数 = CPU 核心数（不超过 64）
- 每个实例独立管理自己的数据页，减少锁竞争

### Buffer Pool 预热

数据库重启后 Buffer Pool 为空，需要预热：

```sql
-- MySQL 5.7+ 支持 Buffer Pool 转储和恢复
-- 重启前：导出 Buffer Pool 中的页信息
SET GLOBAL innodb_buffer_pool_dump_now = ON;

-- 重启后：自动加载
SET GLOBAL innodb_buffer_pool_load_at_startup = ON;

-- 或手动加载
SET GLOBAL innodb_buffer_pool_load_now = ON;

-- 查看加载进度
SHOW STATUS LIKE 'Innodb_buffer_pool_load_status';
```

## InnoDB Log Buffer

### 什么是 Log Buffer？

Log Buffer 是 redo log 的内存缓冲区，定期刷写到磁盘。

```sql
-- 查看大小（默认 16MB）
SHOW VARIABLES LIKE 'innodb_log_buffer_size';

-- 设置（my.cnf）
-- innodb_log_buffer_size = 64M
```

**增大 Log Buffer 的好处**：
1. 减少磁盘写入频率
2. 大事务（如批量更新）可以将更多 redo log 缓存在内存中

**建议值**：
- 普通业务：**16-64MB**
- 大事务较多：**64-256MB**

## 关键系统参数

### 连接相关

```sql
-- 最大连接数（默认 151）
SHOW VARIABLES LIKE 'max_connections';
-- 建议：根据连接池数量 * 应用实例数 + 系统连接设置
-- 一般设为 500-2000

-- 查看历史最大连接数
SHOW GLOBAL STATUS LIKE 'Max_used_connections';

-- 连接超时（默认 28800s = 8h）
SHOW VARIABLES LIKE 'wait_timeout';
SHOW VARIABLES LIKE 'interactive_timeout';
-- 建议：300-600s，避免空闲连接占用资源
```

### 查询缓存

```sql
-- MySQL 8.0 已移除查询缓存
-- MySQL 5.7 及以下建议关闭（命中率低，锁粒度大）
SHOW VARIABLES LIKE 'query_cache_type';
-- 设为 OFF
```

### 排序与临时表

```sql
-- 排序缓冲区（每个连接独立，不能设太大）
SHOW VARIABLES LIKE 'sort_buffer_size';
-- 默认 256KB，建议 1-4MB

-- JOIN 缓冲区
SHOW VARIABLES LIKE 'join_buffer_size';
-- 默认 256KB，建议 1-4MB

-- 临时表大小限制
SHOW VARIABLES LIKE 'tmp_table_size';
SHOW VARIABLES LIKE 'max_heap_table_size';
-- 默认 16MB，建议 64-256MB
-- 超过此值的临时表使用磁盘（tmpdir）
```

### InnoDB IO 参数

```sql
-- InnoDB IO 容量（控制后台 IO 操作的吞吐量）
SHOW VARIABLES LIKE 'innodb_io_capacity';
SHOW VARIABLES LIKE 'innodb_io_capacity_max';

-- SSD 磁盘建议
-- innodb_io_capacity = 2000
-- innodb_io_capacity_max = 4000

-- HDD 磁盘建议
-- innodb_io_capacity = 200
-- innodb_io_capacity_max = 400

-- 刷脏页策略
SHOW VARIABLES LIKE 'innodb_max_dirty_pages_pct';
-- 建议 75（Buffer Pool 中脏页比例超过 75% 时强制刷盘）
```

### redo log 参数

```sql
-- redo log 文件大小
SHOW VARIABLES LIKE 'innodb_log_file_size';

-- redo log 文件数量
SHOW VARIABLES LIKE 'innodb_log_files_in_group';

-- 总大小 = innodb_log_file_size * innodb_log_files_in_group
-- 建议总大小能容纳 1 小时的写入量
-- SSD + 高并发：innodb_log_file_size = 1G, innodb_log_files_in_group = 2
```

### 刷盘策略

```sql
-- 控制事务提交时 redo log 的刷盘策略
SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';

-- 值 | 含义
--  1 | 每次提交都刷盘（最安全，默认值）
--  0 | 每秒刷盘（最快，可能丢失 1 秒数据）
--  2 | 每次提交写入 OS 缓存，每秒刷盘

-- 建议：
-- 数据安全要求高（金融）：1
-- 性能优先（日志类）：2
-- 极致性能（可接受数据丢失）：0
```

```sql
-- 控制 binlog 刷盘策略
SHOW VARIABLES LIKE 'sync_binlog';

-- 值 | 含义
--  0 | 由 OS 决定何时刷盘
--  1 | 每次提交都刷盘（最安全，配合 innodb_flush_log_at_trx_commit=1）
-- N | 每 N 次提交刷盘

-- 双1配置（最安全）：
-- innodb_flush_log_at_trx_commit = 1
-- sync_binlog = 1
```

### 双1配置 vs 性能配置

| 场景 | innodb_flush_log_at_trx_commit | sync_binlog | 安全性 | 性能 |
|------|-------------------------------|-------------|--------|------|
| **双1配置** | 1 | 1 | 最高 | 较低 |
| 性能优先 | 2 | 1 | 较高 | 较高 |
| 极致性能 | 0 | 0 | 最低 | 最高 |

**金融、支付、订单**：必须双1配置。
**日志、统计、缓存**：可以适当放宽。

## 慢查询参数

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = ON;

-- 慢查询阈值（默认 10s，建议 1s）
SET GLOBAL long_query_time = 1;

-- 记录未使用索引的查询
SET GLOBAL log_queries_not_using_indexes = ON;

-- 限制每分钟记录的未使用索引查询数（避免日志爆炸）
SET GLOBAL log_throttle_queries_not_using_indexes = 60;
```

## 性能监控指标

### 核心指标

```sql
-- QPS（每秒查询数）
SHOW GLOBAL STATUS LIKE 'Queries';

-- TPS（每秒事务数）
SHOW GLOBAL STATUS LIKE 'Com_commit';
SHOW GLOBAL STATUS LIKE 'Com_rollback';

-- 计算
-- QPS = Queries 差值 / 时间间隔
-- TPS = (Com_commit 差值 + Com_rollback 差值) / 时间间隔

-- 慢查询数量
SHOW GLOBAL STATUS LIKE 'Slow_queries';

-- 线程连接数
SHOW GLOBAL STATUS LIKE 'Threads_connected';  -- 当前连接数
SHOW GLOBAL STATUS LIKE 'Threads_running';     -- 当前活跃线程数
```

### InnoDB 指标

```sql
-- InnoDB 行锁等待
SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_waits';
SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_time';

-- InnoDB 缓冲池命中率
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read_requests';
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_reads';

-- InnoDB 页操作
SHOW GLOBAL STATUS LIKE 'Innodb_pages_read';
SHOW GLOBAL STATUS LIKE 'Innodb_pages_written';
```

### 推荐监控工具

| 工具 | 类型 | 特点 |
|------|------|------|
| **Prometheus + Grafana** | 开源 | 灵活强大，推荐 |
| Percona Monitoring | 开源 | 专为 MySQL 设计 |
| PMM (Percona Monitoring and Management) | 开源 | 一站式监控方案 |
| MySQL Enterprise Monitor | 商业 | Oracle 官方 |

## 参数调优 Checklist

| 检查项 | 默认值 | 建议值 | 说明 |
|--------|--------|--------|------|
| innodb_buffer_pool_size | 128MB | 物理内存 60-80% | 最重要的参数 |
| innodb_buffer_pool_instances | 8 | CPU 核心数 | 减少锁竞争 |
| max_connections | 151 | 500-2000 | 根据业务需求 |
| wait_timeout | 28800 | 300-600 | 及时释放空闲连接 |
| innodb_flush_log_at_trx_commit | 1 | 1（安全）/2（性能） | 数据安全 vs 性能 |
| sync_binlog | 1 | 1（安全）/N（性能） | 配合刷盘策略 |
| innodb_io_capacity | 200 | SSD: 2000 | 匹配磁盘性能 |
| sort_buffer_size | 256KB | 1-4MB | 每连接独立分配 |
| innodb_log_file_size | 48MB | 1GB | 减少 redo log 切换 |
| long_query_time | 10 | 1 | 及时发现慢查询 |
