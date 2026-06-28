---
title: "TypeScript工程化：配置、框架集成与报错排查"
date: 2026-06-28 15:00:00
tags:
  - TypeScript
  - JavaScript
  - Vue3
  - React
  - 前端
categories:
  - 前端开发
---

## 前言

前五篇学完了 TS 的类型系统，最后一篇解决"学了但配不好"的问题——`tsconfig.json` 怎么配、路径别名怎么设、Vue 3 和 React 怎么集成、编译报错怎么排查。这是把 TS 落地到真实项目的关键一步。

<!-- more -->

## 一、tsconfig.json 核心字段详解

### 1.1 基础配置

```json
{
  "compilerOptions": {
    // 编译目标：输出哪个版本的 JS
    "target": "ES2020",

    // 模块系统
    "module": "ESNext",

    // 模块解析策略
    "moduleResolution": "bundler",

    // 严格模式
    "strict": true,

    // 输出目录
    "outDir": "./dist",

    // 允许导入 JSON 文件
    "resolveJsonModule": true,

    // 允许导入 JS 文件
    "allowJs": true,

    // 生成 source map（调试用）
    "sourceMap": true,

    // 跳过库的类型检查（加速编译）
    "skipLibCheck": true
  },

  // 包含哪些文件
  "include": ["src/**/*", "types/**/*"],

  // 排除哪些目录
  "exclude": ["node_modules", "dist"]
}
```

### 1.2 target 选择建议

| target | 输出 | 适用场景 |
|--------|------|---------|
| `ES2015` | ES6 | 需要兼容旧浏览器 |
| `ES2020` | 支持 optional chaining、nullish coalescing | 现代浏览器 / Node 14+ |
| `ESNext` | 最新语法 | 有打包器处理兼容性 |

**推荐：** 前端项目用 `ESNext`（打包器会降级），Node.js 项目用与运行时匹配的版本。

### 1.3 module 和 moduleResolution 的搭配

| 场景 | module | moduleResolution |
|------|--------|-----------------|
| Vite / Webpack 打包器 | `ESNext` | `bundler` |
| Node.js ESM | `nodenext` | `nodenext` |
| Node.js CommonJS | `commonjs` | `node` |

### 1.4 strict 模式的子开关

如果不想一次性全开 `strict`，可以单独控制：

```json
{
  "compilerOptions": {
    "strict": false,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

**迁移策略：** 先开 `noImplicitAny` + `strictNullChecks`，这两个收益最大。等项目稳定后再开 `strict: true`。

## 二、路径别名

项目大了之后，`../../../../components/Button` 这种相对路径很痛苦。路径别名解决这个问题：

### 2.1 tsconfig.json 配置

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}
```

### 2.2 Vite 配置同步

tsconfig 的 `paths` 只管类型检查，运行时需要打包器配合：

```typescript
// vite.config.ts
import { defineConfig } from "vite"
import path from "path"

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@components": path.resolve(__dirname, "src/components"),
      "@utils": path.resolve(__dirname, "src/utils"),
    },
  },
})
```

### 2.3 Webpack 配置

```javascript
// webpack.config.js
const path = require("path")

module.exports = {
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
}
```

### 2.4 使用

```typescript
// 之前
import Button from "../../../../components/Button"

// 之后
import Button from "@/components/Button"
```

## 三、Vue 3 + TypeScript 集成

### 3.1 项目初始化

```bash
npm create vite@latest my-vue-app -- --template vue-ts
```

生成的项目已经配好了 TS 支持。核心是 `tsconfig.json` 里的 `vue` 相关配置：

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}
```

### 3.2 组件中的 TS

```vue
<script setup lang="ts">
import { ref, computed } from "vue"

// ref 泛型
const count = ref<number>(0)
const name = ref<string>("Alice")

// computed 泛型
const doubleCount = computed<number>(() => count.value * 2)

// 函数类型
function increment(): void {
  count.value++
}
</script>
```

### 3.3 Props 类型定义

```vue
<script setup lang="ts">
interface Props {
  title: string
  count?: number
  items: string[]
}

const props = withDefaults(defineProps<Props>(), {
  count: 0,
})

// emit 类型
const emit = defineEmits<{
  (e: "update", value: number): void
  (e: "close"): void
}>()

emit("update", 42)  // ✅
emit("update", "x") // ❌ 类型不匹配
</script>
```

### 3.4 组合函数（Composables）

```typescript
// composables/useUser.ts
import { ref, Ref } from "vue"

interface User {
  id: number
  name: string
  email: string
}

interface UseUserReturn {
  user: Ref<User | null>
  loading: Ref<boolean>
  fetchUser: (id: number) => Promise<void>
}

