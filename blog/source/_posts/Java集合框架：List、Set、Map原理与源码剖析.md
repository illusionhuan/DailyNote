---
title: "Java集合框架：List、Set、Map原理与源码剖析"
date: 2026-06-22 13:00:00
tags:
  - Java
  - 集合框架
  - HashMap
  - 源码分析
categories:
  - Java 进阶
---

## 前言

集合框架是 Java 中使用频率最高的 API 之一。ArrayList 和 LinkedList 怎么选？HashSet 的底层是什么？HashMap 的数组+链表+红黑树是怎么回事？本文从源码层面剖析集合框架的核心原理，帮你做出正确的技术选型。

<!-- more -->

## 一、Collection 体系概览

```
Collection（接口）
├── List（有序，可重复）
│   ├── ArrayList    — 数组实现
│   ├── LinkedList   — 双向链表
│   └── Vector       — 线程安全（过时）
├── Set（无序，不可重复）
│   ├── HashSet      — 基于 HashMap
│   ├── LinkedHashSet — 保持插入顺序
│   └── TreeSet      — 红黑树，有序
│
Map（接口，键值对）
├── HashMap          — 数组+链表+红黑树
├── LinkedHashMap    — 保持插入顺序
├── TreeMap          — 红黑树，按键排序
└── ConcurrentHashMap — 线程安全
```

## 二、ArrayList vs LinkedList

### 2.1 ArrayList 源码要点

ArrayList 底层是 `Object[]` 数组，默认容量 10，扩容为原来的 **1.5 倍**：

```java
// 扩容核心代码
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1); // 1.5 倍
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

**特点：**
- 随机访问 O(1)：`get(index)` 直接下标定位
- 尾部添加 O(1) 均摊：偶尔触发扩容
- 中间插入/删除 O(n)：需要移动后续元素

### 2.2 LinkedList 源码要点

LinkedList 底层是双向链表，每个节点包含 `prev`、`item`、`next`：

```java
private static class Node<E> {
    E item;
    Node<E> next;
    Node<E> prev;
}
```

**查找优化：** `get(index)` 会判断 index 在前半段还是后半段，从较近的一端遍历：

```java
Node<E> node(int index) {
    if (index < (size >> 1)) {
        Node<E> x = first;
        for (int i = 0; i < index; i++) x = x.next;
        return x;
    } else {
        Node<E> x = last;
        for (int i = size - 1; i > index; i--) x = x.prev;
        return x;
    }
}
```

### 2.3 选型对比

| 操作 | ArrayList | LinkedList |
|------|-----------|------------|
| 随机访问 `get(i)` | O(1) | O(n) |
| 尾部添加 `add(e)` | O(1) 均摊 | O(1) |
| 中间插入 `add(i,e)` | O(n) | O(n)（查找O(n)+插入O(1)） |
| 内存占用 | 紧凑（可能浪费尾部空间） | 每个节点额外 prev/next 指针 |

**结论：绝大多数场景选 ArrayList。** 只有在频繁头部插入/删除时才考虑 LinkedList。

## 三、HashSet 与 TreeSet

### 3.1 HashSet 的秘密

HashSet 底层就是一个 HashMap，元素存为 key，value 统一用一个 `PRESENT` 哑对象：

```java
public class HashSet<E> {
    private transient HashMap<E,Object> map;
    private static final Object PRESENT = new Object();

    public boolean add(E e) {
        return map.put(e, PRESENT) == null;
    }
}
```

### 3.2 TreeSet

TreeSet 底层是 TreeMap（红黑树），元素自然排序或自定义 Comparator：

```java
TreeSet<Integer> set = new TreeSet<>();
set.add(3);
set.add(1);
set.add(2);
System.out.println(set); // [1, 2, 3]（有序）
```

## 四、HashMap 底层原理

### 4.1 数据结构

JDK 8 的 HashMap 采用 **数组 + 链表 + 红黑树**：

```
数组（Node[] table）
├── [0] → null
├── [1] → Node → Node → Node（链表，长度<8）
├── [2] → null
├── [3] → TreeNode（红黑树，链表长度≥8时转化）
└── ...
```

### 4.2 hash() 扰动函数

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

高 16 位与低 16 位异或，增加散列性，减少哈希冲突。

**数组下标计算：** `(n - 1) & hash`，等价于 `hash % n`（前提是 n 为 2 的幂）。

### 4.3 put 流程

1. 计算 key 的 hash 值
2. 如果 table 为空，调用 `resize()` 初始化
3. 计算下标 `(n-1) & hash`，如果该位置为空，直接插入
4. 如果有冲突：
   - 链表：遍历到尾部插入（JDK 8 尾插法，JDK 7 头插法）
   - 如果链表长度 ≥ 8 且数组长度 ≥ 64，转化为红黑树
5. 如果 key 已存在，覆盖 value
6. 如果 size > threshold（容量 × 加载因子），触发扩容

### 4.4 扩容机制

默认初始容量 16，加载因子 0.75，扩容为原来的 **2 倍**：

```java
// 扩容时元素重新分配
// JDK 8 优化：新索引 = 原位置 或 原位置 + 原容量
if ((e.hash & oldCap) == 0) {
    // 新索引 = 原索引（低位不变）
} else {
    // 新索引 = 原索引 + oldCap（高位加偏移）
}
```

### 4.5 为什么加载因子是 0.75？

这是时间和空间的折中。根据泊松分布，当加载因子为 0.75 时：
- 链表长度为 0 的概率：0.60653066
- 链表长度为 1 的概率：0.30326533
- ...
- **链表长度达到 8 的概率：约 0.00000006（千万分之六）**

这个概率足够低，使得红黑树转化很少发生，保证了大多数情况下的 O(1) 查找效率。

### 4.6 HashMap 的 key 要求

- 必须正确实现 `hashCode()` 和 `equals()`
- 两个相等的 key 必须有相同的 hashCode
- 推荐使用不可变对象作为 key（String、Integer）

## 五、fail-fast 机制

当使用迭代器遍历集合时，如果集合被修改（非迭代器自身修改），会抛出 `ConcurrentModificationException`：

```java
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

// 错误：遍历中直接删除
for (String s : list) {
    if ("B".equals(s)) {
        list.remove(s);  // 抛出 ConcurrentModificationException
    }
}

// 正确：使用迭代器的 remove()
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    if ("B".equals(it.next())) {
        it.remove();  // 安全删除
    }
}
```

## 总结

| 集合 | 底层结构 | 适用场景 |
|------|----------|----------|
| ArrayList | 数组 | 随机访问、尾部操作 |
| LinkedList | 双向链表 | 频繁头尾操作（极少用） |
| HashSet | HashMap | 去重 |
| TreeSet | 红黑树 | 去重 + 排序 |
| HashMap | 数组+链表+红黑树 | 键值对存储（最常用） |
| ConcurrentHashMap | 分段锁/CAS | 线程安全的键值对 |

集合框架是 Java 面试的必考内容，理解底层数据结构和源码实现，不仅能帮你做出正确的技术选型，还能在排查性能问题时游刃有余。
