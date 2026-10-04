# TypeScript / JavaScript Review Rules

These rules supplement the common review framework. Apply them to `.ts`, `.tsx`, `.js`, and `.jsx` files.

## Prefer Modern Features

Flag legacy patterns when modern alternatives exist. Findings from this table are `common/language-idiom` unless a row's pattern also matches a more specific rule in this reference or the catalog; that rule's ID and severity take precedence. Gate runtime APIs on the project's `target`/`lib` and its supported runtimes.

| Legacy Pattern | Prefer | Why |
|---|---|---|
| `enum`, runtime `namespace`, constructor parameter properties, `import x = require()` | Union types or `as const` objects; plain fields assigned in the constructor; ES `import` | They emit runtime code, so Node's built-in type stripping rejects them (`ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`); `erasableSyntaxOnly` enforces this. NestJS code relies on parameter properties and decorators; do not flag them there |
| `any` | `unknown` + type narrowing | `any` disables the type system entirely |
| Type assertion `as Foo` | Type guards / `satisfies` | Assertions bypass checking; `satisfies` validates while inferring |
| `interface` for utility shapes | `type` alias | `type` supports unions, intersections, mapped types; use `interface` for contracts that may be extended |
| `Promise` chains with `.then` | `async/await` | Readability; easier error handling |
| `var` | `const` / `let` | Block scoping, no hoisting surprises |
| `arguments` object | Rest parameters `...args` | Type-safe, actual array |
| `require()` | `import` / `import()` | Tree-shakeable, statically analyzable |
| Index signatures `[key: string]` | `Record<K, V>` or `Map` | More expressive, better tooling support |
| Class with only static methods | Module-level functions | No reason for a class wrapper |
| Hand-rolled set algebra, iterator-to-array-then-`map`, `new Promise` wrapping sync-or-async calls | `Set.prototype.union`/`intersection`/`difference`, Iterator helpers (`.map`/`.filter`/`.take` on iterators), `Promise.try` | Finished (Stage 4) and in evergreen runtimes |
| `instanceof Error` on values that may cross realms (iframes, `vm`, workers) | `Error.isError(value)` | `instanceof` fails across realms |
| `Buffer`/`btoa` round-trips for base64 on `Uint8Array` | `Uint8Array.fromBase64` / `.toBase64()` | Standard, works outside Node |
| Floating-point `reduce((a, b) => a + b)` for money-like or precision-sensitive sums | `Math.sumPrecise` | Avoids accumulated rounding error |
| `map.has(k) ? map.get(k) : (map.set(k, v), v)` | `map.getOrInsert(k, v)` / `getOrInsertComputed(k, fn)` | Finished (Stage 4); one lookup |
| `Date` or moment.js arithmetic in new code, where the runtime ships `Temporal` | `Temporal` | Immutable, time-zone and calendar aware |

## Type System

### Flags

- **`any` leakage**: Flag `any` in new code unless it is explicitly justified with a comment — `common/weak-type-model`. Check for implicit `any` from untyped dependencies.
- **Missing return types on public APIs**: Exported functions should have explicit return types. Internal functions can rely on inference. — `common/language-idiom`
- **Double assertions**: `x as unknown as T` (or `as any as T`) overrides the compiler's "neither type sufficiently overlaps" error (TS2352), so it usually hides a type error — `common/weak-type-model`. Prefer a type guard or a typed boundary. Accept it in test doubles and in a branded-type constructor.
- **Non-null assertions (`!`)**: Flag unless the author explains why null is impossible. Prefer optional chaining or early returns. — `common/weak-type-model`
- **Overly broad types**: `string` where a union of literals would enforce correctness. `object` where a specific shape exists. — `common/weak-type-model`

### Patterns to Encourage

