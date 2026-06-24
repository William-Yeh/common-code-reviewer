# Expected Findings: Rust — user_service.rs

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Implementation | Unsafe / SAFETY | 130 | `data.get_unchecked(0)` in an `unsafe` block with no `// SAFETY:` comment — and it's UB when `data` is empty. Use the safe `data.first()` / `data.get(0)` which returns `Option`. |
| 2 | MAJOR | Design | ISP | 15-24 | `UserStore` trait has 8 methods. A read-only consumer must still implement `save`, `delete`, `bulk_import`, `export_csv`, etc. Split into `UserReader` / `UserWriter` / `UserReporter`. |
| 3 | MAJOR | Design | OCP | 31-52 | `handle_user_action` matches on an action `&str`; each new action edits this function. Model actions as an `enum` so the `match` is exhaustive and the compiler enforces new arms. |
| 4 | MAJOR | Design | OCP / silent default | 50 | The `_ => Ok(())` arm makes unknown actions silently succeed. Return an error for unrecognized actions. |
| 5 | MAJOR | Architecture | Anemic domain | 57-66 | `User` is a pure data bag — all behavior (activation, counting, deactivation) lives in free functions and `UserService`. |
| 6 | MAJOR | Design | Error type erasure | 17-24, 35, 79 | Public API returns `Box<dyn Error>`, erasing the error variant so callers can't match on it. Expose a typed error enum (e.g. via `thiserror`). |
| 7 | MAJOR | Design | FP / hidden side effects | 70-77 | `count_active_users` is named as a pure count but writes `/tmp/user-stats.txt`. Extract the side effect; keep the counter pure. |
| 8 | MAJOR | Implementation | Testability | 73, 84-88 | `SystemTime::now()` and the hardcoded `/etc/app/users.json` path make these non-deterministic and untestable. Inject a clock and a config source/`Reader`. |
| 9 | MINOR | Design | Ownership / Arc<Mutex> overuse | 82 | `cache: Arc<Mutex<HashMap<...>>>` introduces shared mutability before it's shown to be needed. If the service has a single owner, `&mut self` + a plain `HashMap` avoids the lock and its panic surface. |
| 10 | MINOR | Design | Clone-to-compile | 96-97, 109, 140 | `user.clone()` / `x.clone()` clone whole `User` values (in `cache_user`, in the loop in `deactivate_inactive`, and in `proc`) to satisfy the borrow checker. Restructure to move or store references/`Arc<User>`. |
| 11 | MINOR | Implementation | Clean Code (nesting) | 103-117 | `deactivate_inactive` nests `if` 4 levels deep. Flatten with early `continue`, or extract a `should_deactivate(&User, days)` predicate and `filter`. |
| 12 | MINOR | Implementation | Clean Code (naming) | 135-143 | `proc`, `d`, `f`, `r`, `x` reveal no intent. Rename to `users_with_role(users, role)` etc. |
| 13 | MINOR | Implementation | Clean Code (dead code) | 146-148 | `old_notify` is never called. Remove it. |
| 14 | MINOR | Design | DIP | 152-154 | `remove_user` takes the concrete `&mut PostgresStore` instead of `&mut impl UserStore`. Depend on the abstraction so it works with any store and is testable with a fake. |
| 15 | NIT | Design | Newtype / type safety | 61, 62 | `role: String` and `status: String` should be `Role` / `Status` enums — the stringly-typed fields permit invalid values the compiler could reject. |
| 16 | NIT | Implementation | Error handling | 75 | `std::fs::write(...).unwrap()` in a non-test path panics on any I/O error. Propagate with `?` instead. |

## Coverage Check (General + Rust Principles)

- [x] ISP (finding 2)
- [x] OCP — stringly-typed match + silent default (findings 3, 4)
- [x] Architecture — anemic domain (finding 5)
- [x] DIP — concrete instead of abstraction (finding 14)
- [x] FP — hidden side effects (finding 7)
- [x] Testability — non-deterministic + hard-coded deps (finding 8)
- [x] Clean Code — deep nesting (finding 11)
- [x] Clean Code — bad naming (finding 12)
- [x] Clean Code — dead code (finding 13)
- [x] Rust — `unsafe` without SAFETY comment / UB (finding 1)
- [x] Rust — `Box<dyn Error>` in public lib API (finding 6)
- [x] Rust — `Arc<Mutex>` overuse (finding 9)
- [x] Rust — clone-to-satisfy-borrow-checker (finding 10)
- [x] Rust — newtype/enum over stringly-typed (finding 15)

## Notes

- LSP is intentionally **not** exercised here: Rust has no implementation inheritance, so the classic Liskov substitution scenario doesn't apply (same exclusion as the Go samples). LSP coverage lives in the TS, Python, and Java fixtures.
- This sample emphasizes Rust-idiom rules (`unsafe`, ownership/clone, error-type design, `Arc<Mutex>`) that the other languages' fixtures cannot demonstrate.
