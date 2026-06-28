---
title: "TypeScript泛型与工具类型：类型参数化与内置工具"
date: 2026-06-28 13:00:00
tags:
  - TypeScript
  - JavaScript
  - 前端
categories:
  - 前端开发
---

## 前言

上一篇用泛型函数开了个头，本篇全面展开泛型的完整能力——泛型接口、泛型类、泛型约束，然后介绍 TS 内置的工具类型（`Partial`、`Pick`、`Omit`、`Record` 等），最后带你理解条件类型、`infer` 和映射类型的原理。学完这篇，你能看懂 Vue 3、React 等框架源码中的复杂泛型定义。

<!-- more -->

## 一、泛型接口

接口也可以带类型参数：

```typescript
// 泛型接口：API 响应的通用结构
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 使用时指定 T 的具体类型
interface User {
  id: number
  name: string
}

const response: ApiResponse<User> = {
  code: 200,
  message: "ok",
  data: { id: 1, name: "Alice" },
}
```

泛型接口配合函数使用：

```typescript
async function fetchJson<T>(url: string): Promise<ApiResponse<T>> {
  const res = await fetch(url)
  return res.json()
}

// 使用时指定 T
const userRes = await fetchJson<User>("/api/user/1")
userRes.data.name  // ✅ data 是 User 类型
```

### 带默认值的泛型参数

```typescript
interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

// 不指定 T 时，默认是 unknown
const res: ApiResponse = {
  code: 200,
  message: "ok",
  data: "anything",  // data 类型是 unknown
}
```

## 二、泛型类

类也可以用泛型，常见于容器类、服务类：

```typescript
class DataStore<T> {
  private items: T[] = []

  add(item: T): void {
    this.items.push(item)
  }

  getById(index: number): T | undefined {
    return this.items[index]
  }

  getAll(): T[] {
    return [...this.items]
  }
}

// 使用
const userStore = new DataStore<User>()
userStore.add({ id: 1, name: "Alice" })
userStore.add({ id: 2, name: "Bob" })

const user = userStore.getById(0)  // 类型是 User | undefined
```

类也可以有多个泛型参数：

```typescript
class KeyValuePair<K, V> {
  constructor(public key: K, public value: V) {}
}

const pair = new KeyValuePair("name", "Alice")  // KeyValuePair<string, string>
```

## 三、泛型约束详解

`extends` 让类型参数满足特定条件：

### 3.1 约束为有特定属性的对象

```typescript
// T 必须有 length 属性
interface HasLength {
  length: number
}

function logLength<T extends HasLength>(value: T): void {
  console.log(value.length)
}

logLength("hello")     // ✅
logLength([1, 2, 3])   // ✅
logLength({ length: 5 }) // ✅
logLength(42)           // ❌
```

### 3.2 约束为对象的 key

```typescript
// K 必须是 T 的 key 之一
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}

const user = { name: "Alice", age: 25 }

getProperty(user, "name")  // ✅ 返回类型是 string
getProperty(user, "age")   // ✅ 返回类型是 number
getProperty(user, "email") // ❌ "email" 不是 user 的 key
```

`keyof T` 获取对象所有 key 的联合类型，配合 `extends` 可以精确约束属性访问。

### 3.3 约束为构造函数

```typescript
interface Constructor<T> {
  new (...args: any[]): T
}

function createInstance<T>(ctor: Constructor<T>): T {
  return new ctor()
}
```

## 四、内置工具类型

TS 内置了一系列工具类型，本质都是泛型 + 映射类型的组合。掌握它们能大幅减少重复的类型定义。

### 4.1 Partial\<T>：所有属性变为可选

```typescript
interface User {
  id: number
  name: string
  email: string
}

// 所有属性都变成可选
type PartialUser = Partial<User>
// 等价于：
// { id?: number; name?: string; email?: string }

// 常见用途：更新操作只需要传需要改的字段
function updateUser(id: number, updates: Partial<User>): void {
  // ...
}

updateUser(1, { name: "Bob" })  // ✅ 只更新 name
```

### 4.2 Required\<T>：所有属性变为必选

```typescript
interface Config {
  apiUrl?: string
  timeout?: number
}

type RequiredConfig = Required<Config>
// 等价于：
// { apiUrl: string; timeout: number }
```

### 4.3 Readonly\<T>：所有属性变为只读