- Discriminated unions for state machines and variant types — `common/weak-type-model`
- `satisfies` for validating object shapes while preserving literal types — `common/language-idiom`
- `const` assertions (`as const`) for readonly tuples and literal types — `common/language-idiom`
- Template literal types for string patterns — `common/language-idiom`
- Branded types for domain primitives (e.g., `UserId`, `Email`) — `common/weak-type-model`
- `readonly` on array/object parameters that shouldn't be mutated — `common/unnecessary-mutation`
- `using` / `await using` for resource management (Explicit Resource Management) — `common/language-idiom`
- Hand-written regex escaping (`str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')`) — prefer `RegExp.escape`. An incomplete hand-written escaper on untrusted input is a regex-injection and ReDoS risk — `common/missing-input-validation`.
- For published libraries: explicit return/export types to enable `isolatedDeclarations` (5.5+) — faster, parallelizable `.d.ts` emit. Flag exported APIs relying on inferred types in packages that ship declarations. — `common/language-idiom`

## Functional Patterns

- Prefer `map`/`filter`/`reduce`/`flatMap` over `for` loops when the intent is transformation — `common/imperative-transformation`
- Flag `forEach` with side effects — if you're not returning a value, use `for...of` for clarity — `common/style-readability`
- Encourage pure functions: same input, same output, no mutations — `common/hidden-side-effect`
- Flag mutation of function parameters — use spread or `structuredClone` — `common/unnecessary-mutation`
- Prefer `Object.freeze` / `as const` / `readonly` for data that shouldn't change — `common/unnecessary-mutation`
- Encourage pipe/compose patterns when chaining 3+ transformations — `common/imperative-transformation`

## Error Handling

- **Never** catch and ignore: flag `catch (e) {}` — `common/ignored-error`
- Prefer typed error results over thrown exceptions for expected failures. Use discriminated unions — `common/erased-failure`:
  ```typescript
  type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
  ```
- `catch (e: unknown)` — never assume error type. Use `instanceof` or type guard. — `common/weak-type-model`
- Avoid `catch` at every level — let errors propagate to a boundary handler — `common/incomplete-error-handling`
- Flag `console.log` / `console.error` in production code — use a structured logger — `common/language-idiom`

## Compiler and Toolchain Configuration

Review `tsconfig.json`, `package.json`, and ESLint config when they change:

- **TypeScript 6.0 removals** — flag `common/deprecated-api`: `outFile`; `module` set to `amd`, `umd`, `systemjs`, or `none`; `moduleResolution: "classic"`; `esModuleInterop` or `allowSyntheticDefaultImports` set to `false`.
- **TypeScript 6.0 deprecations** (errors unless `"ignoreDeprecations": "6.0"`, and removed in 7.0) — flag `common/deprecated-api`: `target: "es5"`, `downlevelIteration`, `moduleResolution: "node"` / `"node10"` (use `nodenext` or `bundler`), `baseUrl` (put the prefix in `paths`), the `module Foo {}` namespace keyword (use `namespace`), and import assertions `assert { type: "json" }` (use `with`). Flag a new `ignoreDeprecations` setting that has no migration plan.
- **TypeScript 6.0 defaults**: `strict` and `noUncheckedSideEffectImports` default to `true`, and `types` no longer auto-includes every `@types` package. Flag `strict: false` added without a written reason — `common/weak-type-model`.
- **TypeScript 7.0** (native compiler) ships no compiler API until 7.1. Flag an upgrade that drops TypeScript 6 while typescript-eslint or other API-based tooling still needs it; keep it side-by-side through `@typescript/typescript6` — `common/deprecated-api`.
- **Code run directly by Node** (type stripping, Node 22.18+): enable `erasableSyntaxOnly` and `verbatimModuleSyntax`, and import with `.ts` extensions. Non-erasable syntax in such code fails at startup — `common/deprecated-api`.
- **ESLint**: ESLint 10 removed `.eslintrc*` support. Flag `.eslintrc*` files or `ESLINT_USE_FLAT_CONFIG=false` — `common/deprecated-api`; use `eslint.config.js` (flat config).

