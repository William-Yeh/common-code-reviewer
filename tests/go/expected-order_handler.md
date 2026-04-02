# Expected Findings: Go — order_handler.go

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Input validation | 44-49 | SQL injection via `fmt.Sprintf`. User input directly interpolated into SQL. Use parameterized queries (`$1`, `$2`). |
| 2 | BLOCKER | Security | Input validation | 87 | SQL injection inside N+1 loop. `id` interpolated into query string. |
| 3 | BLOCKER | Implementation | Error handling | 38-39 | `ShouldBindJSON` error ignored. Invalid JSON silently proceeds with zero-value body. |
| 4 | BLOCKER | Implementation | Error handling | 41 | Unsafe type assertion `body["customer_id"].(string)` without comma-ok pattern. Will panic on missing or non-string values. |
| 5 | BLOCKER | Implementation | Error handling | 82 | `rows.Scan` error ignored. Corrupted data silently propagated. |
| 6 | BLOCKER | Implementation | Error handling | 85 | Error discarded with blank identifier `_` on N+1 query. Query failures silently produce nil rows. |
| 7 | BLOCKER | Performance | Resource leak | 78 | Missing `defer rows.Close()` after `db.Query`. Connection leak will exhaust connection pool. |
| 8 | MAJOR | Architecture | SRP | 35 | God function `CreateOrder` — handles binding, SQL, caching, and notification. Separate into handler → service → repository. |
| 9 | MAJOR | Design | FP / Immutability | 19-22 | Package-level mutable globals: `db`, `orderCache`. Inject dependencies instead. |
| 10 | MAJOR | Performance | N+1 queries | 85-94 | N+1 query: executing `SELECT ... FROM order_items` per order inside a loop. Use a JOIN or batch query. |
| 11 | MAJOR | Performance | Bounded queries | 76 | Unbounded `SELECT ... FROM orders` with no LIMIT or pagination. |
| 12 | MAJOR | Design | Concurrency | 61 | Goroutine `go notifyWarehouse(body)` without lifecycle management. No `errgroup`, no context cancellation — goroutine leak. |
| 13 | MAJOR | Design | Type safety | 37, 104 | `map[string]interface{}` used for request body and throughout. Define typed structs for Order, OrderItem. |
| 14 | MAJOR | Implementation | Error handling | 29-30 | `InitDB` logs error but continues execution. Subsequent calls to `db` will nil-pointer panic. Should return error or fatal. |
| 15 | MINOR | Security | Error exposure | 54, 78 | Internal error details leaked to client via `err.Error()` in JSON response. Return generic message, log details. |
| 16 | MINOR | Implementation | Error handling | 106 | `json.Marshal` error ignored with blank identifier. |
| 17 | MINOR | Design | Context | 26, 104 | Missing `context.Context` parameter on `InitDB` and `notifyWarehouse`. Cannot respect timeouts or cancellation. |
| 18 | MINOR | Performance | Timeouts | 109 | No timeout on `http.Post` — will use `http.DefaultClient` with no timeout. Can hang indefinitely. |
| 19 | MINOR | Implementation | Error handling | 113 | Error logged without wrapping: `log.Println(err)`. Use `fmt.Errorf("notifying warehouse: %w", err)`. |
| 20 | NIT | Implementation | Modern features | 10 | `log.Println` — consider `slog` for structured logging (Go 1.21+). |
| 21 | NIT | Design | Graceful shutdown | 119 | No graceful shutdown. `gin.Engine` returned without `http.Server` wrapping for `Shutdown(ctx)`. |

## Coverage Check

- [x] Architecture (finding 8)
- [x] Security (findings 1, 2, 15)
- [x] Performance (findings 7, 10, 11, 18)
- [x] Design — SOLID (finding 9)
- [x] Design — Concurrency (finding 12)
- [x] Design — Type safety (finding 13)
- [x] Design — Context (finding 17)
- [x] Implementation — Error Handling (findings 3, 4, 5, 6, 14, 16, 19)
- [x] Implementation — Modern features (finding 20)
- [x] Style (finding 21)
- [x] All severity levels represented

## Notes

- Go test has the highest BLOCKER count (7) because Go's explicit error handling creates more opportunities for ignored errors — this is intentional to test error handling review depth.
- Findings 5 and 6 (ignored Scan/Query errors) are Go-specific review rules — tests that the language reference is loaded.
- Finding 12 (goroutine leak) tests concurrency review from the Go reference.
- The reviewer should note that the `bytes` import is missing (line 109), which would be a compilation error, but since this is a test sample the focus is on design/architecture issues.
