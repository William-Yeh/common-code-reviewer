# TypeScript / JavaScript Review Rules

These rules supplement the common review framework. Apply them to `.ts`, `.tsx`, `.js`, and `.jsx` files.

## Prefer Modern Features

Flag legacy patterns when modern alternatives exist:

| Legacy Pattern | Prefer | Why |
|---|---|---|
| `enum` (numeric/string) | Union types or `as const` objects | Enums leak runtime code, have quirky behavior with reverse mapping |
| `any` | `unknown` + type narrowing | `any` disables the type system entirely |
| Type assertion `as Foo` | Type guards / `satisfies` | Assertions bypass checking; `satisfies` validates while inferring |
| `interface` for utility shapes | `type` alias | `type` supports unions, intersections, mapped types; use `interface` for contracts that may be extended |
| `Promise` chains with `.then` | `async/await` | Readability; easier error handling |
| `var` | `const` / `let` | Block scoping, no hoisting surprises |
| `arguments` object | Rest parameters `...args` | Type-safe, actual array |
| `require()` | `import` / `import()` | Tree-shakeable, statically analyzable |
| Index signatures `[key: string]` | `Record<K, V>` or `Map` | More expressive, better tooling support |
| Class with only static methods | Module-level functions | No reason for a class wrapper |

## Type System

### Flags

- **`any` leakage**: Any `any` in new code is MAJOR unless explicitly justified with a comment. Check for implicit `any` from untyped dependencies.
- **Missing return types on public APIs**: Exported functions should have explicit return types. Internal functions can rely on inference.
- **Type assertions in chains**: `foo as Bar as Baz` is almost always hiding a type error — BLOCKER.
- **Non-null assertions (`!`)**: Flag unless the author explains why null is impossible. Prefer optional chaining or early returns.
- **Overly broad types**: `string` where a union of literals would enforce correctness. `object` where a specific shape exists.

### Patterns to Encourage

- Discriminated unions for state machines and variant types
- `satisfies` for validating object shapes while preserving literal types
- `const` assertions (`as const`) for readonly tuples and literal types
- Template literal types for string patterns
- Branded types for domain primitives (e.g., `UserId`, `Email`)
- `readonly` on array/object parameters that shouldn't be mutated
- `using` / `await using` for resource management (Explicit Resource Management)

## Functional Patterns

- Prefer `map`/`filter`/`reduce`/`flatMap` over `for` loops when the intent is transformation
- Flag `forEach` with side effects — if you're not returning a value, use `for...of` for clarity
- Encourage pure functions: same input, same output, no mutations
- Flag mutation of function parameters — use spread or `structuredClone`
- Prefer `Object.freeze` / `as const` / `readonly` for data that shouldn't change
- Encourage pipe/compose patterns when chaining 3+ transformations

## Error Handling

- **Never** catch and ignore: `catch (e) {}` is BLOCKER
- Prefer typed error results over thrown exceptions for expected failures. Use discriminated unions:
  ```typescript
  type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
  ```
- `catch (e: unknown)` — never assume error type. Use `instanceof` or type guard.
- Avoid `catch` at every level — let errors propagate to a boundary handler
- Flag `console.log` / `console.error` in production code — use a structured logger

## Style Standard

Follow **ESLint recommended** + **Airbnb style guide** conventions (the de-facto community standard):

- Trailing commas in multiline structures (less noisy diffs)
- Semicolons required
- Single quotes for strings (double quotes in JSX)
- Explicit function return types on exports
- No default exports (named exports for refactoring safety)
- Imports ordered: external → internal → relative, each group alphabetized
- Prefer `type` imports (`import type { Foo }`) to avoid runtime import of types

Do not flag style issues that ESLint/Prettier would catch. Only flag style when it affects semantics or readability beyond formatter scope.

## React (`.tsx` / `.jsx`)

- Flag `useEffect` with missing or incorrect dependency arrays
- Flag `useEffect` used for derived state — prefer `useMemo` or compute inline
- Flag `useState` for values derivable from props or other state
- Flag inline object/array/function literals in JSX props (causes unnecessary re-renders)
- Flag components over ~100 lines — likely needs decomposition
- Encourage custom hooks to extract reusable stateful logic
- `key` prop: flag array index as key when list items can reorder
- Prefer Server Components by default in Next.js App Router — only add `"use client"` when necessary
- Flag prop drilling through 3+ levels — use context or composition

## NestJS

- **Module boundaries**: Each module should encapsulate a bounded context. Flag cross-module direct imports that bypass the module system.
- **Dependency injection**: Flag `new Service()` inside controllers/services. Use constructor injection.
- **DTOs and validation**: All API inputs must have DTO classes with `class-validator` decorators. Flag raw `@Body()` without a DTO type.
- **Guards over middleware**: Prefer guards (`@UseGuards`) for auth/authorization over Express middleware.
- **Exception filters**: Use domain-specific exception classes, not raw `HttpException` with hardcoded status codes.
- **Circular dependencies**: Flag `forwardRef()` — usually indicates a design problem. Suggest extracting a shared module.
- **Repository pattern**: Data access logic belongs in repositories/services, not controllers.

## Next.js (App Router)

- **Server vs Client**: Flag `"use client"` on components that don't use hooks, event handlers, or browser APIs — they should be Server Components.
- **Data fetching**: Prefer `fetch` in Server Components over client-side `useEffect` + `useState`. Use React Server Components for data loading.
- **Route handlers**: Flag business logic in `route.ts` — it belongs in a service layer.
- **Server Actions**: Validate all inputs in server actions — they're publicly accessible endpoints. Use Zod or similar.
- **Metadata**: Flag pages missing `metadata` or `generateMetadata` exports.
- **Loading/Error states**: Flag route segments missing `loading.tsx` and `error.tsx` boundaries.
- **Caching**: Be explicit about caching — flag `fetch` calls without `cache` or `revalidate` options in production code.

## Testing

- Prefer `describe`/`it` structure with intention-revealing test names
- Flag tests that test implementation details (e.g., asserting internal state, method call counts) over behavior
- Flag missing edge case tests: null, empty array, boundary values
- Mock at module boundaries, not deep internals
- Flag `any` in test code — tests should be type-safe too
- Prefer `toEqual` over `toBe` for objects; prefer `toStrictEqual` when undefined properties matter

## Common Enterprise Anti-Patterns

- **Barrel files that re-export everything**: Kills tree-shaking, creates circular dependency risks
- **God services**: A `UserService` with 20+ methods — split by use case
- **Shared mutable singletons**: Module-level `let` state accessed by multiple consumers
- **String-typed APIs**: Using `string` for IDs, statuses, types — use branded types or unions
- **Callback hell in legacy code being modified**: If touching it, refactor to async/await
- **Default exports**: Prefer named exports for refactoring safety and IDE support