## Style Standard

Follow **ESLint recommended** + **typescript-eslint** (flat config) conventions. Respect a project's own shared config; do not recommend `eslint-config-airbnb`, which does not support flat config:

- Trailing commas in multiline structures (less noisy diffs)
- Semicolons required
- Single quotes for strings (double quotes in JSX)
- Explicit function return types on exports — `common/language-idiom`
- No default exports (named exports keep one name per symbol across importers) — `common/style-naming`
- Imports ordered: external → internal → relative, each group alphabetized
- Prefer `type` imports (`import type { Foo }`) to avoid runtime import of types — `common/language-idiom`

Do not flag style issues that ESLint/Prettier would catch. Only flag style when it affects semantics or readability beyond formatter scope.

## React (`.tsx` / `.jsx`)

Check whether React Compiler is enabled (`babel-plugin-react-compiler`, or `reactCompiler: true` in `next.config`). It memoizes automatically, which changes the memoization advice below.

- Flag `useEffect` with missing or incorrect dependency arrays — `common/api-misuse`
- Flag `// eslint-disable-next-line react-hooks/exhaustive-deps` used to leave a dependency out — `common/hidden-side-effect`. Since React 19.2, move the non-reactive logic into `useEffectEvent`.
- Flag `useEffect` used for derived state — compute it during render; reach for `useMemo` only when the compiler is off and the computation is measurably expensive — `common/unnecessary-mutation`
- Flag `useState` for values derivable from props or other state — `common/unnecessary-mutation`
- Without React Compiler: flag inline object/array/function literals passed to memoized children (they defeat `memo`) — `common/hot-path-allocation`. With React Compiler: do not flag them, and do not ask for new `useMemo`/`useCallback`; keep them only as an escape hatch, such as stabilizing an effect dependency. Do not ask for existing memoization to be removed either.
- Flag components over ~100 lines — likely needs decomposition — `common/god-module`
- Encourage custom hooks to extract reusable stateful logic — `common/duplicated-logic`
- `key` prop: flag array index as key when list items can reorder or be inserted — `common/api-misuse`
- Prefer Server Components by default in Next.js App Router — only add `"use client"` when necessary — `common/language-idiom`
- Flag prop drilling through 3+ levels — use context or composition — `common/missing-abstraction`

## NestJS

- **Module boundaries**: Each module should encapsulate a bounded context. Flag cross-module direct imports that bypass the module system. — `common/layer-violation`
- **Dependency injection**: Flag `new Service()` inside controllers/services. Use constructor injection. — `common/hard-coded-dependency`
- **DTOs and validation**: All API inputs must have DTO classes with `class-validator` decorators. Flag raw `@Body()` without a DTO type. — `common/missing-input-validation`
- **Guards over middleware**: Prefer guards (`@UseGuards`) for auth/authorization over Express middleware. — `common/language-idiom`
- **Exception filters**: Use domain-specific exception classes, not raw `HttpException` with hardcoded status codes. — `common/erased-failure`
- **Circular dependencies**: Flag `forwardRef()` — usually indicates a design problem. Suggest extracting a shared module. — `common/circular-dependency`
- **Repository pattern**: Data access logic belongs in repositories/services, not controllers. — `common/layer-violation`

## Next.js (App Router)

