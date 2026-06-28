---
title: "TypeScript函数类型化：参数、返回值与重载"
date: 2026-06-28 12:00:00
tags:
  - TypeScript
  - JavaScript
  - 前端
categories:
  - 前端开发
---

## 前言

函数是 JS 的核心，也是 TS 类型系统收益最大的地方——参数传错、返回值类型不对，编译器直接标红。本文系统讲解 TS 中函数的类型表达：参数类型、返回值类型、可选参数、默认值、剩余参数、函数重载、`this` 类型，以及泛型函数的入门用法。

<!-- more -->

## 一、基础：参数和返回值类型

```typescript
// 参数必须写类型，返回值可以省略（TS 会推断）
function add(a: number, b: number): number {
  return a + b
}

// 箭头函数
const multiply = (a: number, b: number): number => a * b

// 返回值推断：省略 : number 也行
const divide = (a: number, b: number) => a / b  // 推断为 number
```

**经验法则：** 简单函数省略返回值类型没问题，但导出给外部用的函数建议写上——它相当于文档。

## 二、可选参数与默认值

### 2.1 可选参数

用 `?` 标记可以不传的参数，**必须放在必选参数后面**：

```typescript
function greet(name: string, greeting?: string): string {
  return `${greeting ?? "Hello"}, ${name}!`
}

greet("Alice")            // ✅ "Hello, Alice!"
greet("Alice", "Hi")      // ✅ "Hi, Alice!"
```

### 2.2 默认值

有默认值的参数自动变为可选：

```typescript
function greet(name: string, greeting: string = "Hello"): string {
  return `${greeting}, ${name}!`
}

greet("Alice")            // ✅ "Hello, Alice!"
greet("Alice", "Hey")     // ✅ "Hey, Alice!"
```

可选参数与默认值的区别：

```typescript
// 可选参数：类型是 string | undefined
function a(x?: string) {}   // x: string | undefined

// 默认值：类型是 string
function b(x: string = "hi") {}  // x: string（使用时始终是 string）
```

**推荐用默认值**，类型更明确，调用时也不需要处理 `undefined`。

## 三、剩余参数

用 `...` 收集多余的参数为数组：

```typescript
function sum(...nums: number[]): number {
  return nums.reduce((acc, n) => acc + n, 0)
}

sum(1, 2, 3)       // 6
sum(10, 20, 30, 40) // 100
```

剩余参数必须是最后一个参数：

```typescript
// ✅ 正确
function log(level: string, ...msgs: string[]) {}

// ❌ 报错：剩余参数必须是最后一个
function log(...msgs: string[], level: string) {}
```

## 四、函数类型表达

除了给函数体加类型注解，还可以**单独声明函数的类型**：

```typescript
// 函数类型：接受两个 number，返回 number
type MathFn = (a: number, b: number) => number

const add: MathFn = (a, b) => a + b
const subtract: MathFn = (a, b) => a - b

// 用在回调参数中
function calculate(a: number, b: number, op: MathFn): number {
  return op(a, b)
}

calculate(10, 3, add)       // 13
calculate(10, 3, subtract)  // 7
```

### 回调函数类型

实际开发中最常见的场景是给回调参数标注类型：

```typescript
// 事件处理
function onReady(callback: () => void): void {
  // ...
}

// 异步回调
function fetchData(url: string, onSuccess: (data: unknown) => void): void {
  // ...
}

// 数组方法的回调
const nums = [1, 2, 3]
nums.map((n): string => n.toString())  // 返回值类型是 string[]
```

**注意回调返回值是 `void` 的含义：** 它不是说回调不能有返回值，而是说**调用方不关心返回值**：

```typescript
type Callback = () => void

const cb: Callback = () => 42  // ✅ 合法！void 回调可以有返回值
```

这是 TS 的设计决策——让 `Array.prototype.forEach` 等接受 `void` 回调的函数更灵活。

## 五、函数重载

JS 不支持重载（同名函数不同参数），TS 的重载是**编译时**的类型提示，运行时只有一个实现：

```typescript
// 重载签名（类型声明，没有函数体）
function format(value: string): string
function format(value: number): string
function format(value: Date): string

// 实现签名（有函数体，参数类型用联合）
function format(value: string | number | Date): string {
  if (typeof value === "string") {
    return value.toUpperCase()
  } else if (typeof value === "number") {
    return value.toFixed(2)
  } else {
    return value.toISOString()
  }
}

format("hello")       // ✅ 返回 string
format(3.14)          // ✅ "3.14"
format(new Date())    // ✅ ISO 字符串
format(true)          // ❌ 没有匹配的重载签名
```

