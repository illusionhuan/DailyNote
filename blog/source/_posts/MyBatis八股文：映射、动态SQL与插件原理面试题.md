---
title: MyBatis八股文：映射、动态SQL与插件原理面试题
date: 2026-06-23
tags: [MyBatis, 面试, ORM, SQL]
categories: [常用框架]
description: MyBatis高频面试题精讲，涵盖#{}与${}区别、Dao接口原理、分页插件、动态SQL、结果映射、延迟加载、Executor等核心知识点。
---

## #{} 和 ${} 的区别是什么？

**`${}`** 是 Properties 文件中的变量占位符，属于**静态文本替换**，比如 `${driver}` 会被静态替换为 `com.mysql.jdbc.Driver`。

**`#{}`** 是 SQL 的参数占位符，MyBatis 会将 SQL 中的 `#{}` 替换为 `?` 号，在 SQL 执行前使用 **PreparedStatement** 的参数设置方法按序设置参数值。`#{item.name}` 的取值方式为使用反射从参数对象中获取 item 对象的 name 属性值。

**核心区别：** `#{}` 能有效防止 SQL 注入，`${}` 不能。

## xml 映射文件中还有哪些标签？

除了常见的 `select`、`insert`、`update`、`delete` 标签之外，还有：

- **`<resultMap>`**：定义结果集映射
- **`<parameterMap>`**：参数映射
- **`<sql>`**：SQL 片段标签
- **`<include>`**：引入 SQL 片段
- **`<selectKey>`**：不支持自增的主键生成策略标签
- **动态 SQL 标签**：`trim`、`where`、`set`、`foreach`、`if`、`choose`、`when`、`otherwise`、`bind`

## Dao 接口的工作原理是什么？方法能重载吗？

Dao 接口就是 Mapper 接口，接口的**全限名**是映射文件中 `namespace` 的值，接口的**方法名**是映射文件中 `MappedStatement` 的 id 值。

**工作原理：** MyBatis 运行时使用 **JDK 动态代理**为 Dao 接口生成代理对象，代理对象拦截接口方法，转而执行 MappedStatement 所代表的 SQL。

**关于重载：** Dao 接口方法可以重载，但需要满足以下条件：
1. 仅有一个无参方法和一个有参方法
2. 多个有参方法时，参数数量必须一致，且使用相同的 `@Param`

但 xml 里的 **id 不允许重复**，因为 `namespace + id` 作为 Map 的 key 使用。

## MyBatis 是如何进行分页的？分页插件的原理是什么？

MyBatis 分页有三种方式：

1. **RowBounds 对象**：内存分页（逻辑分页），非物理分页
2. **SQL 物理分页**：在 SQL 内直接书写物理分页参数
3. **分页插件**：实现物理分页

**分页插件原理：** 使用 MyBatis 提供的插件接口实现自定义插件，在拦截方法内拦截待执行的 SQL，然后重写 SQL，添加对应的物理分页语句和参数。例如：`select * from student` 被重写为 `select t.* from (select * from student) t limit 0, 10`。

## 简述 MyBatis 的插件运行原理

MyBatis 仅可以编写针对 **ParameterHandler**、**ResultSetHandler**、**StatementHandler**、**Executor** 这 4 种接口的插件。

MyBatis 使用 **JDK 动态代理**为需要拦截的接口生成代理对象，每当执行这 4 种接口对象的方法时，就会进入拦截方法（`InvocationHandler.invoke()`），只拦截指定需要拦截的方法。

**编写插件步骤：**
1. 实现 MyBatis 的 `Interceptor` 接口并复写 `intercept()` 方法
2. 给插件编写注解，指定要拦截哪一个接口的哪些方法
3. 在配置文件中配置插件

## MyBatis 执行批量插入能返回数据库主键列表吗？

**能。** JDBC 都能，MyBatis 当然也能。

## MyBatis 动态 SQL 有哪些？执行原理是什么？

MyBatis 提供了 **9 种动态 SQL 标签**：

- `<if>`：条件判断
- `<where>`：自动处理 WHERE 关键字
- `<trim>`：自定义前缀/后缀
- `<set>`：UPDATE 语句的 SET 处理
- `<choose>` / `<when>` / `<otherwise>`：类似 switch-case
- `<foreach>`：遍历集合
- `<bind>`：变量绑定

