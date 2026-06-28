---
title: "TypeScript入门：类型系统基石"
date: 2026-06-28 10:00:00
tags:
  - TypeScript
  - JavaScript
  - 前端
categories:
  - 前端开发
---

## 前言

你已经会 JavaScript，知道 `let`、`const`、函数、数组、对象。TypeScript 在 JS 之上加了一层**类型系统**——不改变运行时行为，只在编写阶段帮你抓错。本文从零开始，带你搭建 TS 环境，掌握类型注解、基本类型、特殊类型和严格模式，学完就能把现有 JS 文件改成 `.ts` 并通过编译。

<!-- more -->

## 一、安装与初始化

```bash
# 全局安装 TypeScript 编译器
npm install -g typescript

# 验证安装
tsc --version

# 初始化 tsconfig.json（TS 项目的配置文件）
tsc --init
```

`tsconfig.json` 生成后，先关注两个字段：

```json
{
  "compilerOptions": {
    "target": "ES2020",      // 编译目标：输出哪个版本的 JS
    "strict": true           // 开启严格模式（推荐）
  }
}
```

编译并运行：

```bash
# 编译：.ts → .js
tsc

# 或者一步到位用 ts-node 直接运行
npx ts-node index.ts
```

## 二、类型注解：TS 的核心语法

TS 最大的变化就是可以在变量、参数、返回值后面加 `: 类型`：

```typescript
// 变量注解
let name: string = "Alice"
let age: number = 25
let isStudent: boolean = true

// 函数参数和返回值注解
function add(a: number, b: number): number {
  return a + b
}
```

**如果你不写注解，TS 也会自动推断类型**（类型推断）：

```typescript
let x = 42        // TS 推断 x 是 number
x = "hello"       // ❌ 报错：不能将 string 赋值给 number
```

所以很多时候不需要手写注解，TS 比你想象的聪明。但**函数参数**必须手写，因为 TS 无法从调用处推断参数类型。

## 三、基本类型一览

### 3.1 原始类型

```typescript
// 与 JS 一一对应
let str: string = "hello"
let num: number = 42          // 包括整数、浮点、NaN、Infinity
let bool: boolean = true
let n: null = null
let u: undefined = undefined

// ES2020 新增
let big: bigint = 100n
let sym: symbol = Symbol("id")
```

### 3.2 数组

```typescript
// 两种写法等价
let nums: number[] = [1, 2, 3]
let strs: Array<string> = ["a", "b", "c"]

// 混合类型数组（用联合类型，后面会详细讲）
let mixed: (string | number)[] = [1, "two", 3]
```

### 3.3 元组（Tuple）

元组是**固定长度、固定类型**的数组：

```typescript
// 第一个必须是 string，第二个必须是 number
let pair: [string, number] = ["Alice", 25]

// 常见用途：useState 的返回值
let state: [number, (n: number) => void] = [0, () => {}]
```

元组和数组的区别：

```typescript
let arr: number[] = [1, 2, 3]     // 长度不固定，类型统一
let tup: [string, number] = ["a", 1]  // 长度固定，类型按位置对应

tup[0]  // 类型是 string
tup[1]  // 类型是 number
tup[2]  // ❌ 报错：索引越界
```

### 3.4 枚举（enum）

JS 没有枚举，TS 新增了这个特性：

```typescript
// 数字枚举（默认从 0 开始自增）
enum Direction {
  Up,      // 0
  Down,    // 1
  Left,    // 2
  Right,   // 3
}

let dir: Direction = Direction.Up
console.log(dir)  // 0

// 字符串枚举（更常用，值不会变）
enum Status {
  Active = "ACTIVE",
  Inactive = "INACTIVE",
  Pending = "PENDING",
}

let s: Status = Status.Active
console.log(s)  // "ACTIVE"
```

**枚举的坑：** 数字枚举是双向映射，字符串枚举是单向的：

```typescript
enum Color { Red, Green, Blue }

Color.Red       // 0
Color[0]        // "Red"（数字枚举支持反向查找）

enum Fruit { Apple = "APPLE" }
Fruit.Apple     // "APPLE"
Fruit["APPLE"]  // ❌ 不支持反向查找
```

实际开发中推荐用**字符串枚举**或**常量对象 + as const**，数字枚举的隐式自增容易踩坑。

## 四、特殊类型：any、unknown、void、never

这四个是 TS 特有的类型，理解它们的差异是写好 TS 的关键。

### 4.1 any：放弃类型检查

```typescript
let x: any = 42
x = "hello"     // ✅ 不报错
x.foo()         // ✅ 不报错（但运行时会炸）
```

`any` 等于告诉 TS："别管我"。它会**跳过所有类型检查**，一个 `any` 就能污染周围的类型推断。初学迁移时可以先用，但最终目标是消灭所有 `any`。

### 4.2 unknown：安全版 any

```typescript
let x: unknown = 42
x = "hello"     // ✅ 赋值没问题

// 但使用前必须先检查类型
x.toUpperCase()  // ❌ 报错：unknown 上不能调用方法

if (typeof x === "string") {
  x.toUpperCase()  // ✅ 类型收窄后可以使用
}
```

**规则：`unknown` 只能赋值给 `unknown` 或 `any`，使用前必须先判断类型。** 这就是它比 `any` 安全的原因。