```typescript
type ReadonlyUser = Readonly<User>
// 等价于：
// { readonly id: number; readonly name: string; readonly email: string }

const user: ReadonlyUser = { id: 1, name: "Alice", email: "a@b.com" }
user.name = "Bob"  // ❌ 只读属性不能修改
```

### 4.4 Pick\<T, K>：挑选部分属性

```typescript
// 从 User 中只取 name 和 email
type UserPreview = Pick<User, "name" | "email">
// 等价于：
// { name: string; email: string }

// 常见用途：列表页只需要部分字段
function getUserPreview(): Pick<User, "name" | "email"> {
  // ...
}
```

### 4.5 Omit\<T, K>：排除部分属性

```typescript
// 从 User 中排除 id（与 Pick 相反）
type CreateUserInput = Omit<User, "id">
// 等价于：
// { name: string; email: string }

// 常见用途：创建时不需要 id（由后端生成）
function createUser(input: CreateUserInput): User {
  return { id: Date.now(), ...input }
}
```

### 4.6 Record\<K, V>：构造键值对类型

```typescript
// key 是 string，value 是 number
type Scores = Record<string, number>

const scores: Scores = {
  math: 90,
  english: 85,
}

// 用字面量联合做 key
type Role = "admin" | "user" | "guest"
type RolePermissions = Record<Role, string[]>

const permissions: RolePermissions = {
  admin: ["read", "write", "delete"],
  user: ["read", "write"],
  guest: ["read"],
}
```

### 4.7 ReturnType\<T> 和 Parameters\<T>

从函数类型中提取返回值类型和参数类型：

```typescript
function createUser(name: string, age: number) {
  return { name, age, createdAt: new Date() }
}

// 提取返回值类型
type User = ReturnType<typeof createUser>
// { name: string; age: number; createdAt: Date }

// 提取参数类型（返回元组）
type Params = Parameters<typeof createUser>
// [string, number]

// 提取单个参数
type FirstParam = Parameters<typeof createUser>[0]  // string
```

### 4.8 Exclude\<T, U> 和 Extract\<T, U>

从联合类型中排除或提取：

```typescript
type All = "a" | "b" | "c" | "d"

// 从 All 中排除 "a" 和 "b"
type Remaining = Exclude<All, "a" | "b">  // "c" | "d"

// 从 All 中提取 "a" 和 "b"
type Selected = Extract<All, "a" | "b">   // "a" | "b"
```

### 工具类型速查表

| 工具类型 | 作用 | 示例 |
|---------|------|------|
| `Partial<T>` | 所有属性变可选 | 更新操作 |
| `Required<T>` | 所有属性变必选 | 强制完整对象 |
| `Readonly<T>` | 所有属性变只读 | 不可变数据 |
| `Pick<T, K>` | 挑选部分属性 | 列表页字段 |
| `Omit<T, K>` | 排除部分属性 | 创建输入 |
| `Record<K, V>` | 构造键值对 | 映射表 |
| `ReturnType<T>` | 函数返回值类型 | 提取类型 |
| `Parameters<T>` | 函数参数类型 | 提取类型 |
| `Exclude<T, U>` | 联合类型排除 | 过滤类型 |
| `Extract<T, U>` | 联合类型提取 | 选取类型 |
| `NonNullable<T>` | 排除 null/undefined | 去除空值 |

## 五、条件类型

条件类型让类型可以根据条件选择：

```typescript
// 基本语法：T extends U ? X : Y
type IsString<T> = T extends string ? "yes" : "no"

type A = IsString<string>   // "yes"
type B = IsString<number>   // "no"
```

### 分布式条件类型

当 `T` 是联合类型时，条件类型会**逐个分发**：

```typescript
type ToArray<T> = T extends any ? T[] : never

type Result = ToArray<string | number>
// 等价于：
// ToArray<string> | ToArray<number>
// string[] | number[]
```

如果不想分发，用方括号包裹：

```typescript
type ToArray<T> = [T] extends [any] ? T[] : never

type Result = ToArray<string | number>
// (string | number)[]
```

## 六、infer 关键字

`infer` 在条件类型中**声明一个待推断的类型变量**：

### 6.1 推断函数返回值类型

```typescript
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never

type A = MyReturnType<() => string>           // string
type B = MyReturnType<(x: number) => boolean> // boolean
```

### 6.2 推断函数参数类型

