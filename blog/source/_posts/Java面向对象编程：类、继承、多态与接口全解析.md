---
title: "Java面向对象编程：类、继承、多态与接口全解析"
date: 2026-06-22 11:00:00
tags:
  - Java
  - 面向对象
  - 设计模式
categories:
  - Java 进阶
---

## 前言

面向对象编程（OOP）是 Java 的灵魂。理解类与对象、继承与多态、接口与抽象类，是从 Java 初学者迈向进阶开发者的关键一步。本文系统梳理 Java 面向对象的核心知识点，配合代码示例，帮你建立完整的 OOP 认知体系。

<!-- more -->

## 一、类与对象

### 1.1 什么是类

类是对象的模板（蓝图），定义了一组属性（字段）和行为（方法）。

```java
public class Person {
    // 属性（字段）
    String name;
    int age;

    // 行为（方法）
    public void sayHello() {
        System.out.println("大家好，我是" + name + "，今年" + age + "岁");
    }
}
```

### 1.2 创建对象

通过 `new` 关键字实例化类，调用构造方法创建对象：

```java
public class Main {
    public static void main(String[] args) {
        Person p = new Person();
        p.name = "沉默王二";
        p.age = 18;
        p.sayHello();
    }
}
```

### 1.3 对象在内存中的存储

- **栈（Stack）**：存放局部变量和对象引用（变量名指向堆中的地址）
- **堆（Heap）**：存放对象实例（new 出来的对象）
- **方法区**：存放类信息、常量池、静态变量

```
栈           堆
p ---------> Person 对象
             name = "沉默王二"
             age = 18
```

## 二、构造方法

构造方法用于对象初始化，与类名相同，无返回值。

### 2.1 默认构造方法

如果不写构造方法，编译器会自动提供一个无参构造方法：

```java
public class Person {
    String name;
    int age;

    // 无参构造方法
    public Person() {
        this.name = "未知";
        this.age = 0;
    }
}
```

### 2.2 有参构造方法

```java
public Person(String name, int age) {
    this.name = name;
    this.age = age;
}
```

### 2.3 构造方法重载

一个类可以有多个构造方法，参数列表不同：

```java
public Person() { }
public Person(String name) { this.name = name; }
public Person(String name, int age) { this.name = name; this.age = age; }
```

### 2.4 this 关键字

`this` 指向当前对象实例，常用于：
- 区分成员变量和局部变量（参数同名时）
- 在构造方法中调用另一个构造方法：`this(args)`

```java
public Person(String name) {
    this(name, 0); // 调用另一个构造方法
}
```

## 三、封装

封装是 OOP 的第一大特性，核心思想：**隐藏内部实现，只暴露必要接口**。

### 3.1 访问修饰符

| 修饰符 | 同类 | 同包 | 子类 | 其他包 |
|--------|------|------|------|--------|
| `private` | ✅ | ❌ | ❌ | ❌ |
| `default` | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

### 3.2 Getter/Setter

将字段设为 `private`，通过 `public` 方法访问：

```java
public class Person {
    private String name;
    private int age;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public int getAge() { return age; }
    public void setAge(int age) {
        if (age < 0) throw new IllegalArgumentException("年龄不能为负");
        this.age = age;
    }
}
```

## 四、继承

继承是 OOP 的第二大特性，子类继承父类的属性和方法，实现代码复用。

### 4.1 继承语法

使用 `extends` 关键字：

```java
public class Animal {
    String name;

    public void eat() {
        System.out.println(name + "在吃东西");
    }
}

public class Dog extends Animal {
    public void bark() {
        System.out.println(name + "在汪汪叫");
    }
}
```

### 4.2 方法重写（Override）

子类可以重写父类的方法，`@Override` 注解显式声明：

```java
public class Dog extends Animal {
    @Override
    public void eat() {
        System.out.println(name + "在啃骨头");
    }
}
```

**重写规则：**
- 方法名、参数列表必须相同
- 返回值类型可以是父类返回值的子类（协变返回）
- 访问权限不能比父类更严格
- 不能抛出比父类更多的受检异常

### 4.3 super 关键字

`super` 指向父类的引用：
- `super.method()`：调用父类方法
- `super.field`：访问父类字段
- `super(args)`：调用父类构造方法（必须放在第一行）

```java
public class Dog extends Animal {
    public Dog(String name) {
        super.name = name; // 调用父类字段
    }

    @Override
    public void eat() {
        super.eat(); // 调用父类方法
        System.out.println("还啃了骨头");
    }
}
```

