---
title: "TypeScript类、模块与声明文件：类型生态全貌"
date: 2026-06-28 14:00:00
tags:
  - TypeScript
  - JavaScript
  - 前端
categories:
  - 前端开发
---

## 前言

你已经会 JS 的 `class`、`import`、`export`。TS 在此基础上增加了访问修饰符、抽象类、类型导入，以及一个 JS 完全没有的概念——声明文件（`.d.ts`）。声明文件是 TS 与整个 JS 生态协作的桥梁，理解它才能理解 `@types/*` 是怎么回事。本文逐一拆解这些能力。

<!-- more -->

## 一、TS 中的类增强

JS 已经有 `class`，TS 增加了三个关键能力：访问修饰符、抽象类和参数属性。

### 1.1 访问修饰符

```typescript
class User {
  public name: string        // 公开，外部可访问（默认）
  private password: string   // 私有，仅类内部可访问
  protected role: string     // 受保护，类内部 + 子类可访问

  constructor(name: string, password: string, role: string) {
    this.name = name
    this.password = password
    this.role = role
  }
}

const user = new User("Alice", "123", "admin")
user.name       // ✅
user.password   // ❌ 私有属性，外部不可访问
user.role       // ❌ 受保护属性，外部不可访问
```

| 修饰符 | 类内部 | 子类 | 外部 |
|--------|--------|------|------|
| `public` | ✅ | ✅ | ✅ |
| `protected` | ✅ | ✅ | ❌ |
| `private` | ✅ | ❌ | ❌ |

### 1.2 readonly 属性

```typescript
class Config {
  readonly apiUrl: string

  constructor(url: string) {
    this.apiUrl = url
  }
}

const config = new Config("https://api.example.com")
config.apiUrl  // ✅ 读取
config.apiUrl = "xxx"  // ❌ 只读，不能修改
```

### 1.3 参数属性

TS 的语法糖，在构造函数参数前加修饰符，自动声明并赋值属性：

```typescript
// 普通写法
class User {
  public name: string
  private age: number

  constructor(name: string, age: number) {
    this.name = name
    this.age = age
  }
}

// 参数属性简写（效果完全一样）
class User {
  constructor(
    public name: string,
    private age: number,
  ) {}
}
```

参数属性让类定义更简洁，但可读性稍差——构造函数签名不再只反映"参数"，还暗含"属性声明"。

### 1.4 抽象类

抽象类不能实例化，只能被继承，用于定义"规范"：

```typescript
abstract class Shape {
  abstract area(): number     // 抽象方法：子类必须实现
  abstract perimeter(): number

  // 普通方法：子类可以直接用
  describe(): string {
    return `面积: ${this.area()}, 周长: ${this.perimeter()}`
  }
}

class Circle extends Shape {
  constructor(private radius: number) {
    super()
  }

  area(): number {
    return Math.PI * this.radius ** 2
  }

  perimeter(): number {
    return 2 * Math.PI * this.radius
  }
}

const circle = new Circle(10)
circle.describe()  // ✅
// new Shape()     // ❌ 抽象类不能实例化
```

### 1.5 implements 实现接口

类可以实现一个或多个接口，强制它拥有接口定义的所有属性和方法：

```typescript
interface Printable {
  print(): void
}

interface Serializable {
  serialize(): string
}

class Document implements Printable, Serializable {
  constructor(private content: string) {}

  print(): void {
    console.log(this.content)
  }

  serialize(): string {
    return JSON.stringify({ content: this.content })
  }
}
```

## 二、模块系统

TS 使用 ES Module 语法（`import` / `export`），与 JS 基本一致，但增加了**类型导入**。

### 2.1 基本导入导出

```typescript
// utils.ts
export function add(a: number, b: number): number {
  return a + b
}

export interface User {
  name: string
  age: number
}

export default class Logger {
  log(msg: string): void {
    console.log(msg)
  }
}

// main.ts
import Logger, { add, User } from "./utils"
```

### 2.2 类型导入（import type）

TS 3.8+ 支持 `import type`，只导入类型信息，编译后会被完全擦除：

```typescript
// 普通导入：运行时保留（会生成 require/import 语句）
import { User } from "./types"

// 类型导入：编译后完全消失
import type { User } from "./types"
```

**为什么要用 `import type`？**

1. **避免运行时开销**：如果 `types.ts` 只有类型定义，普通导入会生成一个空的 `require` 调用
2. **防止循环依赖**：类型导入在编译后不存在，不会引发运行时循环引用问题
3. **意图清晰**：告诉读者"这里只用到了类型"

```typescript
// 推荐：tsconfig.json 中开启
{
  "compilerOptions": {
    "verbatimModuleSyntax": true  // 强制使用 import type
  }
}
```

### 2.3 重新导出

```typescript
// barrel 模式：统一导出
// types/index.ts
export type { User } from "./user"
export type { Post } from "./post"
export type { Comment } from "./comment"

// 使用时一行搞定
import type { User, Post, Comment } from "./types"
```

## 三、声明文件（.d.ts）

声明文件是 TS 类型系统的核心机制——它告诉 TS "这个 JS 代码有哪些类型"，但不包含任何实现。

### 3.1 为什么需要声明文件？

JS 库没有类型信息，TS 不知道它导出了什么。声明文件就是"翻译官"：

```
lodash（纯 JS）  →  @types/lodash（声明文件）  →  TS 知道 _.map 的类型
```

### 3.2 declare 关键字

`declare` 告诉 TS："这个东西存在于运行时，我来描述它的类型"：

