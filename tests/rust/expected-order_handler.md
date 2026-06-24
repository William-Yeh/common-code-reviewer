# Expected Findings: Rust — order_handler.rs

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | SQL injection | 8-9 | `format!("... id = '{}'", order_id)` interpolates user input into SQL. Use parameterized queries (`sqlx::query!` / bind parameters). |
| 2 | BLOCKER | Security | SQL injection | 18 | `status` concatenated into the query string. Same fix — bind parameters, never `format!`. |
| 3 | BLOCKER | Security | Command injection | 26-30 | `sh -c "invoice-gen --order {order_id}"` runs user input through a shell. Pass args directly: `Command::new("invoice-gen").args(["--order", order_id])`, no `sh -c`. |
| 4 | BLOCKER | Security | Path traversal | 35-36 | User-controlled `file_name` joined into a path. `../../etc/passwd` escapes the dir. Validate/canonicalize and confirm the path stays under `/var/receipts`. |
| 5 | BLOCKER | Implementation | Error handling (unwrap) | 11 | `.unwrap()` on a fallible DB call in library code panics the caller's process. Return `Result<Order, _>` and propagate with `?`. |
| 6 | BLOCKER | Implementation | Error handling (unwrap) | 28, 31, 37, 67 | Pervasive `.unwrap()`/`.expect()` on fallible operations (command output, UTF-8, fs read, DB save). Each is a latent panic. Return `Result`. |
| 7 | BLOCKER | Performance | Blocking in async | 71-73 | `std::fs::read_to_string` is a blocking syscall inside `async fn` — it stalls the runtime worker thread. Use `tokio::fs` or `spawn_blocking`. |
| 8 | BLOCKER | Design | Async / lock across await | 62-66 | `state.lock()` guard is held across `db.flush_metrics().await`. With a std `Mutex` this blocks the executor and risks deadlock. Drop the guard before awaiting, or use `tokio::sync::Mutex` scoped tightly. |
| 9 | MAJOR | Performance | N+1 query | 52-57 | One `query_one` per order inside the loop. Batch with a single `WHERE customer_id IN (...)` query. |
| 10 | MAJOR | Performance | Unbounded query | 18-20 | `orders_by_status` has no `LIMIT`/pagination — loads the entire matching set into memory. |
| 11 | MAJOR | Implementation | SRP | 76-85 | `process_order` validates, charges payment, persists, and emails. Four responsibilities. Split into focused units. |
| 12 | MAJOR | Implementation | Swallowed error | 81 | `let _ = charge_card(&order);` discards the payment `Result`. A failed charge proceeds to save+confirm as success. |
| 13 | MINOR | Security | Sensitive data exposure | 89 | Full `card_number` written to stdout/logs. Mask all but the last 4 digits, or omit. |
| 14 | MINOR | Design | Ownership / clone | 58 | `order.clone()` clones an owned `Order` every iteration. Restructure to move or borrow instead of cloning in the hot loop. |
| 15 | MINOR | Design | Result over bool | 77-78 | `process_order` returns `bool`, erasing the failure reason. Return `Result<(), OrderError>` so callers know *why* it failed. |
| 16 | NIT | Implementation | Magic number | 95 | `30` (stale threshold in days) is unexplained. Extract `const STALE_AFTER_DAYS: u64 = 30;`. |

## Coverage Check (General + Rust Principles)

- [x] Security — SQL injection (findings 1, 2)
- [x] Security — command injection (finding 3)
- [x] Security — path traversal (finding 4)
- [x] Security — sensitive data exposure (finding 13)
- [x] Rust — `.unwrap()`/`panic` in library code (findings 5, 6)
- [x] Rust — blocking call in async (finding 7)
- [x] Rust — lock held across `.await` (finding 8)
- [x] Performance — N+1 query (finding 9)
- [x] Performance — unbounded query (finding 10)
- [x] SRP (finding 11)
- [x] Swallowed / discarded error (finding 12)
- [x] Rust — clone-to-satisfy-borrow-checker in hot path (finding 14)
- [x] FP / error model — Result over bool (finding 15)
- [x] Magic number (finding 16)

## Notes

- This sample uses stub `unimplemented!()` bodies for helpers; the review targets design/security/error-handling issues, not compilation of stubs.
- `Send`/`Sync` data-race rules are enforced by the compiler and so are not exercised here; the async-specific runtime hazards (blocking, lock-across-await) are what the reviewer must catch.
