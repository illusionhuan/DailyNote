---
title: "Java异常处理与IO：从基础到进阶"
date: 2026-06-22 14:00:00
tags:
  - Java
  - 异常处理
  - IO
  - NIO
categories:
  - Java 进阶
---

## 前言

异常处理和 IO 操作是 Java 开发中的基础能力。写代码不可能不出错，关键是优雅地处理错误；文件读写、网络通信更是日常需求。本文系统梳理 Java 异常体系、IO 流、NIO 基础和反射机制，帮你建立完整的知识框架。

<!-- more -->

## 一、异常体系

### 1.1 异常层次结构

```
Throwable
├── Error（程序无法处理）
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── NoClassDefFoundError
└── Exception（程序可以处理）
    ├── RuntimeException（非受检异常，运行时）
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   ├── ClassCastException
    │   └── IllegalArgumentException
    └── 受检异常（编译时必须处理）
        ├── IOException
        ├── SQLException
        └── FileNotFoundException
```

### 1.2 受检异常 vs 非受检异常

- **受检异常（Checked）**：编译器强制要求处理（try-catch 或 throws），如 `IOException`
- **非受检异常（Unchecked）**：RuntimeException 及其子类，编译器不强制处理，如 `NullPointerException`

## 二、try-catch-finally

### 2.1 基本语法

```java
try {
    FileInputStream fis = new FileInputStream("test.txt");
    int data = fis.read();
} catch (FileNotFoundException e) {
    System.out.println("文件不存在");
} catch (IOException e) {
    System.out.println("读取失败");
} finally {
    System.out.println("无论是否异常都会执行");
}
```

### 2.2 catch 顺序规则

多个 catch 块时，子类异常必须在前，父类异常在后：

```java
try {
    // ...
} catch (FileNotFoundException e) {  // 子类在前
    // ...
} catch (IOException e) {            // 父类在后
    // ...
}
```

### 2.3 finally 的特性

- 无论 try 中是否 return，finally 都会执行
- finally 中不要写 return，会覆盖 try/catch 中的返回值

```java
public static int test() {
    try {
        return 1;
    } finally {
        System.out.println("finally 执行"); // 会执行
        // return 2;  // 不要这样做！会覆盖返回值为 2
    }
}
// 输出：finally 执行，返回 1
```

### 2.4 throw vs throws

```java
// throw：主动抛出异常
public void setAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("年龄不能为负");
    }
}

// throws：声明方法可能抛出的异常
public void readFile() throws IOException {
    FileInputStream fis = new FileInputStream("test.txt");
}
```

## 三、try-with-resources

Java 7 引入的语法糖，自动关闭实现了 `AutoCloseable` 接口的资源。

### 3.1 传统方式

```java
FileInputStream fis = null;
try {
    fis = new FileInputStream("test.txt");
    // 使用资源
} catch (IOException e) {
    e.printStackTrace();
} finally {
    if (fis != null) {
        try {
            fis.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### 3.2 try-with-resources

```java
try (FileInputStream fis = new FileInputStream("test.txt")) {
    // 使用资源，结束后自动关闭
} catch (IOException e) {
    e.printStackTrace();
}
// 不需要 finally 手动关闭
```

### 3.3 多个资源

```java
try (
    FileInputStream fis = new FileInputStream("in.txt");
    FileOutputStream fos = new FileOutputStream("out.txt")
) {
    // 自动按逆序关闭：先关 fos，再关 fis
}
```

## 四、IO 流体系

### 4.1 IO 流分类

| 分类 | 输入流 | 输出流 |
|------|--------|--------|
| 字节流 | InputStream | OutputStream |
| 字符流 | Reader | Writer |
| 缓冲流 | BufferedInputStream/BufferedReader | BufferedOutputStream/BufferedWriter |

### 4.2 字节流

```java
// 文件复制
try (FileInputStream fis = new FileInputStream("source.jpg");
     FileOutputStream fos = new FileOutputStream("copy.jpg")) {
    byte[] buffer = new byte[1024];
    int len;
    while ((len = fis.read(buffer)) != -1) {
        fos.write(buffer, 0, len);
    }
}
```

### 4.3 字符流

```java
// 读取文本文件
try (BufferedReader br = new BufferedReader(new FileReader("test.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
}
```

### 4.4 缓冲流

缓冲流在内部维护缓冲区（默认 8KB），减少系统调用次数，显著提升 IO 性能：

```java
// 使用缓冲流加速
try (BufferedInputStream bis = new BufferedInputStream(new FileInputStream("large.dat"));
     BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream("copy.dat"))) {
    byte[] buffer = new byte[8192];
    int len;
    while ((len = bis.read(buffer)) != -1) {
        bos.write(buffer, 0, len);
    }
}
```

## 五、NIO 基础

Java NIO（New IO）提供了非阻塞 IO 模型，核心组件：

### 5.1 三大核心组件

- **Buffer**：数据容器（ByteBuffer、CharBuffer 等）
- **Channel**：数据传输通道（FileChannel、SocketChannel 等）
- **Selector**：多路复用器（一个线程管理多个 Channel）

### 5.2 文件复制示例

```java
try (FileChannel src = new FileInputStream("source.dat").getChannel();
     FileChannel dst = new FileOutputStream("copy.dat").getChannel()) {
    src.transferTo(0, src.size(), dst);
}
```

### 5.3 Buffer 操作

```java
ByteBuffer buffer = ByteBuffer.allocate(1024);
// 写模式
buffer.put("Hello".getBytes());

// 切换到读模式
buffer.flip();
while (buffer.hasRemaining()) {
    System.out.print((char) buffer.get());
}

// 清空，准备下一次写入
buffer.clear();
```

## 六、反射机制

反射允许在运行时获取类信息、创建对象、调用方法、访问字段。

### 6.1 获取 Class 对象

```java
// 三种方式
Class<?> c1 = Class.forName("java.lang.String");
Class<?> c2 = String.class;
Class<?> c3 = "Hello".getClass();
```

### 6.2 创建实例

```java
Class<?> c = Class.forName("com.example.User");
User user = (User) c.getDeclaredConstructor().newInstance();
```

### 6.3 访问字段

```java
Class<?> c = obj.getClass();
Field field = c.getDeclaredField("name");
field.setAccessible(true);  // 突破 private 限制
String name = (String) field.get(obj);
field.set(obj, "新名字");
```

### 6.4 调用方法

```java
Class<?> c = obj.getClass();
Method method = c.getDeclaredMethod("sayHello", String.class);
method.setAccessible(true);
Object result = method.invoke(obj, "World");
```

**反射的应用场景：** Spring IoC 容器、ORM 框架、序列化/反序列化、动态代理等。

## 总结

| 知识点 | 核心要点 |
|--------|----------|
| 异常体系 | Error vs Exception，受检 vs 非受检 |
| try-with-resources | 自动关闭 AutoCloseable 资源，替代 finally 手动关闭 |
| IO 流 | 字节流处理二进制，字符流处理文本，缓冲流提升性能 |
| NIO | Buffer + Channel + Selector，非阻塞 IO |
| 反射 | 运行时获取类信息，框架的基石 |

异常处理和 IO 是 Java 开发的基本功，掌握这些知识能让你写出更健壮、更高效的代码。