重载签名的顺序**有影响**——TS 从上往下匹配，找到第一个匹配的就用。所以更精确的签名应该写在前面。

### 实际场景：根据参数返回不同类型

```typescript
function parseInput(input: string, asNumber: true): number
function parseInput(input: string, asNumber: false): string
function parseInput(input: string, asNumber: boolean): string | number {
  return asNumber ? Number(input) : input
}

const n = parseInput("42", true)    // 类型是 number
const s = parseInput("42", false)   // 类型是 string
```

## 六、this 类型

JS 中 `this` 的指向是运行时确定的，TS 可以在编译时声明 `this` 的类型：

```typescript
interface Counter {
  count: number
  increment(this: Counter): void
}

const counter: Counter = {
  count: 0,
  increment(this: Counter) {
    this.count++  // ✅ this 类型明确
  },
}

counter.increment()
```

**`this` 参数必须是第一个参数，且不会出现在运行时参数中。**

常见用法：防止回调中 `this` 丢失

```typescript
class Timer {
  seconds = 0

  start(this: Timer) {
    setInterval(() => {
      this.seconds++  // ✅ 箭头函数不绑定 this，这里指向 Timer 实例
    }, 1000)
  }
}
```

如果你不用 `this` 参数，TS 在 `strict` 模式下会对函数中的 `this` 报 `noImplicitThis` 错误。

## 七、泛型函数入门

泛型让函数接受**类型参数**，实现"一个函数适配多种类型"：

```typescript
// 没有泛型：需要为每种类型写一个函数
function firstNumber(arr: number[]): number | undefined {
  return arr[0]
}
function firstString(arr: string[]): string | undefined {
  return arr[0]
}

// 有泛型：一个函数搞定
function first<T>(arr: T[]): T | undefined {
  return arr[0]
}

first([1, 2, 3])        // 返回类型是 number | undefined
first(["a", "b", "c"])  // 返回类型是 string | undefined
```

`<T>` 是类型参数，TS 会根据传入的实参**自动推断** `T` 的具体类型。

### 7.1 多个类型参数

```typescript
function pair<A, B>(a: A, b: B): [A, B] {
  return [a, b]
}

const p = pair("hello", 42)  // 类型是 [string, number]
```

### 7.2 泛型约束

用 `extends` 限制类型参数的范围：

```typescript
// T 必须有 length 属性
function getLength<T extends { length: number }>(item: T): number {
  return item.length
}

getLength("hello")     // ✅ string 有 length
getLength([1, 2, 3])   // ✅ 数组有 length
getLength(42)          // ❌ number 没有 length 属性
```

### 7.3 泛型与回调结合

```typescript
function map<T, U>(arr: T[], fn: (item: T) => U): U[] {
  return arr.map(fn)
}

map([1, 2, 3], n => n.toString())  // 返回 string[]
map(["a", "b"], s => s.length)     // 返回 number[]
```

泛型是 TS 最强大的特性之一，下一篇会深入讲泛型接口、泛型类和内置工具类型。

## 八、函数的类型断言

有时候 TS 无法推断回调的类型，可以用断言帮助：

```typescript
const callbacks = [
  (() => 1) as () => number,
  (() => "hello") as () => string,
]

// 或者用泛型数组
const callbacks: Array<() => number | string> = [
  () => 1,
  () => "hello",
]
```

## 九、实战：事件系统的类型定义

综合运用函数类型、泛型和联合类型：

```typescript
type EventMap = {
  click: { x: number; y: number }
  keydown: { key: string; code: string }
  scroll: { scrollTop: number }
}

// 泛型事件监听器
function on<K extends keyof EventMap>(
  event: K,
  handler: (payload: EventMap[K]) => void
): void {
  // 注册事件...
}

// 使用：payload 类型自动推断
on("click", (payload) => {
  console.log(payload.x, payload.y)  // ✅ 自动推断为 { x: number; y: number }
})

on("keydown", (payload) => {
  console.log(payload.key)  // ✅ 自动推断为 { key: string; code: string }
})
```

这种模式在 Vue 3、React 的事件系统中非常常见。

## 总结

1. **参数类型必须写**，返回值类型简单函数可省略
2. **可选参数 `?`** 必须在必选参数之后，**默认值**更推荐
3. **剩余参数 `...args`** 收集为数组，必须是最后一个参数
4. **函数类型表达**用 `type Fn = (a: number) => string`，回调参数类型很重要
5. **函数重载**让同名函数接受不同参数返回不同类型
6. **`this` 参数**在 strict 模式下防止 this 指向错误
7. **泛型函数**用 `<T>` 适配多种类型，`extends` 约束范围

下一篇进入泛型的完整世界——泛型接口、泛型类、内置工具类型。
