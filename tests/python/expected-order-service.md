# Expected Findings: Python — order_service.py

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Input validation | 39-42 | SQL injection via f-string in `text()`. User input directly interpolated into SQL. Use bound parameters. |
| 2 | BLOCKER | Security | Input validation | 77-78 | SQL injection via f-string in `search_orders`. Same pattern repeated. |
| 3 | BLOCKER | Security | Input validation | 67 | SQL injection inside N+1 loop — `order.id` interpolated into query string. |
| 4 | BLOCKER | Implementation | Error handling | 47-48 | Bare `except: pass` — catches and silently discards all exceptions including `KeyboardInterrupt` and `SystemExit`. |
| 5 | BLOCKER | Implementation | Clean Code | 19 | Mutable default argument `tags=[]`. Shared across calls — will accumulate values. |
| 6 | MAJOR | Performance | N+1 queries | 65-69 | N+1 query pattern: executing a query per order inside a loop. Use a JOIN or `selectinload`. |
| 7 | MAJOR | Performance | Bounded queries | 62 | Unbounded `SELECT * FROM orders` with no LIMIT or pagination. |
| 8 | MAJOR | Architecture | SRP | 35 | God function `create_order` — does input handling, raw SQL, caching, notification, and validation in one function. |
| 9 | MAJOR | Design | DTO / Validation | 35 | `body: dict` instead of a Pydantic `BaseModel`. No input validation, no schema, no OpenAPI docs. |
| 10 | MAJOR | Performance | Async consistency | 84-88 | Synchronous `requests.post()` in a function called from async route. Blocks the event loop. Use `httpx` or `aiohttp`. |
| 11 | MAJOR | Design | FP / Immutability | 14 | Module-level mutable `order_cache = {}` — shared mutable state across requests. |
| 12 | MINOR | Implementation | Clean Code | 52 | Magic number `500` — no explanation of business significance. |
| 13 | MINOR | Implementation | Clean Code | 90 | `print()` in production code — use structured logging. |
| 14 | MINOR | Implementation | Error handling | 89 | HTTP response status not checked. Failures pass silently. |
| 15 | MINOR | Performance | Timeouts | 85 | No timeout on `requests.post()` — can hang indefinitely. |
| 16 | MINOR | Implementation | Type hints | 26, 83 | Missing type hints on public functions `get_db` and `notify_warehouse`. |

## Coverage Check

- [x] Architecture (finding 8)
- [x] Security (findings 1, 2, 3)
- [x] Performance (findings 6, 7, 10, 15)
- [x] Design — SOLID (finding 9)
- [x] Design — FP (finding 11)
- [x] Implementation — Clean Code (findings 5, 12, 13)
- [x] Implementation — Error Handling (findings 4, 14)
- [x] Implementation — Testability (implicit: global state, sync calls not injectable)
- [x] All severity levels represented (no NIT in this sample — acceptable)

## Notes

- Finding 5 (mutable default) is Python-specific — tests that the language reference is loaded.
- Finding 10 (sync in async) is FastAPI-specific — tests framework rule coverage.
- Finding 6 (N+1) combined with finding 3 (SQL injection inside the loop) tests whether the reviewer catches both issues in the same code block.
