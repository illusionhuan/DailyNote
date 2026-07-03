---
title: 数据库查询优化：SQL调优与EXPLAIN执行计划全解析
date: 2026-07-03
tags: [MySQL, 查询优化, EXPLAIN, SQL调优, 慢查询]
categories: [数据库优化]
description: 深入解析MySQL查询优化核心技术，包括EXPLAIN执行计划解读、慢查询日志分析、SQL改写技巧与常见反模式。
---

## 为什么需要查询优化？

数据库性能问题 80% 以上源于**低效的 SQL 查询**。一条写得不好的 SQL 可能从毫秒级退化到秒级甚至分钟级，直接影响用户体验和系统稳定性。

查询优化的核心思路：**减少扫描行数、减少回表次数、减少临时表和文件排序**。

## 慢查询日志

### 什么是慢查询日志？

慢查询日志（Slow Query Log）是 MySQL 提供的内置诊断工具，记录执行时间超过阈值的 SQL 语句。

### 如何开启慢查询日志？

```sql
-- 查看是否开启
SHOW VARIABLES LIKE 'slow_query_log';

-- 临时开启（重启失效）
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;           -- 超过1秒记录
SET GLOBAL log_queries_not_using_indexes = ON;  -- 记录未使用索引的查询

-- 永久开启，在 my.cnf 中配置
-- [mysqld]
-- slow_query_log = 1
-- slow_query_log_file = /var/log/mysql/slow.log
-- long_query_time = 1
-- log_queries_not_using_indexes = 1
```

### 如何分析慢查询日志？

MySQL 自带 `mysqldumpslow` 工具：

```bash
# 按执行时间排序，取前10条
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log

# 按查询次数排序
mysqldumpslow -s c -t 10 /var/log/mysql/slow.log

# 按返回行数排序
mysqldumpslow -s r -t 10 /var/log/mysql/slow.log
```

更强大的第三方工具 **pt-query-digest**（Percona Toolkit）：

```bash
pt-query-digest /var/log/mysql/slow.log > report.txt
```

输出报告包含：总执行时间、平均执行时间、执行次数、返回行数统计、SQL 指纹等，是生产环境慢查询分析的首选工具。

## EXPLAIN 执行计划详解

### 什么是 EXPLAIN？

`EXPLAIN` 是 MySQL 提供的查询分析工具，用于查看 SQL 语句的执行计划，了解 MySQL 如何处理你的查询。

```sql
EXPLAIN SELECT * FROM users WHERE age > 25;
```

### EXPLAIN 输出字段详解

| 字段 | 含义 | 关注重点 |
|------|------|----------|
| **id** | 查询序号 | 相同 id 从上往下执行，不同 id 值大的先执行 |
| **select_type** | 查询类型 | SIMPLE（简单查询）、PRIMARY（主查询）、SUBQUERY（子查询）、DERIVED（派生表） |
| **table** | 访问的表 | 表名或别名 |
| **type** | 访问类型 | **最重要字段**，决定查询效率 |
| **possible_keys** | 可能使用的索引 | 优化器考虑的候选索引 |
| **key** | 实际使用的索引 | NULL 表示未使用索引 |
| **key_len** | 索引使用长度 | 判断联合索引使用了几个列 |
| **ref** | 索引关联的列 | const（常量）、字段名（关联查询） |
| **rows** | 预估扫描行数 | 越小越好 |
| **filtered** | 过滤百分比 | 越大越好，100% 最佳 |
| **Extra** | 额外信息 | 包含重要优化提示 |

### type 访问类型（性能从好到差）

```
system > const > eq_ref > ref > range > index > ALL
```

| 类型 | 说明 | 示例 |
|------|------|------|
| **system** | 表只有一行（系统表） | 极少出现 |
| **const** | 主键或唯一索引等值查询 | `WHERE id = 1` |
| **eq_ref** | 连表查询中使用主键/唯一索引 | `JOIN` 中 `ON a.id = b.user_id` |
| **ref** | 非唯一索引等值查询 | `WHERE name = 'test'`（name 有普通索引） |
| **range** | 索引范围查询 | `WHERE age > 25`、`WHERE id IN (1,2,3)` |
| **index** | 全索引扫描 | 扫描整棵索引树 |
| **ALL** | 全表扫描 | **必须优化！** |

**优化目标**：至少达到 **range** 级别，最好是 **ref** 及以上。

### Extra 字段常见值

