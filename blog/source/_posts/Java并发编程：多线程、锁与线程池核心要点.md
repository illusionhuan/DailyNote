---
title: "Java并发编程：多线程、锁与线程池核心要点"
date: 2026-06-22 15:00:00
tags:
  - Java
  - 并发编程
  - 多线程
  - 线程池
categories:
  - Java 进阶
---

## 前言

并发编程是 Java 进阶的必经之路。线程如何创建？synchronized 和 volatile 有什么区别？线程池的参数怎么配？本文从线程基础到高级并发工具，系统梳理 Java 并发编程的核心知识点。

<!-- more -->

## 一、线程基础

### 1.1 创建线程的三种方式

**方式一：继承 Thread**
```java
public class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread 运行：" + getName());
    }
}
new MyThread().start();
```

**方式二：实现 Runnable**
```java
new Thread(() -> {
    System.out.println("Runnable 运行");
}).start();
```

**方式三：实现 Callable（有返回值）**
```java
FutureTask<Integer> task = new FutureTask<>(() -> {
    return 1 + 1;
});
new Thread(task).start();
Integer result = task.get(); // 阻塞等待结果
```

### 1.2 线程生命周期

```
NEW（新建）
  ↓ start()
RUNNABLE（可运行/运行中）
  ↓ 获得锁        ↓ wait()        ↓ sleep()/join()
  ↑               WAITING         TIMED_WAITING
  ↓ notify()      ↓ 超时/notify()
RUNNABLE ←────────┘
  ↓ run() 结束
TERMINATED（终止）
```

### 1.3 核心方法

| 方法 | 作用 | 是否释放锁 |
|------|------|------------|
| `start()` | 启动线程 | - |
| `sleep(ms)` | 暂停执行 | ❌ 不释放 |
| `join()` | 等待线程结束 | ❌ 不释放 |
| `wait()` | 等待通知 | ✅ 释放锁 |
| `notify()` | 唤醒一个等待线程 | - |
| `notifyAll()` | 唤醒所有等待线程 | - |
| `yield()` | 让出 CPU 时间片 | - |
| `interrupt()` | 中断线程 | - |

## 二、synchronized

### 2.1 三种用法

```java
// 1. 修饰实例方法：锁的是 this 对象
public synchronized void method() { }

// 2. 修饰静态方法：锁的是 Class 对象
public static synchronized void staticMethod() { }

// 3. 修饰代码块：锁的是指定对象
public void blockMethod() {
    synchronized (this) {
        // 临界区
    }
}
```

### 2.2 底层原理

- **代码块层面**：通过 `monitorenter` 和 `monitorexit` 字节码指令
- **方法层面**：通过 `ACC_SYNCHRONIZED` 标志位
- **锁升级**：无锁 → 偏向锁 → 轻量级锁（CAS + 自旋）→ 重量级锁（OS 互斥量）

### 2.3 可重入性

synchronized 是可重入锁，同一线程可以多次获取同一把锁：

```java
public synchronized void method1() {
    method2();  // 可以直接调用，不会死锁
}
public synchronized void method2() { }
```

## 三、volatile

### 3.1 两个作用

1. **可见性**：一个线程修改 volatile 变量后，其他线程立即可见
2. **禁止指令重排**：通过内存屏障防止编译器和 CPU 重排序

```java
private volatile boolean running = true;

// 线程 A
running = false;  // 修改后立即对其他线程可见

// 线程 B
while (running) { }  // 能立即感知到变化
```

### 3.2 volatile vs synchronized

| 特性 | volatile | synchronized |
|------|----------|--------------|
| 原子性 | ❌（仅保证读写的原子性） | ✅ |
| 可见性 | ✅ | ✅ |
| 有序性 | ✅（禁止重排） | ✅ |
| 阻塞 | ❌ | ✅ |
| 适用场景 | 状态标志、DCL 单例 | 临界区保护 |

### 3.3 经典应用：DCL 双检锁单例

```java
public class Singleton {
    private static volatile Singleton instance;

    public static Singleton getInstance() {
        if (instance == null) {                    // 第一次检查
            synchronized (Singleton.class) {
                if (instance == null) {            // 第二次检查
                    instance = new Singleton();    // volatile 防止重排序
                }
            }
        }
        return instance;
    }
}
```

