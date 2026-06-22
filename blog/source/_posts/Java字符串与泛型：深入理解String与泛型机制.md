---
title: "Java字符串与泛型：深入理解String与泛型机制"
date: 2026-06-22 12:00:00
tags:
  - Java
  - String
  - 泛型
categories:
  - Java 进阶
---

## 前言

String 是 Java 中最常用的类之一，但其底层设计却暗藏玄机——不可变性、常量池、字符串拼接的性能陷阱，都是面试和开发中的高频考点。泛型则是 Java 5 引入的类型安全利器。本文从源码层面深入解析 String 和泛型的核心机制。

<!-- more -->

## 一、String 的不可变性

String 类被 `final` 修饰，不能被继承；内部字符数组也是 `final` 的，创建后不可修改。

```java
// JDK 8 及之前
public final class String {
    private final char value[];
}

// JDK 9+ 改为 byte[] 节省内存
public final class String {
    private final byte[] value;
}
```

**所有字符串操作（拼接、截取、替换）都会返回新对象：**

```java
String s1 = "Hello";
String s2 = s1.concat(" World");
System.out.println(s1); // "Hello"（原对象不变）
System.out.println(s2); // "Hello World"（新对象）
```

**不可变的三大意义：**
1. **安全性**：网络连接、文件路径等参数使用 String，防止被恶意修改
2. **哈希稳定性**：hashCode 缓存不变，可安全用作 HashMap 的 key
3. **常量池共享**：相同字面量可复用同一对象，节省内存

## 二、字符串常量池

### 2.1 字面量 vs new

```java
String s1 = "Hello";
String s2 = "Hello";
String s3 = new String("Hello");

System.out.println(s1 == s2);  // true（常量池同一对象）
System.out.println(s1 == s3);  // false（s3 在堆上新建了对象）
System.out.println(s1.equals(s3)); // true（值相同）
```

### 2.2 intern() 方法

`intern()` 将字符串放入常量池并返回池中引用：

```java
String s1 = new String("Hello");
String s2 = s1.intern();
String s3 = "Hello";

System.out.println(s2 == s3);  // true
```

### 2.3 创建了几个对象？

```java
String s = new String("Hello");
```

这段代码创建了 **2 个对象**：常量池中的 `"Hello"` + 堆上的 `new String()`。但如果常量池中已有 `"Hello"`，则只创建 1 个。

## 三、字符串比较

### 3.1 == vs equals()

```java
String a = "Hello";
String b = new String("Hello");

System.out.println(a == b);       // false（引用不同）
System.out.println(a.equals(b));  // true（值相同）
```

**规则：字符串比较永远用 `equals()`，不用 `==`。**

### 3.2 Objects.equals() 防空指针

```java
String a = null;
String b = "Hello";

// System.out.println(a.equals(b));  // NullPointerException!
System.out.println(Objects.equals(a, b));  // false（安全）
```

## 四、字符串拼接的性能陷阱

### 4.1 + 号拼接的真相

编译器会将 `+` 优化为 `StringBuilder.append()`，但在循环中每次都会创建新的 StringBuilder：

```java
// 循环中用 + 拼接（极慢！）
String result = "";
for (int i = 0; i < 100000; i++) {
    result += i;  // 每次循环 new StringBuilder → append → toString
}

// 正确做法：手动 StringBuilder
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 100000; i++) {
    sb.append(i);
}
String result = sb.toString();
```

**性能差距：循环 10 万次，`+` 号拼接比 StringBuilder 慢约 6000 倍。**

### 4.2 StringBuilder vs StringBuffer

| 特性 | StringBuilder | StringBuffer |
|------|---------------|--------------|
| 线程安全 | ❌ | ✅（synchronized） |
| 性能 | 更快 | 略慢 |
| 使用场景 | 单线程（绝大多数情况） | 多线程共享时 |

**结论：优先使用 StringBuilder，除非明确需要线程安全。**

## 五、泛型基础

泛型是 Java 5 引入的参数化类型机制，在编译期检查类型安全。

### 5.1 泛型类

```java
public class Box<T> {
    private T content;

    public void set(T content) {
        this.content = content;
    }

    public T get() {
        return content;
    }
}

Box<String> box = new Box<>();
box.set("Hello");
String s = box.get();  // 无需强制类型转换
```

### 5.2 泛型方法

```java
public static <T> T getFirst(List<T> list) {
    return list.get(0);
}

// 调用时类型推断
String first = getFirst(Arrays.asList("A", "B", "C"));
```

### 5.3 泛型接口

```java
public interface Repository<T> {
    void save(T entity);
    T findById(int id);
}

public class UserRepository implements Repository<User> {
    @Override
    public void save(User entity) { }
    @Override
    public User findById(int id) { return null; }
}
```

## 六、类型擦除

泛型信息只在编译期存在，运行时会被擦除。

```java
// 编译前
List<String> list = new ArrayList<>();
list.add("Hello");

// 编译后（类型擦除）
List list = new ArrayList();
list.add("Hello");
String s = (String) list.get(0);  // 编译器自动插入强转
```

**类型擦除的限制：**
1. 不能使用基本类型：`List<int>` ❌，`List<Integer>` ✅
2. 不能创建泛型数组：`new T[10]` ❌
3. 不能 instanceof 泛型类型：`obj instanceof List<String>` ❌

## 七、通配符

### 7.1 上界通配符 `<? extends T>` — 只读

```java
// 可以读取为 Number，但不能写入
public double sum(List<? extends Number> list) {
    double total = 0;
    for (Number n : list) {
        total += n.doubleValue();
    }
    return total;
}
```

### 7.2 下界通配符 `<? super T>` — 只写

```java
// 可以添加 Integer 或其子类
public void addIntegers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
}
```

### 7.3 PECS 原则

**Producer Extends, Consumer Super**：
- 如果是数据**生产者**（读取数据），用 `? extends T`
- 如果是数据**消费者**（写入数据），用 `? super T`

```java
// Collections.copy() 经典示例
public static <T> void copy(List<? super T> dest, List<? extends T> src) {
    for (int i = 0; i < src.size(); i++) {
        dest.set(i, src.get(i));  // src 读取用 extends，dest 写入用 super
    }
}
```

## 总结

| 知识点 | 核心要点 |
|--------|----------|
| String 不可变 | `final class` + `final byte[]`，所有操作返回新对象 |
| 常量池 | 字面量共享，`new` 不共享，`intern()` 手动入池 |
| 字符串拼接 | 循环中用 StringBuilder，不用 `+` |
| 泛型 | 编译期类型检查，运行时类型擦除 |
| 通配符 | PECS 原则：Producer Extends, Consumer Super |

String 和泛型是 Java 开发的日常工具，理解其底层机制能帮你写出更安全、更高效的代码。
