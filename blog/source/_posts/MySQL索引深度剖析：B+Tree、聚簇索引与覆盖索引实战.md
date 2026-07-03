---
title: MySQL索引深度剖析：B+Tree、聚簇索引与覆盖索引实战
date: 2026-07-03
tags: [MySQL, 索引, B+Tree, 聚簇索引, 覆盖索引, InnoDB]
categories: [数据库优化]
description: 深入剖析MySQL索引底层数据结构B+Tree、聚簇索引与非聚簇索引的区别、覆盖索引原理、索引下推机制及索引优化实战。
---

## 什么是索引？

索引是帮助 MySQL **高效获取数据的有序数据结构**。可以类比为书的目录——没有目录时需要逐页翻找，有目录则直接定位页码。

索引的本质：**用额外的存储空间和写入开销，换取查询速度的提升**。

## 为什么选择 B+Tree？

### 常见数据结构对比

| 数据结构 | 查询 | 插入/删除 | 适用场景 |
|----------|------|-----------|----------|
| 二叉搜索树 | O(log n) | O(log n) | 数据量小，退化为链表时 O(n) |
| AVL 树 / 红黑树 | O(log n) | O(log n) | 树高较高，磁盘 IO 多 |
| B 树 | O(log n) | O(log n) | 非叶子节点也存数据，单节点存的 key 少 |
| **B+ 树** | O(log n) | O(log n) | **MySQL InnoDB 的选择** |

### B+Tree 的核心特性

```
         [10 | 20 | 30]              ← 非叶子节点（只存 key）
        /    |    |    \
  [1,5]  [10,15] [20,25] [30,35]     ← 叶子节点（存 key + data）
    ←→      ←→      ←→      ←→      ← 叶子节点之间用双向链表连接
```

1. **非叶子节点只存 key，不存数据**：每个节点能容纳更多 key，树更矮，IO 次数更少
2. **叶子节点存所有数据**：查询任何数据都要走到叶子节点，查询性能稳定
3. **叶子节点用双向链表连接**：支持高效的范围查询和排序
4. **树高通常 2-4 层**：千万级数据 3 层 B+Tree 即可，每次查询 3 次磁盘 IO

### B+Tree 的查询过程

```sql
SELECT * FROM users WHERE id = 15;
```

```
第1次IO：读根节点 [10 | 20 | 30] → 15 在 10~20 之间
第2次IO：读中间节点 [10, 15] → 找到 15
第3次IO：读叶子节点 → 获取完整数据行
```

**3 次磁盘 IO 就能从千万级数据中找到目标记录**，这就是索引的威力。

## 聚簇索引与非聚簇索引

### 聚簇索引（Clustered Index）

InnoDB 的**主键索引就是聚簇索引**，叶子节点存储的是**完整的数据行**。

```
主键索引（聚簇索引）B+Tree：
         [10 | 20 | 30]
        /    |    |    \
  [id=1] [id=10] [id=20] [id=30]  ← 叶子节点直接存储完整行数据
  row     row     row     row
```

**特点**：
- 一张表**只能有一个**聚簇索引（数据只能按一种方式物理排序）
- InnoDB 选择主键作为聚簇索引
- 没有主键时，选择第一个非空唯一索引
- 都没有时，InnoDB 自动生成一个隐藏的 ROW_ID 作为聚簇索引

### 非聚簇索引（Secondary Index）

除主键索引外的所有索引都是非聚簇索引（二级索引），叶子节点存储的是**主键值**。

```
二级索引 idx_name B+Tree：
         ["Bob" | "John" | "Tom"]
        /       |        |       \
  ["Alice",1] ["Bob",2] ["John",3] ["Tom",4]  ← 叶子节点存 name + 主键 id
```

### 回表查询

```sql
-- 有索引 idx_name(name)
SELECT * FROM users WHERE name = 'Bob';
```

查询过程：
1. 在 `idx_name` 的 B+Tree 中找到 `name = 'Bob'`，获取主键 `id = 2`
2. **回表**：拿着 `id = 2` 去主键索引（聚簇索引）中查找完整行数据

```
idx_name B+Tree → 找到 id=2 → 主键索引 B+Tree → 找到完整行
     第1次IO            →           第2-3次IO
```

**回表的代价**：额外的磁盘 IO。如果查询返回 1000 行，可能需要 1000 次回表。