## 四、Lock 接口

### 4.1 ReentrantLock

```java
private final ReentrantLock lock = new ReentrantLock();

public void method() {
    lock.lock();
    try {
        // 临界区
    } finally {
        lock.unlock();  // 必须在 finally 中释放
    }
}
```

### 4.2 synchronized vs ReentrantLock

| 特性 | synchronized | ReentrantLock |
|------|--------------|---------------|
| 实现 | JVM 内置 | JDK API |
| 自动释放 | ✅ | ❌ 需手动 unlock |
| 可中断 | ❌ | ✅ `lockInterruptibly()` |
| 超时获取 | ❌ | ✅ `tryLock(timeout)` |
| 公平锁 | ❌ | ✅ `new ReentrantLock(true)` |
| 条件变量 | 1 个 wait/notify | 多个 Condition |

## 五、线程池

### 5.1 ThreadPoolExecutor 核心参数

```java
public ThreadPoolExecutor(
    int corePoolSize,       // 核心线程数
    int maximumPoolSize,    // 最大线程数
    long keepAliveTime,     // 非核心线程空闲存活时间
    TimeUnit unit,          // 时间单位
    BlockingQueue<Runnable> workQueue,  // 任务队列
    ThreadFactory threadFactory,         // 线程工厂
    RejectedExecutionHandler handler     // 拒绝策略
)
```

### 5.2 工作流程

```
提交任务
  ↓
当前线程数 < corePoolSize？ → 创建核心线程执行
  ↓ 否
任务队列未满？ → 放入队列等待
  ↓ 否
当前线程数 < maximumPoolSize？ → 创建非核心线程执行
  ↓ 否
执行拒绝策略
```

### 5.3 四种拒绝策略

| 策略 | 行为 |
|------|------|
| `AbortPolicy`（默认） | 抛出 RejectedExecutionException |
| `CallerRunsPolicy` | 由提交任务的线程执行 |
| `DiscardPolicy` | 静默丢弃 |
| `DiscardOldestPolicy` | 丢弃队列最老的任务 |

### 5.4 常用线程池

```java
// 固定线程池
ExecutorService fixed = Executors.newFixedThreadPool(4);

// 缓存线程池
ExecutorService cached = Executors.newCachedThreadPool();

// 单线程池
ExecutorService single = Executors.newSingleThreadExecutor();

// 定时线程池
ScheduledExecutorService scheduled = Executors.newScheduledThreadPool(2);
```

**阿里规约建议：** 不要使用 `Executors` 创建线程池，应直接使用 `ThreadPoolExecutor`，明确参数以避免 OOM。

### 5.5 线程池大小估算

- **CPU 密集型**：线程数 = CPU 核心数 + 1
- **IO 密集型**：线程数 = CPU 核心数 × 2（或根据 IO 等待比例调整）

## 六、并发工具类

### 6.1 CountDownLatch

等待 N 个线程完成后再继续：

```java
CountDownLatch latch = new CountDownLatch(3);

for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        System.out.println("子任务完成");
        latch.countDown();
    }).start();
}

latch.await();  // 阻塞等待计数归零
System.out.println("所有子任务完成");
```

### 6.2 CAS（Compare And Swap）

无锁并发的基础，比较并交换：

```java
// AtomicInteger 的 incrementAndGet 底层
public final int incrementAndGet() {
    return U.getAndAddInt(this, VALUE, 1) + 1;
    // 底层 CAS 循环：预期值匹配才更新，否则重试
}
```

**ABA 问题**：值从 A→B→A，CAS 检测不到变化。解决方案：`AtomicStampedReference`（加版本号）。

## 总结

| 知识点 | 核心要点 |
|--------|----------|
| 线程创建 | Thread / Runnable / Callable |
| synchronized | 可重入锁，锁升级（偏向→轻量级→重量级） |
| volatile | 可见性 + 禁止重排，不保证原子性 |
| Lock | 更灵活：可中断、超时、公平锁、多条件 |
| 线程池 | 7 大参数、工作流程、拒绝策略 |
| 并发工具 | CountDownLatch、CAS |

并发编程是 Java 面试的重灾区，理解线程安全的本质（可见性、原子性、有序性）和各种同步机制的适用场景，是写出高质量并发代码的前提。