**执行原理：** 使用 **OGNL** 从 SQL 参数对象中计算表达式的值，根据表达式的值动态拼接 SQL。

## MyBatis 如何将 SQL 执行结果封装为目标对象？

有两种映射形式：

1. **`<resultMap>` 标签**：逐一定义列名和对象属性名之间的映射关系
2. **SQL 别名**：将列别名书写为对象属性名，如 `T_NAME AS NAME`

MyBatis 通过**反射**创建对象，同时使用反射给对象的属性逐一赋值。找不到映射关系的属性无法赋值。

## 一对一、一对多关联查询如何实现？

MyBatis 支持一对一、一对多、多对一、多对多的关联查询。

**两种实现方式：**

1. **单独发送 SQL**：发送一个 SQL 查询关联对象，赋给主对象后返回
2. **嵌套查询（join）**：使用 join 查询，一部分列是 A 对象的属性，另一部分是关联对象 B 的属性，只发一个 SQL

**去重原理：** `<resultMap>` 标签内的 `<id>` 子标签指定唯一确定一条记录的 id 列，MyBatis 根据 `<id>` 列值完成去重。

## MyBatis 是否支持延迟加载？实现原理是什么？

**支持。** MyBatis 仅支持 **association**（一对一）和 **collection**（一对多）的延迟加载。

**实现原理：** 使用 **CGLIB** 创建目标对象的代理对象。当调用目标方法时（如 `a.getB().getName()`），拦截器发现 `a.getB()` 是 null，就会单独发送事先保存好的查询关联 B 对象的 SQL，把 B 查询上来，然后调用 `a.setB(b)`。

配置方式：在 MyBatis 配置文件中设置 `lazyLoadingEnabled=true`。

## 不同 xml 映射文件的 id 可以重复吗？

如果配置了 **namespace**，id 可以重复；如果没有配置 namespace，id 不能重复。

原因：`namespace + id` 作为 `Map<String, MappedStatement>` 的 key 使用，没有 namespace 时 id 重复会导致数据互相覆盖。

## MyBatis 都有哪些 Executor 执行器？

MyBatis 有三种基本的 Executor 执行器：

| 执行器 | 特点 |
|--------|------|
| **SimpleExecutor** | 每执行一次 update 或 select，就开启一个 Statement 对象，用完立刻关闭 |
| **ReuseExecutor** | 以 sql 作为 key 查找 Statement 对象，存在就使用，不存在就创建，用完不关闭，供下次使用 |
| **BatchExecutor** | 执行 update 时将所有 sql 添加到批处理中（addBatch），等待统一执行（executeBatch） |

作用范围：Executor 的特点严格限制在 **SqlSession 生命周期**范围内。

## MyBatis 是否可以映射 Enum 枚举类？

**可以。** 映射方式为自定义一个 **TypeHandler**，实现 `setParameter()` 和 `getResult()` 接口方法。TypeHandler 有两个作用：
1. 完成从 javaType 至 jdbcType 的转换
2. 完成 jdbcType 至 javaType 的转换

## include 引用的标签必须定义在前面吗？

**不需要。** 虽然 MyBatis 解析 xml 映射文件是按照顺序解析的，但被引用的 B 标签可以定义在任何地方。

原理：MyBatis 解析 A 标签发现引用了尚未解析的 B 标签时，会将 A 标签标记为**未解析状态**，继续解析剩余标签，待所有标签解析完毕后，重新解析那些未解析的标签。

## xml 映射文件与 MyBatis 内部数据结构的映射关系？

MyBatis 将所有 xml 配置信息封装到 **Configuration** 对象内部：

- `<parameterMap>` → **ParameterMap** 对象
- `<parameterMap>` 子元素 → **ParameterMapping** 对象
- `<resultMap>` → **ResultMap** 对象
- `<resultMap>` 子元素 → **ResultMapping** 对象
- `<select>`/`<insert>`/`<update>`/`<delete>` → **MappedStatement** 对象
- 标签内的 SQL → **BoundSql** 对象

## MyBatis 是半自动 ORM 映射工具？

**Hibernate** 属于全自动 ORM 映射工具，查询关联对象或集合时可以根据对象关系模型直接获取。

**MyBatis** 在查询关联对象或关联集合对象时，需要**手动编写 SQL** 来完成，所以称之为半自动 ORM 映射工具。