### 如何避免回表？

使用**覆盖索引**。

## 覆盖索引

### 什么是覆盖索引？

当查询所需的**所有列都在索引中**时，不需要回表，直接从索引中返回数据。这就是覆盖索引。

```sql
-- 有联合索引 idx_name_age(name, age)

-- 覆盖索引：查询的列都在索引中
EXPLAIN SELECT name, age FROM users WHERE name = 'Bob';
-- Extra: Using index ✅

-- 非覆盖索引：需要回表查 email
EXPLAIN SELECT name, age, email FROM users WHERE name = 'Bob';
-- Extra: NULL（需要回表）
```

### 覆盖索引的设计策略

```sql
-- 频繁查询：SELECT user_id, status FROM orders WHERE user_id = ?
-- 设计覆盖索引
ALTER TABLE orders ADD INDEX idx_user_status (user_id, status);
```

**覆盖索引的好处**：
1. 减少回表 IO，查询速度大幅提升
2. 减少对主键索引的访问压力
3. 随机 IO 变为顺序 IO

### 覆盖索引的局限

1. 联合索引列数有限（建议不超过 5 个）
2. 索引占用更多存储空间
3. 写入性能略有下降（维护更多索引）

## 索引下推（Index Condition Pushdown）

### 什么是索引下推？

索引下推（ICP，Index Condition Pushdown）是 MySQL 5.6 引入的优化：**在索引遍历过程中，对索引包含的字段做判断，提前过滤掉不满足条件的记录，减少回表次数**。

```sql
-- 联合索引 idx_name_age(name, age)
SELECT * FROM users WHERE name LIKE '张%' AND age > 25;
```

### 无 ICP（MySQL 5.6 之前）

```
1. 存储引擎用索引找到所有 name LIKE '张%' 的记录 → 回表
2. 将完整行返回给 Server 层
3. Server 层过滤 age > 25
```

问题：即使 age 不满足条件，也回表了。

### 有 ICP（MySQL 5.6+）

```
1. 存储引擎用索引找到所有 name LIKE '张%' 的记录
2. 在索引中直接判断 age > 25，不满足的跳过
3. 只对满足条件的记录回表
```

**EXPLAIN 中体现为 Extra: Using index condition**。

### ICP 的适用条件

1. 只适用于**二级索引**（非聚簇索引）
2. 只适用于 `range`、`ref`、`eq_ref`、`ref_or_null` 类型的访问
3. 不适用于聚簇索引（主键索引已经包含完整数据）

## 索引合并（Index Merge）

### 什么是索引合并？

当查询条件涉及多个独立索引时，MySQL 可能对多个索引的结果做交集或并集。

```sql
-- 有 idx_user_id(user_id) 和 idx_status(status)
SELECT * FROM orders WHERE user_id = 1001 OR status = 1;
```

```
Index Merge (Union):
1. 用 idx_user_id 找到 user_id = 1001 的记录
2. 用 idx_status 找到 status = 1 的记录
3. 合并两个结果集（去重）
4. 回表获取完整数据
```

### EXPLAIN 中的体现

```
type: index_merge
key: idx_user_id,idx_status
Extra: Using union(idx_user_id, idx_status)
```

### 索引合并的类型

| 类型 | 条件 | 说明 |
|------|------|------|
| **Union** | OR | 多个索引结果取并集 |
| **Intersect** | AND | 多个索引结果取交集 |
| **Sort-Union** | OR + 范围 | 先排序再取并集 |

### 索引合并的局限

索引合并是优化器的**兜底策略**，不代表查询已经最优。出现索引合并时，应考虑：
1. 是否可以设计联合索引替代多个单列索引
2. 索引合并的回表开销可能仍然很大

## 索引设计实战

### 场景1：高频查询优化

```sql
-- 高频查询
SELECT id, user_id, amount, status
FROM orders
WHERE status = 1 AND user_id = 1001
ORDER BY created_at DESC
LIMIT 20;

-- 最佳索引：覆盖索引 + 排序
ALTER TABLE orders ADD INDEX idx_status_user_created (status, user_id, created_at);
-- status 等值 → user_id 等值 → created_at 排序
-- Extra: Using index（覆盖索引，无回表，无 filesort）
```

### 场景2：范围查询优化