export function useUser(): UseUserReturn {
  const user = ref<User | null>(null)
  const loading = ref(false)

  async function fetchUser(id: number): Promise<void> {
    loading.value = true
    try {
      const res = await fetch(`/api/users/${id}`)
      user.value = await res.json()
    } finally {
      loading.value = false
    }
  }

  return { user, loading, fetchUser }
}
```

## 四、React + TypeScript 集成

### 4.1 项目初始化

```bash
npm create vite@latest my-react-app -- --template react-ts
```

### 4.2 组件类型

```tsx
// 函数组件：Props 用 interface 定义
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: "primary" | "secondary" | "danger"
  disabled?: boolean
}

function Button({ label, onClick, variant = "primary", disabled = false }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  )
}
```

### 4.3 useState 类型

```tsx
import { useState } from "react"

interface User {
  id: number
  name: string
}

function UserList() {
  // 自动推断
  const [count, setCount] = useState(0)            // number

  // 需要泛型的场景：初始值是 null
  const [user, setUser] = useState<User | null>(null)

  // 数组
  const [users, setUsers] = useState<User[]>([])

  return <div>{user?.name}</div>
}
```

### 4.4 事件处理

```tsx
function Form() {
  function handleSubmit(e: React.FormEvent<HTMLFormElement>): void {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    console.log(formData.get("name"))
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>): void {
    console.log(e.target.value)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" onChange={handleChange} />
      <button type="submit">Submit</button>
    </form>
  )
}
```

### 4.5 通用组件

```tsx
// 泛型组件：通用列表
interface ListProps<T> {
  items: T[]
  renderItem: (item: T) => React.ReactNode
  keyExtractor: (item: T) => string
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item) => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  )
}

// 使用
<List
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
  keyExtractor={(user) => String(user.id)}
/>
```

## 五、常见编译报错排查清单

### 5.1 TS2322: 类型不赋值

```
Type 'string' is not assignable to type 'number'
```

**原因：** 变量或参数类型不匹配。
**解决：** 检查赋值两侧的类型，用类型断言或修正类型定义。

### 5.2 TS2339: 属性不存在

```
Property 'name' does not exist on type '{ id: number }'
```

**原因：** 访问了对象上不存在的属性。
**解决：** 检查 interface 定义是否完整，或用可选链 `?.` 处理可能为 undefined 的情况。

### 5.3 TS2531: 对象可能为 null

```
Object is possibly 'null'
```

**原因：** `strictNullChecks` 开启后，`null` 不能直接当有值的对象用。
**解决：**

```typescript
const el = document.getElementById("root")

// 方式一：类型守卫
if (el) {
  el.innerHTML = "hello"
}

// 方式二：非空断言（你确信它存在）
el!.innerHTML = "hello"

// 方式三：空值合并
const value = el?.innerHTML ?? "default"
```

### 5.4 TS7006: 参数隐式为 any

```
Parameter 'x' implicitly has an 'any' type
```

**原因：** `noImplicitAny` 开启，函数参数没有类型注解。
**解决：** 给参数加类型，或者用 `any`（不推荐）。

### 5.5 TS2345: 参数类型不匹配

```
Argument of type 'string' is not assignable to parameter of type 'number'
```

**原因：** 传给函数的实参类型与形参不匹配。
**解决：** 检查函数签名，确认传入正确的类型。

### 5.6 TS18048: 值可能为 undefined

```
'value' is possibly 'undefined'
```

**原因：** 数组取值或对象属性可能是 undefined。
**解决：**

```typescript
const arr: number[] = []
const first = arr[0]  // 类型是 number | undefined

// 使用前检查
if (first !== undefined) {
  console.log(first.toFixed(2))
}
```

### 5.7 模块找不到

```
Cannot find module '@utils/helper' or its corresponding type declarations
```

**原因：** 路径别名没有在 tsconfig 中配置，或配置不正确。
**解决：** 检查 `paths` 配置和打包器的 `alias` 是否一致。

## 六、实用的 tsconfig 预设

### 6.1 Vue 3 + Vite 项目

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "env.d.ts"]
}
```

### 6.2 Node.js 项目

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "strict": true,
    "esModuleInterop": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "resolveJsonModule": true,
    "declaration": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

## 七、tsc 常用命令

```bash
# 编译整个项目
tsc

# 只检查不输出文件（CI 中常用）
tsc --noEmit

# 编译单个文件
tsc src/index.ts

# 查看生效的配置
tsc --showConfig

# 生成 tsconfig 模板
tsc --init
```

## 总结

1. **tsconfig.json** 是 TS 项目的核心配置，`strict` + `target` + `moduleResolution` 是三个最重要的字段
2. **路径别名**需要 tsconfig `paths` 和打包器 `alias` 双重配置
3. **Vue 3** 用 `<script setup lang="ts">`，`defineProps<T>` 和 `defineEmits<T>` 是核心
4. **React** 用 `.tsx` 后缀，`useState<T>` 和事件类型 `React.ChangeEvent<HTMLInputElement>` 是重点
5. **报错排查**先看错误码，`TS2322/TS2339/TS2531` 是最常见的三类

至此 TypeScript 系列六篇全部完成。从类型基石到工程化落地，覆盖了日常开发需要的全部核心知识。
