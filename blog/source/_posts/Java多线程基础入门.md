---
title: Java多线程基础入门
date: 2026-06-21 10:00:00
tags:
  - 后端开发
  - Java
  - 多线程
categories:
  - 后端开发
description: 全面介绍 Java 多线程的核心概念，包括线程创建、生命周期、同步机制、线程池等基础知识，帮助初学者建立多线程编程的完整认知。
---

## 为什么需要多线程？

在现代计算机中，CPU 通常有多个核心。如果程序只有一个线程，那就只能利用一个核心，其余核心都在空闲。多线程编程让我们能够：

- **提高程序响应速度**：UI 线程不被耗时操作阻塞
- **充分利用多核 CPU**：多个任务并行执行
- **提升吞吐量**：服务器同时处理多个请求

## 创建线程的三种方式

### 方式一：继承 Thread 类

```java
public class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("线程运行中: " + Thread.currentThread().getName());
    }
}

// 启动
MyThread t = new MyThread();
t.start();  // 注意是 start()，不是 run()
```

### 方式二：实现 Runnable 接口

```java
Runnable task = () -> {
    System.out.println("Runnable 任务执行: " + Thread.currentThread().getName());
};

Thread t = new Thread(task);
t.start();
```

### 方式三：实现 Callable 接口（有返回值）

```java
Callable<Integer> callable = () -> {
    Thread.sleep(1000);
    return 42;
};

// 通过 FutureTask 包装
FutureTask<Integer> future = new FutureTask<>(callable);
new Thread(future).start();

// 获取返回值（会阻塞当前线程）
Integer result = future.get();
System.out.println("结果: " + result);
```

> **推荐使用 Runnable/Callable**，因为 Java 不支持多继承，实现接口更灵活。

## 线程的生命周期

Java 线程有 6 种状态，定义在 `Thread.State` 枚举中：

```
NEW ──start()──▶ RUNNABLE ──获得锁──▶ 运行中
                       │                    │
                       │ wait()/join()      │ sleep()/wait()
                       ▼                    ▼
                   WAITING/TIMED_WAITING   BLOCKED（等待锁）
                       │                    │
                       │ notify()/超时       │ 获得锁
                       ▼                    ▼
                   RUNNABLE ◀──────────────┘
                       │
                    run() 结束
                       ▼
                   TERMINATED
```

| 状态 | 说明 |
|------|------|
| `NEW` | 已创建，尚未调用 `start()` |
| `RUNNABLE` | 可运行，可能正在运行也可能在等待 CPU 时间片 |
| `BLOCKED` | 等待获取 synchronized 锁 |
| `WAITING` | 无限期等待（`wait()`、`join()`） |
| `TIMED_WAITING` | 有限期等待（`sleep()`、`wait(timeout)`） |
| `TERMINATED` | 执行完毕 |

## 线程同步机制

多线程共享资源时会产生**竞态条件**（Race Condition）。Java 提供了多种同步机制。

### synchronized 关键字

```java
public class Counter {
    private int count = 0;

    // 同步方法：锁住整个对象
    public synchronized void increment() {
        count++;
    }

    // 同步代码块：只锁关键部分
    public void decrement() {
        synchronized (this) {
            count--;
        }
    }
}
```

### ReentrantLock

比 `synchronized` 更灵活，支持公平锁、可中断锁、超时锁：

```java
ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    // 临界区代码
} finally {
    lock.unlock();  // 必须在 finally 中释放
}
```

### volatile 关键字

保证变量的**可见性**（一个线程修改后，其他线程立即可见），但不保证原子性：

```java
private volatile boolean running = true;

// 线程 A
running = false;  // 修改后其他线程立即可见

// 线程 B
while (running) {
    // 能及时看到 running 的变化
}
```

## 线程间通信

### wait() / notify()

```java
synchronized (lock) {
    while (!condition) {
        lock.wait();     // 释放锁，进入等待
    }
    // 条件满足，执行业务逻辑
}

// 另一个线程
synchronized (lock) {
    condition = true;
    lock.notify();      // 唤醒一个等待线程
    // lock.notifyAll()  // 唤醒所有等待线程
}
```

> **注意：** `wait()` 必须在 `synchronized` 块中调用，否则抛出 `IllegalMonitorStateException`。

### CountDownLatch

等待一组任务完成：

```java
CountDownLatch latch = new CountDownLatch(3);

for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        doSomething();
        latch.countDown();  // 计数减 1
    }).start();
}

latch.await();  // 阻塞直到计数为 0
System.out.println("所有任务完成");
```

## 线程池

频繁创建销毁线程开销很大，线程池复用线程，是生产环境的标准做法。

### ThreadPoolExecutor

```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    2,                          // 核心线程数
    4,                          // 最大线程数
    60, TimeUnit.SECONDS,       // 非核心线程空闲存活时间
    new LinkedBlockingQueue<>(100),  // 任务队列
    new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略
);

pool.execute(() -> System.out.println("执行任务"));
pool.shutdown();
```

### Executors 工厂方法

```java
// 固定线程池
ExecutorService fixed = Executors.newFixedThreadPool(4);

// 缓存线程池（按需创建）
ExecutorService cached = Executors.newCachedThreadPool();

// 单线程池（保证任务顺序执行）
ExecutorService single = Executors.newSingleThreadExecutor();

// 定时线程池
ScheduledExecutorService scheduled = Executors.newScheduledThreadPool(2);
scheduled.scheduleAtFixedRate(() -> {
    System.out.println("定时任务");
}, 0, 1, TimeUnit.SECONDS);
```

> **阿里规约建议：** 不要使用 `Executors` 创建线程池，而是直接使用 `ThreadPoolExecutor`，明确指定参数，避免 OOM。

## 常见并发工具类

| 类 | 用途 |
|---|---|
| `ConcurrentHashMap` | 线程安全的 HashMap |
| `AtomicInteger` | 原子操作的整数 |
| `CopyOnWriteArrayList` | 读多写少场景的线程安全 List |
| `Semaphore` | 信号量，控制并发访问数 |
| `CyclicBarrier` | 一组线程互相等待，同时出发 |
| `BlockingQueue` | 生产者-消费者模型的阻塞队列 |

## 常见面试题速查

**1. start() 和 run() 的区别？**
`start()` 创建新线程并执行 `run()`；直接调用 `run()` 只是在当前线程执行普通方法。

**2. sleep() 和 wait() 的区别？**
`sleep()` 不释放锁，到时自动恢复；`wait()` 释放锁，需要 `notify()` 唤醒。

**3. synchronized 和 ReentrantLock 的区别？**
`synchronized` 自动释放锁，语法简洁；`ReentrantLock` 手动释放，支持公平锁、可中断、条件变量。

**4. 线程池的核心参数？**
核心线程数、最大线程数、空闲存活时间、任务队列、拒绝策略。

---

*下一篇将介绍 Java 并发编程的进阶内容：CompletableFuture、Fork/Join 框架和实战案例。*
