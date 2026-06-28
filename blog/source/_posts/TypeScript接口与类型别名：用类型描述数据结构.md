---
title: "TypeScript接口与类型别名：用类型描述数据结构"
date: 2026-06-28 11:00:00
tags:
  - TypeScript
  - JavaScript
  - 前端
categories:
  - 前端开发
---

## 前言

上一篇学了基本类型，但实际开发中你面对的不是孤立的 `number` 或 `string`，而是**对象**——API 返回的 JSON、组件的 Props、配置项。TypeScript 提供了 `interface` 和 `type` 两个工具来描述这些数据结构。本文带你掌握它们的用法、区别，以及联合类型、交叉类型、类型守卫等配套能力。

<!-- more -->

## 一、interface：定义对象的形状

`interface` 描述一个对象**应该有哪些属性、每个属性是什么类型**：

```typescript
interface User {
  name: string
  age: number
  email: string
}

const user: User = {
  name: "Alice",
  age: 25,
  email: "alice@example.com",
}
```

对象**多属性少属性都会报错**：

```typescript
const user: User = {
  name: "Alice",
  age: 25,
  // ❌ 缺少 email 属性
}

const user: User = {
  name: "Alice",
  age: 25,
  email: "alice@example.com",
  phone: "123",  // ❌ 多余属性检查
}
```

### 1.1 可选属性

用 `?` 标记不是必须存在的属性：

```typescript
interface User {
  name: string
  age: number
  email?: string  // 可选
}

const user: User = {
  name: "Alice",
  age: 25,
  // 不写 email 也合法
}
```

### 1.2 只读属性

用 `readonly` 标记初始化后不能修改的属性：

```typescript
interface Config {
  readonly apiUrl: string
  readonly timeout: number
}

const config: Config = {
  apiUrl: "https://api.example.com",
  timeout: 5000,
}

config.apiUrl = "xxx"  // ❌ 报错：无法修改只读属性
```

### 1.3 索引签名

当你不确定对象会有哪些 key，但知道 key 和 value 的类型时：

```typescript
interface StringMap {
  [key: string]: string
}

const headers: StringMap = {
  "Content-Type": "application/json",
  "Authorization": "Bearer token",
}
```

索引签名可以和确定属性共存：

```typescript
interface ApiResponse {
  code: number
  message: string
  [key: string]: unknown  // 其他不确定的字段
}
```

## 二、type：类型别名

`type` 给一个类型起个名字，能力比 `interface` 更广——不仅能定义对象，还能定义**联合类型、交叉类型、原始类型别名**等：

```typescript
// 对象类型（与 interface 等价）
type User = {
  name: string
  age: number
}

// 原始类型别名（interface 做不到）
type ID = string | number
type Status = "active" | "inactive" | "pending"

// 元组别名
type Point = [number, number]
```

## 三、interface vs type：怎么选？

两者大部分场景可以互换，但有细微差异：

| 对比点 | `interface` | `type` |
|--------|------------|--------|
| 定义对象 | ✅ | ✅ |
| 联合类型 | ❌ | ✅ `type A = string \| number` |
| 交叉类型 | ❌ | ✅ `type C = A & B` |
| 原始别名 | ❌ | ✅ `type ID = string` |
| 继承/扩展 | `extends` 继承 | `&` 交叉 |
| 声明合并 | ✅ 同名自动合并 | ❌ 同名报错 |
| implements | ✅ 类可以实现 | ✅ 类可以实现 |

**经验法则：**
- 定义对象结构 → 用 `interface`（可扩展、声明合并）
- 定义联合类型、元组、工具类型 → 用 `type`
- 拿不准就用 `type`，它能力更全面

## 四、联合类型：A 或 B

用 `|` 表示一个值可以是多种类型之一：

```typescript
// 变量可以是 string 或 number
let id: string | number
id = "abc"   // ✅
id = 123     // ✅
id = true    // ❌

// 函数参数接受多种类型
function printId(id: string | number): void {
  console.log(id)
}
```

联合类型的关键问题：**怎么安全地使用？**

```typescript
function printId(id: string | number): void {
  console.log(id.toUpperCase())  // ❌ 报错：number 没有 toUpperCase

  // 解决方案：类型收窄
  if (typeof id === "string") {
    console.log(id.toUpperCase())  // ✅ 这里 id 被收窄为 string
  } else {
    console.log(id.toFixed(2))     // ✅ 这里 id 被收窄为 number
  }
}
```

## 五、字面量类型：精确到具体的值

类型不仅可以是宽泛的 `string`，还可以是具体的值：

```typescript
type Direction = "up" | "down" | "left" | "right"

let dir: Direction = "up"    // ✅
let dir: Direction = "top"   // ❌ 不在字面量联合中

type StatusCode = 200 | 301 | 404 | 500

type BooleanValue = true | false  // 等价于 boolean
```

字面量类型常用于函数参数：

```typescript
function setAlignment(align: "left" | "center" | "right"): void {
  // ...
}

setAlignment("left")    // ✅
setAlignment("top")     // ❌ 编译报错，IDE 会提示合法选项
```

### const 断言

`as const` 让变量变成只读的字面量类型：