### 4.3 void：函数没有返回值

```typescript
function log(msg: string): void {
  console.log(msg)
  // 没有 return，或者 return; 不返回值
}

let result: void = log("hi")  // result 是 undefined
```

`void` 主要用于函数返回值声明。与 JS 中不写 `return` 的行为一致——函数默认返回 `undefined`。

### 4.4 never：永远不会结束

```typescript
// 永远抛出异常，不会正常返回
function throwError(msg: string): never {
  throw new Error(msg)
}

// 永远不会结束的循环
function infiniteLoop(): never {
  while (true) {}
}
```

`void` 是"正常结束但不返回值"，`never` 是"根本不会结束"。实际开发中 `never` 最常出现在**穷尽检查**：

```typescript
type Shape = "circle" | "square" | "triangle"

function area(shape: Shape): number {
  switch (shape) {
    case "circle": return Math.PI * 10
    case "square": return 100
    case "triangle": return 50
    default:
      // 如果 Shape 新增了类型但忘记处理，这里会编译报错
      const _exhaustive: never = shape
      return _exhaustive
  }
}
```

## 五、类型推断 vs 显式注解

TS 的类型推断很强，不是所有地方都需要手写类型：

```typescript
// ✅ 推断就够了
let count = 0                // 推断为 number
let items = [1, 2, 3]        // 推断为 number[]
let user = { name: "Alice" } // 推断为 { name: string }

// ✅ 需要手写的地方
function greet(name: string): string {  // 参数必须写
  return `Hello, ${name}`
}

// ✅ 返回值类型可以省略（TS 会推断），但写了更清晰
function add(a: number, b: number) {  // 返回值推断为 number
  return a + b
}
```

**经验法则：**
- 变量声明：能推断就不写
- 函数参数：必须写
- 函数返回值：复杂函数建议写，简单函数可省
- 公共 API（导出的函数/类型）：建议写，作为文档用途

## 六、严格模式：tsconfig.json 的核心开关

`strict: true` 等于同时开启以下所有严格检查：

| 选项 | 作用 | 单独开启时的效果 |
|------|------|-----------------|
| `strictNullChecks` | `null` 和 `undefined` 不能赋值给其他类型 | 最重要，单独开也值 |
| `noImplicitAny` | 禁止隐式 `any`（参数必须有类型） | 消灭"漏网之鱼" |
| `strictFunctionTypes` | 函数参数类型严格匹配 | 防止回调类型不安全 |
| `strictBindCallApply` | `bind/call/apply` 参数类型检查 | 消除动态调用的隐患 |
| `strictPropertyInitialization` | 类属性必须在构造函数中初始化 | 防止未初始化的属性 |
| `noImplicitThis` | 禁止隐式 `this` 类型 | 防止 `this` 指向错误 |
| `alwaysStrict` | 输出文件加 `"use strict"` | 与 JS 的 strict mode 对齐 |

**迁移建议：** 不要一次性开 `strict: true`，而是逐步开启：

```json
{
  "compilerOptions": {
    "strict": false,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

先开这两个收益最大，其余的等项目稳定后再逐步打开。

## 七、类型断言：你比 TS 更了解类型

有时候你比编译器更清楚一个值的类型：

```typescript
// DOM 操作：getElementById 返回 HTMLElement | null
// 但你确定它是 input 元素
const input = document.getElementById("myInput") as HTMLInputElement
input.value = "hello"

// 另一种写法（JSX 中不能用）
const input = <HTMLInputElement>document.getElementById("myInput")
```

**类型断言不是类型转换**，它只是告诉编译器"相信我，这个值是这个类型"。运行时不会做任何转换。

```typescript
const str = "hello"
const num = str as number  // ✅ 编译通过（TS 信任你）
console.log(num.toFixed(2))  // ❌ 运行时报错：str 没有 toFixed 方法
```

断言用错了运行时照样炸，所以只在你**确实知道类型**时使用（比如 DOM 操作、API 响应解析）。

## 八、与 JS 的关键差异速查

| 场景 | JavaScript | TypeScript |
|------|-----------|------------|
| 声明变量 | `let x = 42` | `let x: number = 42`（可省略注解） |
| 函数参数 | `function add(a, b)` | `function add(a: number, b: number)` |
| 空值安全 | `obj.name` 可能炸 | `strictNullChecks` 强制处理 null |
| 枚举 | 无 | `enum Status { Active, Inactive }` |
| 元组 | 无（用数组模拟） | `let t: [string, number] = ["a", 1]` |
| 类型断言 | 无 | `value as string` |
| any | 所有值都是 any | 需要显式声明，且不推荐使用 |

## 总结

TypeScript 的类型系统不是要你写更多代码，而是让你**在编写阶段就发现错误**。核心要点：

1. **类型注解**用 `: 类型` 语法，但很多地方 TS 能自动推断
2. **基本类型**与 JS 一一对应，新增了元组和枚举
3. **any 是逃生舱**，unknown 是安全替代，void 和 never 用于函数返回值
4. **strict 模式**建议逐步开启，`strictNullChecks` + `noImplicitAny` 优先
5. **类型断言**是"你比 TS 更懂"时的工具，但要谨慎使用

下一篇我们将学习 `interface` 和 `type`，学会用类型描述复杂的数据结构。