```typescript
// declare 变量
declare const API_URL: string

// declare 函数
declare function fetch(url: string): Promise<Response>

// declare 类
declare class Promise<T> {
  then<U>(fn: (value: T) => U): Promise<U>
}
```

`declare` 不会生成任何 JS 代码，纯粹是类型声明。

### 3.3 声明文件的写法

声明文件的扩展名是 `.d.ts`，内容全是类型声明，没有实现：

```typescript
// types/my-lib.d.ts

// 声明一个模块
declare module "my-lib" {
  export function doSomething(x: number): string
  export interface Config {
    timeout: number
    retries: number
  }
  export default function init(config: Config): void
}
```

有了这个文件，使用 `my-lib` 时就有完整类型：

```typescript
import init, { doSomething, Config } from "my-lib"

init({ timeout: 5000, retries: 3 })  // ✅ 有类型提示
doSomething(42)                        // ✅ 返回 string
```

### 3.4 全局声明

有些值不是通过模块导入的，而是全局可用的（比如浏览器 API），用 `declare global`：

```typescript
// types/global.d.ts
export {}  // 让文件成为模块

declare global {
  // 扩展全局变量
  interface Window {
    __APP_CONFIG__: {
      apiUrl: string
      env: "dev" | "prod"
    }
  }
}

// 使用
window.__APP_CONFIG__.apiUrl  // ✅ 有类型提示
```

### 3.5 常见的全局声明场景

```typescript
// 环境变量（Vite）
declare const import.meta.env: {
  readonly MODE: string
  readonly BASE_URL: string
  readonly DEV: boolean
  readonly PROD: boolean
}

// CSS Modules
declare module "*.module.css" {
  const classes: Record<string, string>
  export default classes
}

// 静态资源
declare module "*.svg" {
  const src: string
  export default src
}

declare module "*.png" {
  const src: string
  export default src
}
```

## 四、@types/* 生态

### 4.1 DefinitelyTyped

[DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped) 是社区维护的类型声明仓库。当你安装 `@types/lodash` 时，实际上是在安装 `lodash` 的 `.d.ts` 文件：

```bash
npm install lodash          # JS 库
npm install -D @types/lodash # 类型声明
```

安装后 TS 自动识别，不需要额外配置。

### 4.2 什么时候需要 @types？

| 情况 | 是否需要 @types |
|------|----------------|
| 库自带类型（如 Vue 3、Axios） | 不需要 |
| 纯 JS 库（如 Lodash、Express） | 需要 |
| 库自带但不完整 | 可以自己补 `.d.ts` |

检查一个库是否自带类型：看它的 `package.json` 里有没有 `types` 或 `typings` 字段，或者包里有没有 `.d.ts` 文件。

### 4.3 自己写类型补丁

如果一个库没有 `@types/*`，或者自带类型有错误，可以在项目中自己补：

```typescript
// types/some-lib.d.ts
declare module "some-lib" {
  export function doStuff(input: string): number
  export const version: string
}
```

然后确保 `tsconfig.json` 包含这个目录：

```json
{
  "compilerOptions": {
    "typeRoots": ["./types", "./node_modules/@types"]
  }
}
```

## 五、模块解析策略

`tsconfig.json` 中的 `moduleResolution` 决定 TS 如何找到模块：

| 策略 | 适用场景 | 查找方式 |
|------|---------|---------|
| `node` | Node.js 项目 | 按 Node 的 `require` 规则查找 |
| `bundler` | Vite / Webpack 等打包器 | 更宽松，支持 `package.json` 的 `exports` |
| `nodenext` | Node.js ESM 项目 | 最严格，支持 `.mts` / `.cts` |

```json
// Vite / Vue 项目推荐
{
  "compilerOptions": {
    "moduleResolution": "bundler"
  }
}

// Node.js 项目推荐
{
  "compilerOptions": {
    "moduleResolution": "nodenext",
    "module": "nodenext"
  }
}
```

## 六、实战：为一个没有类型的 npm 包写声明

假设你用了一个叫 `fancy-logger` 的包，它没有类型：

```bash
# 先看它导出了什么
node -e "console.log(Object.keys(require('fancy-logger')))"
```

```typescript
// types/fancy-logger.d.ts
declare module "fancy-logger" {
  interface LoggerOptions {
    level?: "debug" | "info" | "warn" | "error"
    prefix?: string
    timestamp?: boolean
  }

  class Logger {
    constructor(options?: LoggerOptions)
    debug(msg: string): void
    info(msg: string): void
    warn(msg: string): void
    error(msg: string): void
  }

  export default Logger
  export type { LoggerOptions }
}
```

使用时就有完整类型了：

```typescript
import Logger from "fancy-logger"

const logger = new Logger({ level: "info", timestamp: true })
logger.info("hello")  // ✅ 有类型提示
logger.foo("bar")     // ❌ 编译报错：foo 不存在
```

## 总结

1. **TS 类** 增加了 `public/private/protected`、`readonly`、`abstract`、`implements`
2. **参数属性** `constructor(public name: string)` 是简洁写法
3. **`import type`** 只导入类型，编译后消失，避免运行时开销和循环依赖
4. **声明文件 `.d.ts`** 用 `declare` 描述 JS 代码的类型，不包含实现
5. **`@types/*`** 是社区维护的类型声明，纯 JS 库通常需要安装
6. **自己写 `.d.ts`** 可以为没有类型的库补充类型
7. **`moduleResolution`** 根据项目类型选择 `bundler` 或 `nodenext`

下一篇是最后一篇——把 TS 落地到真实项目中：tsconfig 配置、Vue/React 集成、常见报错排查。