```typescript
// 普通赋值：类型被拓宽为 string
let name = "Alice"       // 类型是 string

// const 施言：类型锁定为 "Alice"
const name = "Alice"     // 类型是 "Alice"（const 自动收窄）

// 对象用 as const：所有属性变为 readonly + 字面量
const config = {
  apiUrl: "https://api.example.com",
  method: "GET",
} as const

// 等价于：
// { readonly apiUrl: "https://api.example.com"; readonly method: "GET" }
```

`as const` 在定义常量映射时特别有用：

```typescript
const ROUTES = {
  home: "/",
  about: "/about",
  contact: "/contact",
} as const

type Route = keyof typeof ROUTES  // "home" | "about" | "contact"
```

## 六、交叉类型：A 且 B

用 `&` 把多个类型合并为一个：

```typescript
type HasName = { name: string }
type HasAge = { age: number }

// 同时拥有 name 和 age
type Person = HasName & HasAge

const p: Person = {
  name: "Alice",
  age: 25,
}
```

交叉类型与联合类型的区别：

```typescript
// 联合：A 或 B（满足一个就行）
type A = { name: string } | { age: number }
// 可以是 { name: "Alice" } 或 { age: 25 } 或两者都有

// 交叉：A 且 B（必须同时满足）
type B = { name: string } & { age: number }
// 必须同时有 name 和 age
```

实际场景：给已有类型扩展属性

```typescript
interface User {
  name: string
  email: string
}

// 给 User 加一个 token 字段（不修改原接口）
type AuthenticatedUser = User & {
  token: string
  expiresAt: Date
}
```

## 七、类型守卫：运行时的类型收窄

类型守卫让你在运行时判断类型，TS 会自动收窄后续代码中的类型：

### 7.1 typeof 守卫

```typescript
function format(value: string | number): string {
  if (typeof value === "string") {
    return value.toUpperCase()       // value 被收窄为 string
  } else {
    return value.toFixed(2)          // value 被收窄为 number
  }
}
```

### 7.2 instanceof 守卫

```typescript
function printDate(value: string | Date): void {
  if (value instanceof Date) {
    console.log(value.getFullYear())  // Date 类型
  } else {
    console.log(value.toUpperCase())  // string 类型
  }
}
```

### 7.3 in 守卫

```typescript
interface Fish { swim(): void }
interface Bird { fly(): void }

function move(animal: Fish | Bird): void {
  if ("swim" in animal) {
    animal.swim()   // Fish 类型
  } else {
    animal.fly()    // Bird 类型
  }
}
```

### 7.4 可辨识联合（Discriminated Union）

这是 TS 最强大的模式之一——给每个类型一个共同的"标签"属性：

```typescript
interface Circle {
  kind: "circle"
  radius: number
}

interface Rectangle {
  kind: "rectangle"
  width: number
  height: number
}

interface Triangle {
  kind: "triangle"
  base: number
  height: number
}

type Shape = Circle | Rectangle | Triangle

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2
    case "rectangle":
      return shape.width * shape.height
    case "triangle":
      return (shape.base * shape.height) / 2
  }
}
```

`kind` 就是辨识标签——TS 根据它的值自动收窄 `shape` 的类型，你在每个 `case` 里都能安全访问对应类型的属性。

## 八、类型断言的两种形式

上一篇简单提过，这里对比两种写法：

```typescript
// as 语法（推荐，JSX 中可用）
const input = document.getElementById("myInput") as HTMLInputElement

// 尖括号语法（JSX/TSX 中不能用，会和标签冲突）
const input = <HTMLInputElement>document.getElementById("myInput")
```

### 非空断言

当你确定一个值不是 `null` 或 `undefined` 时，用 `!`：

```typescript
const el = document.getElementById("root")  // 类型是 HTMLElement | null

// 方式一：类型守卫
if (el) {
  el.innerHTML = "hello"
}

// 方式二：非空断言（你确信它存在）
el!.innerHTML = "hello"
```

非空断言要谨慎使用——如果 `el` 真的是 `null`，运行时照样报错。

## 九、实战：API 响应的类型定义

综合运用以上知识，定义一个完整的 API 响应类型：

```typescript
// 基础响应结构
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 用户相关类型
interface User {
  id: number
  name: string
  email: string
  role: "admin" | "user" | "guest"  // 字面量联合
  profile?: {                        // 可选属性
    avatar: string
    bio: string
  }
}

// 分页列表
interface PaginatedList<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// 具体的 API 响应类型
type UserListResponse = ApiResponse<PaginatedList<User>>
type UserDetailResponse = ApiResponse<User>

// 使用
async function fetchUsers(): Promise<UserListResponse> {
  const res = await fetch("/api/users")
  return res.json()
}

const result = await fetchUsers()
result.data.items[0].name  // ✅ 完整的类型提示
result.data.items[0].profile?.avatar  // ✅ 可选属性自动处理
```

## 总结

本篇的核心知识点：

1. **interface** 定义对象结构，支持可选 `?`、只读 `readonly`、索引签名
2. **type** 能力更广，可以定义联合类型、交叉类型、原始类型别名
3. **联合类型** `A | B` 表示"或"，**交叉类型** `A & B` 表示"且"
4. **字面量类型**精确到具体的值，配合 `as const` 锁定类型
5. **类型守卫**（typeof / instanceof / in / 可辨识联合）让 TS 在运行时收窄类型
6. **类型断言** `as` 是最后手段，非空断言 `!` 要谨慎使用

下一篇我们将深入函数的类型化——参数、返回值、重载、this 绑定。
