# Expected Findings: Python — user_management.py

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Command injection | 147-153 | `subprocess.run` with `shell=True` and unsanitized user input. Attacker can inject arbitrary commands via `username` or `output_format`. |
| 2 | BLOCKER | Security | Path traversal | 158-160 | User-controlled `user_id` used directly in file path. Attacker can read arbitrary files. |
| 3 | MAJOR | Security | Auth/Authz | 164-166 | `delete_user` performs no authorization check. Any user can delete any other user. |
| 4 | MAJOR | Design | OCP | 55-63 | `get_permissions` uses if/elif chain on role string. Every new role requires modifying this function. Use a role→permissions mapping dict or strategy. |
| 5 | MAJOR | Design | OCP | 55-63 | Missing else clause — returns `None` implicitly for unknown roles. Should raise `ValueError` or return empty list. |
| 6 | MAJOR | Design | LSP | 46-48 | `EmployeeDiscount.calculate()` returns `50.0` (absolute dollars) instead of a fraction between 0-1. Callers using `total * (1 - discount)` get negative prices. |
| 7 | MAJOR | Design | ISP | 14-27 | `IUserRepository` ABC has 8 abstract methods. A read-only repository implementation would need to stub 6 methods. Split into `ReadRepository`, `WriteRepository`, `ReportRepository`. |
| 8 | MAJOR | Architecture | Anemic domain | 68-76 | `User` class is a pure data bag. All behavior (permissions, deactivation, validation) lives in external functions. Move domain logic into the entity. |
| 9 | MAJOR | Design | FP / Side effects | 83-91 | `validate_user_data` writes to `/var/log/validation.log` and sends HTTP analytics. Function name implies pure validation. |
| 10 | MAJOR | Implementation | Testability | 99 | `load_config` hardcodes filesystem path — cannot test without real `/etc/app/config.json`. Inject config path or config object. |
| 11 | MAJOR | Implementation | Testability | 103 | `deactivate_inactive_users` uses `datetime.now()` directly. Non-deterministic — tests break across time boundaries. Inject a clock. |
| 12 | MINOR | Implementation | Clean Code | 105-109 | Deep nesting — 4 levels of `if` in `deactivate_inactive_users`. Flatten with early `continue` or extract a `should_deactivate` predicate. |
| 13 | MINOR | Implementation | Clean Code | 117-124 | Code duplication — role-counting logic with if/elif chain. Use `Counter(u.role for u in users)`. |
| 14 | MINOR | Implementation | Clean Code | 113 | Mixed abstraction levels in `generate_user_report` — config loading, counting, formatting, file I/O all in one method. |
| 15 | MINOR | Implementation | Clean Code | 135-141 | Bad naming: `proc`, `d`, `tmp`, `x`, `flag`. Not intention-revealing. |
| 16 | MINOR | Implementation | Clean Code | 145-150 | Dead code: `_old_send_welcome_email` is never called. Remove it. |
| 17 | MINOR | Implementation | Clean Code | 139-140 | Duplicated email validation logic — same `"@" in email` check as in `validate_user_data`. |
| 18 | NIT | Design | Type safety | 72-73 | `role: str` and `status: str` — use `Literal["admin", "editor", ...]` or `StrEnum`. |

## Coverage Check (General Principles)

- [x] OCP (findings 4, 5)
- [x] LSP (finding 6)
- [x] ISP (finding 7)
- [x] Architecture — anemic domain (finding 8)
- [x] FP — hidden side effects (finding 9)
- [x] Testability — hard-coded dependencies (finding 10)
- [x] Testability — non-deterministic (finding 11)
- [x] Clean Code — deep nesting (finding 12)
- [x] Clean Code — code duplication (findings 13, 17)
- [x] Clean Code — bad naming (finding 15)
- [x] Clean Code — dead code (finding 16)
- [x] Clean Code — mixed abstraction levels (finding 14)
- [x] Security — command injection (finding 1)
- [x] Security — path traversal (finding 2)
- [x] Security — auth gaps (finding 3)