| Extra 值 | 含义 | 是否需要优化 |
|----------|------|-------------|
| **Using index** | 覆盖索引，无需回表 | 不需要（好事） |
| **Using where** | Server 层进行了过滤 | 看情况 |
| **Using index condition** | 索引下推（ICP） | 不需要（好事） |
| **Using temporary** | 使用临时表 | **需要优化** |
| **Using filesort** | 额外排序操作 | **需要优化** |
| **Using join buffer** | 使用连接缓冲 | 看情况 |

### EXPLAIN 实战示例

```sql
-- 示例表
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    amount DECIMAL(10,2),
    status TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status_created (status, created_at)
);

-- 示例1：全表扫描（需要优化）
EXPLAIN SELECT * FROM orders WHERE amount > 100;
-- type: ALL, key: NULL → 没有索引可用

-- 示例2：使用索引
EXPLAIN SELECT * FROM orders WHERE user_id = 1001;
-- type: ref, key: idx_user_id

-- 示例3：覆盖索引
EXPLAIN SELECT user_id, status FROM orders WHERE status = 1;
-- type: ref, key: idx_status_created, Extra: Using index

-- 示例4：联合索引最左前缀
EXPLAIN SELECT * FROM orders WHERE status = 1 AND created_at > '2026-01-01';
-- type: range, key: idx_status_created → 两个列都用上了
```

## SQL 改写优化技巧

### 避免 SELECT *

```sql
-- 反模式：查询所有列
SELECT * FROM orders WHERE user_id = 1001;

-- 优化：只查需要的列
SELECT id, amount, status FROM orders WHERE user_id = 1001;
```

**原因**：
1. 增加网络传输开销
2. 无法使用覆盖索引，必须回表
3. 表结构变更可能导致应用异常

### 避免在索引列上使用函数

```sql
-- 反模式：索引列上使用函数 → 索引失效
SELECT * FROM orders WHERE YEAR(created_at) = 2026;

-- 优化：改为范围查询
SELECT * FROM orders
WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';
```

```sql
-- 反模式：隐式类型转换
SELECT * FROM users WHERE phone = 13800138000;  -- phone 是 VARCHAR

-- 优化：类型匹配
SELECT * FROM users WHERE phone = '13800138000';
```

### 避免 LIKE 左模糊

```sql
-- 反模式：左模糊 → 索引失效
SELECT * FROM users WHERE name LIKE '%张';

-- 可接受：右模糊可以使用索引
SELECT * FROM users WHERE name LIKE '张%';

-- 更好：使用全文索引或搜索引擎
```

### 用 EXISTS 替代 IN（大子查询）

```sql
-- 反模式：大结果集的 IN 子查询
SELECT * FROM orders
WHERE user_id IN (SELECT id FROM users WHERE age > 25);

-- 优化：使用 EXISTS（MySQL 5.6+ 会自动优化，但 EXISTS 更可控）
SELECT * FROM orders o
WHERE EXISTS (SELECT 1 FROM users u WHERE u.id = o.user_id AND u.age > 25);
```

> **注意**：MySQL 5.6+ 引入了半连接优化，很多场景下 IN 和 EXISTS 性能差异不大。用 `EXPLAIN` 验证实际执行计划。

### 分页查询优化

```sql
-- 反模式：大偏移量分页
SELECT * FROM orders ORDER BY id LIMIT 1000000, 10;
-- MySQL 需要扫描 1000010 行，丢弃前 1000000 行

-- 优化方案1：延迟关联
SELECT o.* FROM orders o
INNER JOIN (SELECT id FROM orders ORDER BY id LIMIT 1000000, 10) t
ON o.id = t.id;
-- 子查询走覆盖索引，只回表 10 行

-- 优化方案2：游标分页（记住上次的最后一条 ID）
SELECT * FROM orders WHERE id > 1000000 ORDER BY id LIMIT 10;

-- 优化方案3：业务约束
-- 禁止跳转到第100页，只允许"加载更多"
```

### OR 改写为 UNION

```sql
-- 反模式：OR 导致索引失效
SELECT * FROM orders WHERE user_id = 1001 OR status = 1;
-- 如果两个字段分别有索引，MySQL 可能选择全表扫描

-- 优化：拆分为 UNION（两个字段都有独立索引时）
SELECT * FROM orders WHERE user_id = 1001
UNION
SELECT * FROM orders WHERE status = 1;
```

### 批量操作替代循环

```sql
-- 反模式：逐条插入
INSERT INTO orders (user_id, amount) VALUES (1, 100);
INSERT INTO orders (user_id, amount) VALUES (2, 200);
INSERT INTO orders (user_id, amount) VALUES (3, 300);

-- 优化：批量插入
INSERT INTO orders (user_id, amount) VALUES
(1, 100), (2, 200), (3, 300);
```