- **Server vs Client**: Flag `"use client"` on components that don't use hooks, event handlers, or browser APIs — they should be Server Components. — `common/language-idiom`
- **Data fetching**: Prefer `fetch` in Server Components over client-side `useEffect` + `useState`. Use React Server Components for data loading. — `common/language-idiom`
- **Route handlers**: Flag business logic in `route.ts` — it belongs in a service layer. — `common/layer-violation`
- **Server Actions**: Validate all inputs in server actions — they're publicly accessible endpoints. Use Zod or similar. — `common/missing-input-validation`
- **Metadata**: Flag pages missing `metadata` or `generateMetadata` exports. — `common/language-idiom`
- **Loading/Error states**: Flag route segments missing `loading.tsx` and `error.tsx` boundaries. — `common/incomplete-error-handling`
- **Caching (Next.js 16+)**: Caching is opt-in. With `cacheComponents: true`, cache with the `'use cache'` directive plus `cacheLife` / `cacheTag`; do not flag `fetch` calls for lacking `cache` or `revalidate` options. Flag single-argument `revalidateTag(tag)` — `common/deprecated-api`; pass a `cacheLife` profile (`revalidateTag(tag, 'max')`), or call `updateTag(tag)` inside a Server Action that needs read-your-writes.
- **Caching (Next.js 14–15)**: Be explicit about caching — flag `fetch` calls without `cache` or `revalidate` options in production code. — `common/language-idiom`
- **Request APIs (Next.js 16+)**: `cookies()`, `headers()`, `draftMode()`, and the `params` / `searchParams` props are async only. Flag synchronous access — `common/deprecated-api`.
- **Proxy (Next.js 16+)**: `middleware.ts` is deprecated in favor of `proxy.ts`, which runs on the Node.js runtime. Flag new `middleware.ts` files — `common/deprecated-api`.

## Testing

- Prefer `describe`/`it` structure with intention-revealing test names — `common/unclear-name`
- Flag tests that test implementation details (e.g., asserting internal state, method call counts) over behavior — `common/brittle-test`
- Mock at module boundaries, not deep internals — `common/brittle-test`
- Flag `any` in test code — tests should be type-safe too — `common/weak-type-model`
- Prefer `toEqual` over `toBe` for objects; prefer `toStrictEqual` when undefined properties matter — `common/brittle-test`

## Common Enterprise Anti-Patterns

- **Barrel files that re-export everything**: Kills tree-shaking, creates circular dependency risks — `common/language-idiom`
- **God services**: A `UserService` with 20+ methods — split by use case — `common/god-module`
- **Shared mutable singletons**: Module-level `let` state accessed by multiple consumers — `common/shared-mutable-state`
- **String-typed APIs**: Using `string` for IDs, statuses, types — use branded types or unions — `common/weak-type-model`
- **Callback hell in legacy code being modified**: If touching it, refactor to async/await — `common/deep-nesting`
- **Default exports**: Prefer named exports for refactoring safety and IDE support — `common/style-naming`

## Change Risk

### Scored Units

Function declarations, methods, constructors, getters and setters, and function
or arrow expressions bound to a named `const`, `let`, class field, or object
property. Inline callbacks and IIFEs fold into the enclosing unit. Not scored,
having no body: overload signatures, `declare`, `abstract`, interface and type
members.

### Decision Points

| Category | TypeScript / JavaScript |
|---|---|
| Branch | `if`, `else if` |
| Loop | `for`, `for...of`, `for...in`, `while`, `do` |
| Case arm | each `case`; `default` free |
| Exception handler | `catch` |
| Short-circuit operator | `&&`, `\|\|`, `??`, `&&=`, `\|\|=`, `??=` |
| Conditional expression | `?:` |
| Early-return operator | none |

Not counted: `else`, `finally`, `?.`, optional and default parameters, default
destructuring values.

### Test Files

`*.test.*`, `*.spec.*`, `*.stories.*`, and anything under `__tests__/`,
`__mocks__/`, `cypress/`, or `e2e/`.

### Coverage Evidence

Vitest (`--coverage.reporter=lcov`), Jest (`--coverageReporters=lcov`), c8, and
nyc all write `coverage/lcov.info`; the lines inside the unit's range give cov.

### Oracle Deviations

`lizard` reports `??` as +2 (it tokenises it as two `?`) and scores inline arrow
functions as separate anonymous units. ESLint `complexity` additionally counts
`?.`, default parameters, and default destructuring values, so its CC runs
higher.