```typescript
type FirstParam<T> = T extends (first: infer F, ...rest: any[]) => any ? F : never

type A = FirstParam<(name: string, age: number) => void>  // string
```

### 6.3 推断数组元素类型

```typescript
type ElementOf<T> = T extends (infer E)[] ? E : never

type A = ElementOf<number[]>    // number
type B = ElementOf<string[]>    // string
```

### 6.4 推断 Promise 内部类型

```typescript
type Awaited<T> = T extends Promise<infer U> ? Awaited<U> : T

type A = Awaited<Promise<string>>                // string
type B = Awaited<Promise<Promise<number>>>       // number（递归解包）
```

TS 4.5+ 已内置 `Awaited<T>`，这里展示的是它的实现原理。

## 七、映射类型

映射类型遍历一个对象的所有 key，生成新的类型：

```typescript
// 基本语法
type OptionsFlags<T> = {
  [K in keyof T]: boolean
}

interface Features {
  darkMode: () => void
  notifications: () => void
}

type FeatureFlags = OptionsFlags<Features>
// 等价于：
// { darkMode: boolean; notifications: boolean }
```

`[K in keyof T]` 的含义：遍历 `T` 的所有 key，对每个 key `K` 做变换。

### 7.1 结合修饰符

```typescript
// 所有属性变只读
type MyReadonly<T> = {
  readonly [K in keyof T]: T[K]
}

// 所有属性变可选
type MyPartial<T> = {
  [K in keyof T]?: T[K]
}

// 去掉只读
type Mutable<T> = {
  -readonly [K in keyof T]: T[K]
}

// 去掉可选
type Concrete<T> = {
  [K in keyof T]-?: T[K]
}
```

`+` 添加修饰符（默认），`-` 移除修饰符。

### 7.2 结合条件类型

```typescript
// 只保留函数类型的属性
type FunctionProperties<T> = {
  [K in keyof T as T[K] extends Function ? K : never]: T[K]
}

interface User {
  name: string
  age: number
  greet(): void
  update(): void
}

type UserMethods = FunctionProperties<User>
// { greet(): void; update(): void }
```

`as` 子句可以重映射 key，`never` 表示过滤掉该属性。

## 八、实战：从零构建工具类型

把上面的知识串起来，手写几个内置工具类型：

```typescript
// 手写 Partial
type MyPartial<T> = {
  [K in keyof T]?: T[K]
}

// 手写 Pick
type MyPick<T, K extends keyof T> = {
  [P in K]: T[P]
}

// 手写 Omit
type MyOmit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>

// 手写 Record
type MyRecord<K extends keyof any, V> = {
  [P in K]: V
}

// 手写 ReturnType
type MyReturnType<T extends (...args: any[]) => any> =
  T extends (...args: any[]) => infer R ? R : never
```

理解了这些实现，你就真正掌握了 TS 类型系统的核心机制。

## 九、实战：API 层的完整类型方案

```typescript
// 通用响应结构
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 分页结构
interface Paginated<T> {
  items: T[]
  total: number
  page: number
}

// 用户类型
interface User {
  id: number
  name: string
  email: string
  role: "admin" | "user"
}

// 派生类型
type UserListResponse = ApiResponse<Paginated<User>>
type UserDetailResponse = ApiResponse<User>
type CreateUserInput = Omit<User, "id">
type UpdateUserInput = Partial<CreateUserInput>

// 泛型请求函数
async function get<T>(url: string): Promise<ApiResponse<T>> {
  const res = await fetch(url)
  return res.json()
}

// 使用
const users = await get<Paginated<User>>("/api/users")
const user = await get<User>("/api/users/1")
```

## 总结

1. **泛型接口** `Interface<T>` 让数据结构可复用，支持默认值 `T = unknown`
2. **泛型类** 让容器/服务类适配任意数据类型
3. **泛型约束** `T extends U` 限制类型参数范围，`keyof` 配合约束属性访问
4. **内置工具类型** 是日常开发的瑞士军刀：`Partial/Pick/Omit/Record` 最常用
5. **条件类型** `T extends U ? X : Y` 根据条件选择类型
6. **`infer`** 在条件类型中推断中间类型，是理解框架源码的关键
7. **映射类型** `[K in keyof T]` 遍历对象 key 生成新类型，可结合修饰符和条件类型

下一篇学习 TS 的类增强、模块系统和声明文件——理解 TS 如何与整个 JS 生态协作。