```sql
-- 查询
SELECT * FROM orders
WHERE user_id = 1001 AND created_at > '2026-01-01' AND status = 1;

-- 索引设计：等值在前，范围在后
ALTER TABLE orders ADD INDEX idx_user_status_created (user_id, status, created_at);
-- user_id 等值 → status 等值 → created_at 范围
```

### 场景3：分页查询优化

```sql
-- 深分页查询
SELECT * FROM orders ORDER BY id LIMIT 1000000, 10;

-- 利用覆盖索引 + 延迟关联
SELECT o.* FROM orders o
INNER JOIN (SELECT id FROM orders ORDER BY id LIMIT 1000000, 10) t
ON o.id = t.id;
-- 子查询走覆盖索引（主键），只回表 10 行
```

### 场景4：统计查询优化

```sql
-- 统计查询
SELECT user_id, COUNT(*) FROM orders WHERE status = 1 GROUP BY user_id;

-- 覆盖索引
ALTER TABLE orders ADD INDEX idx_status_user (status, user_id);
-- Extra: Using index（无需回表即可完成统计）
```

## 索引失效的 10 种场景

| 场景 | 示例 | 原因 |
|------|------|------|
| 对索引列使用函数 | `WHERE YEAR(created_at) = 2026` | 索引存的是原值，不是函数结果 |
| 隐式类型转换 | `WHERE phone = 13800138000`（phone 是 VARCHAR） | 需要对每行做类型转换 |
| 左模糊查询 | `WHERE name LIKE '%张'` | B+Tree 按前缀有序，左模糊无法定位 |
| OR 连接无索引列 | `WHERE user_id = 1 OR remark = 'test'` | remark 无索引，被迫全表扫描 |
| 联合索引不满足最左前缀 | 索引 (a,b,c)，`WHERE b = 1` | 跳过了 a |
| NOT IN / NOT EXISTS | `WHERE status NOT IN (1,2)` | 优化器可能选择全表扫描 |
| IS NULL / IS NOT NULL | `WHERE deleted_at IS NOT NULL` | 取决于 NULL 值比例 |
| != 或 <> | `WHERE status != 1` | 不等于条件通常不走索引 |
| 数据量小 | 表只有几百行 | 优化器认为全表扫描更快 |
| 选择性太低 | `WHERE gender = 1`（只有男女两个值） | 回表代价可能比全表扫描更大 |

## 索引监控与维护

### 查看表的索引信息

```sql
-- 查看索引
SHOW INDEX FROM orders;

-- 查看索引使用情况
SELECT * FROM sys.schema_unused_indexes;          -- 未使用的索引
SELECT * FROM sys.schema_redundant_indexes;        -- 冗余索引
SELECT * FROM sys.schema_index_statistics;          -- 索引统计信息
```

### InnoDB 索引统计信息

```sql
-- 查看索引基数（Cardinality）
SHOW INDEX FROM orders;
-- Cardinality 列表示索引的区分度估计值

-- 手动更新统计信息（数据大幅变化后）
ANALYZE TABLE orders;

-- 控制统计信息持久化（推荐开启）
SET GLOBAL innodb_stats_persistent = ON;
```

### 索引碎片与重建

```sql
-- 查看表碎片
SELECT
    TABLE_NAME,
    DATA_LENGTH,
    INDEX_LENGTH,
    DATA_FREE,
    ROUND(DATA_FREE / (DATA_LENGTH + INDEX_LENGTH + DATA_FREE) * 100, 2) AS frag_ratio
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'your_database' AND TABLE_NAME = 'orders';

-- 重建表（消除碎片）
ALTER TABLE orders ENGINE=InnoDB;

-- 或使用 pt-online-schema-change（不锁表）
pt-online-schema-change --alter "ENGINE=InnoDB" D=test,t=orders --execute
```

## 索引优化 Checklist

| 检查项 | 优化手段 |
|--------|----------|
| 全表扫描 | 分析查询，添加合适的索引 |
| 回表过多 | 设计覆盖索引 |
| 索引列函数 | 改写 SQL，将函数移到值端 |
| 隐式转换 | 确保类型匹配 |
| 左模糊 | 改为右模糊或使用搜索引擎 |
| 索引合并 | 用联合索引替代 |
| 索引过多 | 删除未使用和冗余索引 |
| 索引碎片 | 定期 ANALYZE TABLE 或重建 |
| 统计信息过期 | 手动 ANALYZE TABLE |
