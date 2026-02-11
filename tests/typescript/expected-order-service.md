# Expected Findings: TypeScript — order-service.ts

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Input validation | 30-32 | SQL injection via string interpolation in `createOrder`. User input directly embedded in SQL query. |
| 2 | BLOCKER | Security | Input validation | 49-51 | SQL injection via string interpolation in `searchOrders`. Same pattern repeated. |
| 3 | BLOCKER | Implementation | Error handling | 37 | Empty catch block `catch (e) {}` silently swallows warehouse notification failure. |
| 4 | MAJOR | Architecture | SRP | 13 | God controller — mixes HTTP handling, business logic, data access, and caching in a single class. Should separate into Controller → Service → Repository layers. |
| 5 | MAJOR | Design | DIP | 16-17 | Field injection via `@Inject()` — should use constructor injection for testability and explicit dependencies. |
| 6 | MAJOR | Implementation | Clean Code | 10, 42, 56, 67 | `any` type used in multiple places: `orderCache`, `body` parameters, `results` array, `notifyWarehouse` parameter. Disables type safety. |
| 7 | MAJOR | Design | ISP / DTO | 25 | No DTO or validation on `@Body() body` — raw request body with no type checking or constraint validation. |
| 8 | MAJOR | Performance | Bounded queries | 21 | Unbounded `SELECT * FROM orders` with no LIMIT or pagination. Will OOM on large tables. |
| 9 | MAJOR | Design | FP / Immutability | 10 | Module-level mutable `let orderCache` — shared mutable state across requests. |
| 10 | MINOR | Implementation | FP | 56-62 | `forEach` with side effect (pushing to external array). Should use `map` to transform. |
| 11 | MINOR | Implementation | Clean Code | 35 | Magic number `500` — no explanation of why this threshold triggers warehouse notification. |
| 12 | MINOR | Implementation | Error handling | 72 | `fetch` response not checked for HTTP errors. Failures will pass silently. |
| 13 | MINOR | Implementation | Clean Code | 69 | `console.log` in production code. Should use structured logger. |
| 14 | NIT | Style | Naming | 13 | Default export — prefer named export for refactoring safety and IDE support. |

## Coverage Check

- [x] Architecture (finding 4)
- [x] Security (findings 1, 2)
- [x] Performance (finding 8)
- [x] Design — SOLID (findings 5, 7)
- [x] Design — FP (findings 9, 10)
- [x] Implementation — Clean Code (findings 6, 11, 13)
- [x] Implementation — Error Handling (findings 3, 12)
- [x] Style (finding 14)
- [x] All severity levels represented

## Notes

- A thorough review may find additional issues not listed (e.g., missing `Content-Type` header on fetch, hardcoded URL).
- A `--relaxed` review should skip finding 14 (NIT) and may skip isolated MINOR findings.