### 4.4 单继承限制

Java 只支持单继承（一个类只能有一个直接父类），但可以多层继承：

```
Object ← Animal ← Dog
```

## 五、多态

多态是 OOP 的第三大特性，同一方法调用在不同对象上产生不同行为。

### 5.1 多态的前提

1. 必须有继承或实现关系
2. 必须有方法重写
3. 父类引用指向子类对象（向上转型）

```java
Animal animal = new Dog(); // 向上转型
animal.eat(); // 调用的是 Dog 重写后的 eat()
```

### 5.2 向下转型

```java
Animal animal = new Dog();
if (animal instanceof Dog) {
    Dog dog = (Dog) animal; // 向下转型
    dog.bark();
}
```

### 5.3 多态的底层原理

Java 多态基于**动态绑定（Dynamic Binding）**：
- 编译时看引用类型（决定能否调用）
- 运行时看实际对象类型（决定调用哪个方法）

```java
Animal a = new Dog();
a.eat();  // 编译器检查 Animal 有 eat() → 编译通过
          // 运行时发现是 Dog → 调用 Dog.eat()
```

## 六、抽象类

当父类的方法只有方法签名而没有具体实现时，可以定义为抽象类。

```java
public abstract class Shape {
    // 抽象方法：没有方法体
    public abstract double area();

    // 普通方法：可以有实现
    public void print() {
        System.out.println("面积是：" + area());
    }
}

public class Circle extends Shape {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}
```

**抽象类的特点：**
- 不能被实例化（`new Shape()` 编译报错）
- 可以有抽象方法和普通方法
- 子类必须实现所有抽象方法，否则子类也必须声明为抽象类

## 七、接口

接口是一种更纯粹的抽象，Java 8 之后支持默认方法。

### 7.1 定义接口

```java
public interface Flyable {
    int MAX_HEIGHT = 10000; // 默认 public static final

    void fly(); // 默认 public abstract

    // Java 8 默认方法
    default void land() {
        System.out.println("着陆");
    }
}
```

### 7.2 实现接口

```java
public class Bird implements Flyable {
    @Override
    public void fly() {
        System.out.println("鸟儿展翅高飞");
    }
}
```

### 7.3 接口 vs 抽象类

| 特性 | 接口 | 抽象类 |
|------|------|--------|
| 实例化 | ❌ | ❌ |
| 多实现 | ✅ `implements A, B` | ❌ 只能单继承 |
| 构造方法 | ❌ | ✅ |
| 成员变量 | 只能 `public static final` | 任意 |
| 方法 | 抽象方法 + 默认方法 | 抽象方法 + 普通方法 |
| 设计理念 | "能做什么"（能力） | "是什么"（本质） |

### 7.4 接口的多态

```java
public interface Swimmable {
    void swim();
}

public class Duck extends Animal implements Flyable, Swimmable {
    @Override
    public void fly() { System.out.println("鸭子飞"); }

    @Override
    public void swim() { System.out.println("鸭子游泳"); }
}

// 多态使用
Flyable f = new Duck();
f.fly();

Swimmable s = new Duck();
s.swim();
```

## 八、关键字总结

### 8.1 static

- **静态变量**：属于类，所有对象共享，通过 `类名.变量` 访问
- **静态方法**：属于类，不能访问非静态成员
- **静态代码块**：类加载时执行一次，优先于 main 方法

```java
public class Counter {
    static int count = 0;

    public Counter() {
        count++; // 每次创建对象，计数+1
    }

    static {
        System.out.println("类加载了");
    }
}
```

### 8.2 final

- **final 变量**：值不能被修改（常量）
- **final 方法**：不能被重写
- **final 类**：不能被继承

```java
final class Constants {
    public static final double PI = 3.14159265358979;
}
```

## 总结

| 特性 | 核心思想 | 关键词 |
|------|----------|--------|
| 封装 | 隐藏实现，暴露接口 | `private`、getter/setter |
| 继承 | 代码复用，层次关系 | `extends`、`super` |
| 多态 | 同一接口，不同实现 | `@Override`、`instanceof`、向上转型 |

面向对象的三大特性是 Java 编程的基石。掌握类与对象的内存模型、构造方法的初始化流程、继承与多态的动态绑定机制、接口与抽象类的设计选择，是写出高质量 Java 代码的前提。
