---
title: Spring八股文：IoC、AOP、MVC与事务管理核心面试题
date: 2026-06-23
tags: [Spring, 面试, IoC, AOP, MVC]
categories: [常用框架]
description: Spring框架高频面试题精讲，涵盖IoC容器、Bean生命周期、AOP原理、Spring MVC工作原理、事务管理及设计模式应用等核心知识点。
---

## Spring 基础

### 什么是 Spring 框架？

Spring 是一款开源的轻量级 Java 开发框架，核心功能是 **IoC（控制反转）** 和 **AOP（面向切面编程）**。Spring 旨在提高开发效率以及系统的可维护性，可以很方便地对数据库进行访问、集成第三方组件、支持单元测试和 RESTful Java 应用开发。

### Spring 包含哪些模块？

- **Core Container**：核心模块，提供 IoC 依赖注入功能（spring-core、spring-beans、spring-context、spring-expression）
- **AOP**：面向切面编程（spring-aop、spring-aspects）
- **Data Access/Integration**：数据库访问（spring-jdbc、spring-tx、spring-orm）
- **Spring Web**：Web 功能（spring-web、spring-webmvc、spring-webflux）
- **Spring Test**：测试支持

### Spring、Spring MVC、Spring Boot 之间的关系？

- **Spring**：核心是 IoC 依赖注入，其他模块都依赖它
- **Spring MVC**：Spring 中的 Web 模块，快速构建 MVC 架构的 Web 程序
- **Spring Boot**：简化 Spring 开发（减少配置，开箱即用），底层还是用 Spring MVC

## Spring IoC

### 谈谈对 IoC 的了解

**IoC（控制反转）** 是一种设计思想，将原本在程序中手动创建对象的控制权交给 Spring 框架管理。IoC 容器本质上就是一个 Map（key, value），存放各种对象。

- **控制**：对象创建、管理的权力
- **反转**：控制权交给外部环境（Spring 框架）

### @Component 和 @Bean 的区别？

| 对比项 | @Component | @Bean |
|--------|-----------|-------|
| 作用于 | **类** | **方法** |
| 装配方式 | 类路径扫描自动侦测 | 方法中定义产生 bean |
| 自定义性 | 较弱 | 更强 |

**@Bean** 可以注册第三方库中的类，@Component 做不到。

### @Autowired 和 @Resource 的区别？

| 对比项 | @Autowired | @Resource |
|--------|-----------|-----------|
| 来源 | **Spring** 提供 | **JDK** 提供 |
| 默认注入方式 | **byType**（按类型） | **byName**（按名称） |
| 多实现类处理 | 需配合 @Qualifier 指定名称 | 通过 name 属性指定 |

### Bean 的作用域有哪些？

| 作用域 | 说明 |
|--------|------|
| **singleton** | IoC 容器中只有唯一 bean 实例（默认） |
| **prototype** | 每次获取都创建新实例 |
| **request** | 每次 HTTP 请求创建新实例 |
| **session** | 每次新 session 创建新实例 |

### Bean 的生命周期

1. Bean 容器利用 Java Reflection API 创建 Bean 实例
2. 利用 `set()` 方法设置属性值
3. 如果实现了 `BeanNameAware` 等接口，调用相应方法
4. 执行 `BeanPostProcessor.postProcessBeforeInitialization()`
5. 如果实现了 `InitializingBean` 接口，执行 `afterPropertiesSet()`
6. 执行 `init-method` 指定的方法
7. 执行 `BeanPostProcessor.postProcessAfterInitialization()`
8. 销毁时执行 `DisposableBean.destroy()` 或 `destroy-method`

## Spring AOP

### 谈谈对 AOP 的了解

**AOP（面向切面编程）** 将与业务无关但为业务模块共同调用的逻辑（事务处理、日志管理、权限控制）封装起来，减少重复代码，降低耦合度。

**Spring AOP 基于动态代理**：
- 实现了接口 → **JDK Proxy**
- 未实现接口 → **CGLIB** 生成子类

### Spring AOP 和 AspectJ 的区别？

- **Spring AOP**：运行时增强，基于代理
- **AspectJ**：编译时增强，基于字节码操作，功能更强大，切面多时性能更好

### AspectJ 通知类型

- **Before**：目标方法调用前触发
- **After**：目标方法调用后触发
- **AfterReturning**：方法返回结果后触发
- **AfterThrowing**：方法抛出异常后触发
- **Around**：环绕通知，可编程式控制目标方法调用

## Spring MVC

### Spring MVC 工作原理

1. 客户端发送请求 → **DispatcherServlet** 拦截
2. DispatcherServlet 调用 **HandlerMapping** 查找 Handler
3. 调用 **HandlerAdapter** 适配执行 Handler
4. Handler 返回 **ModelAndView** 给 DispatcherServlet
5. **ViewResolver** 根据逻辑 View 查找实际 View
6. DispatcherServlet 把 Model 传给 View（视图渲染）
7. 返回 View 给客户端

### 统一异常处理

使用 **`@ControllerAdvice` + `@ExceptionHandler`** 注解，给所有 Controller 织入异常处理逻辑（AOP）。

## Spring 设计模式

| 设计模式 | 应用 |
|---------|------|
| **工厂模式** | BeanFactory、ApplicationContext 创建 bean |
| **代理模式** | Spring AOP |
| **单例模式** | Bean 默认单例 |
| **模板方法** | JdbcTemplate、HibernateTemplate |
| **观察者模式** | Spring 事件驱动模型 |
| **适配器模式** | Spring AOP 的 Advice、Spring MVC 的 Controller |

## Spring 事务

### 事务传播行为

| 传播行为 | 说明 |
|---------|------|
| **REQUIRED** | 如果当前存在事务则加入，否则创建新事务（默认） |
| **REQUIRES_NEW** | 创建新事务，如果当前存在事务则挂起 |
| **NESTED** | 如果当前存在事务则创建嵌套事务 |
| **MANDATORY** | 如果当前存在事务则加入，否则抛异常 |

### @Transactional(rollbackFor = Exception.class)

默认情况下，事务只在遇到 **RuntimeException** 时回滚。加上 `rollbackFor=Exception.class` 后，遇到**非运行时异常**也会回滚。