批量插入比逐条插入快 **5-10 倍**，因为减少了网络往返和事务开销。

## JOIN 优化

### 小表驱动大表

```sql
-- 假设 users 表 1万行，orders 表 1000万行
-- 好：小表驱动大表
SELECT * FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE u.age > 25;

-- MySQL 优化器通常会自动选择小表作为驱动表
-- 但可以通过 STRAIGHT_JOIN 强制指定驱动表
SELECT * FROM users u
STRAIGHT_JOIN orders o ON o.user_id = u.id
WHERE u.age > 25;
```

### JOIN 字段必须加索引

```sql
-- 确保被驱动表的关联字段有索引
-- orders 表的 user_id 必须有索引
ALTER TABLE orders ADD INDEX idx_user_id (user_id);
```

### 避免过多 JOIN

阿里巴巴开发规范建议：**JOIN 不超过 3 个表**。超过时考虑：
1. 在应用层拆分多次查询
2. 适当冗余字段（反范式设计）
3. 使用宽表（定时同步）

## ORDER BY 优化

### 利用索引避免排序

```sql
-- 有联合索引 (status, created_at)
-- 走索引，无需额外排序
SELECT * FROM orders WHERE status = 1 ORDER BY created_at;

-- Extra: Using index condition（无 Using filesort）
```

### filesort 的两种算法

当无法利用索引排序时，MySQL 使用 filesort：

| 算法 | 过程 | 适用场景 |
|------|------|----------|
| **单次传输排序** | 读取所需列 → 排序 → 直接输出 | 返回列总长度 < `max_length_for_sort_data`（默认 4096 字节） |
| **双次传输排序** | 读取排序字段和 ID → 排序 → 按 ID 回表读取 | 返回列总长度较大 |

```sql
-- 优化：减少排序字段，利用覆盖索引
-- 如果只需要 id 和 created_at
SELECT id, created_at FROM orders WHERE status = 1 ORDER BY created_at;
-- Extra: Using index（覆盖索引 + 索引排序）
```

### ORDER BY 优化要点

1. 利用联合索引的有序性
2. 排序方向一致（都是 ASC 或都是 DESC）
3. 减少排序的数据量（先过滤再排序）
4. 适当增大 `sort_buffer_size`

## GROUP BY 优化

```sql
-- 反模式：GROUP BY 产生临时表和排序
SELECT status, COUNT(*) FROM orders GROUP BY status;

-- 优化：确保 GROUP BY 的字段有索引
-- 联合索引 (status, created_at) 可以优化上面的查询
```

GROUP BY 优化原则与 ORDER BY 类似，核心是**利用索引的有序性避免临时表和文件排序**。

## COUNT 优化

```sql
-- 性能对比
SELECT COUNT(*) FROM orders;           -- InnoDB 会遍历最小的索引树
SELECT COUNT(1) FROM orders;           -- 与 COUNT(*) 性能相同
SELECT COUNT(id) FROM orders;          -- 同上（id 是主键）
SELECT COUNT(status) FROM orders;      -- 不统计 NULL 值
```

**COUNT(*) 与 COUNT(1) 在 InnoDB 中没有性能差异**，优化器会选择最小的索引树遍历。

大数据量下的优化方案：
1. **近似值**：`SHOW TABLE STATUS LIKE 'orders'`（InnoDB 是估算值）
2. **缓存计数**：用 Redis 或额外的计数表维护
3. **分页估算**：搜索引擎的"约 1000 条结果"

## 子查询 vs JOIN

```sql
-- 子查询
SELECT * FROM orders
WHERE user_id IN (SELECT id FROM users WHERE age > 25);

-- JOIN（通常更高效）
SELECT o.* FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE u.age > 25;
```

**经验法则**：
- MySQL 5.6+ 的半连接优化已大幅改善子查询性能
- 但 JOIN 通常仍比子查询更可控
- 用 EXPLAIN 对比两者的执行计划

## 查询优化清单

| 检查项 | 优化手段 |
|--------|----------|
| 全表扫描 | 添加合适的索引 |
| 索引失效 | 检查函数、隐式转换、左模糊 |
| Using filesort | 利用索引排序 |
| Using temporary | 优化 GROUP BY / DISTINCT |
| 回表过多 | 使用覆盖索引 |
| 大偏移量分页 | 延迟关联或游标分页 |
| SELECT * | 只查需要的列 |
| 大子查询 | 改写为 JOIN |
| 循环单条操作 | 批量操作 |
| 未使用索引的 JOIN | 被驱动表关联字段加索引 |
