# Expected Findings: Go — user_service.go

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Command injection | 160-162 | `exec.Command("sh", "-c", ...)` with unsanitized `username` and `format`. Use `exec.Command("user-export", "--user", username, "--format", format)` without shell. |
| 2 | BLOCKER | Security | Path traversal | 167 | User-controlled `userID` used directly in file path. Attacker can read arbitrary files. Sanitize or validate format. |
| 3 | MAJOR | Security | Auth/Authz | 171-172 | `DeleteUser` has no authorization check. Any caller can delete any user. |
| 4 | MAJOR | Design | OCP | 34-51 | `HandleUserAction` uses switch on action string. Every new action requires modifying this function. Use a map of action → handler function. |
| 5 | MAJOR | Design | OCP | 34-51 | No default case — unknown actions silently return nil. Should return an error for unrecognized actions. |
| 6 | MAJOR | Design | ISP | 19-28 | `UserStore` interface has 8 methods. A read-only consumer must implement `Delete`, `BulkImport`, `ExportCSV`, etc. Split into `UserReader`, `UserWriter`, `UserReporter`. |
| 7 | MAJOR | Architecture | Anemic domain | 56-64 | `User` struct is a pure data bag. All behavior (activation, deactivation, counting, reporting) lives in external functions. |
| 8 | MAJOR | Design | FP / Side effects | 77-81 | `CountActiveUsers` writes to filesystem and sends HTTP request. Function name implies pure counting. Extract side effects. |
| 9 | MAJOR | Implementation | Testability | 91 | `IsInactive` uses `time.Since` (depends on `time.Now()` internally). Non-deterministic. Accept a `now time.Time` parameter or inject a clock. |
| 10 | MAJOR | Implementation | Testability | 95-96 | `LoadConfig` hardcodes `/etc/app/users.json`. Cannot test without real filesystem. Accept a path or `io.Reader`. |
| 11 | MINOR | Implementation | Error handling | 101 | `json.Unmarshal` error ignored. Malformed config silently produces zero-value map. |
| 12 | MINOR | Implementation | Clean Code | 107-116 | Deep nesting — 4 levels of `if` in `DeactivateInactive`. Flatten with `continue` or extract a `shouldDeactivate` function. |
| 13 | MINOR | Implementation | Clean Code | 121 | `LoadConfig` error ignored with `_`. Config loading failure silently produces nil map, causing panics downstream. |
| 14 | MINOR | Implementation | Clean Code | 124-130 | Code duplication — role-counting via if/else chain. Use a map counter: `counts[u.Role]++`. |
| 15 | MINOR | Implementation | Clean Code | 120 | Mixed abstraction levels — `GenerateReport` does config loading, counting, formatting, and file I/O in one function. |
| 16 | MINOR | Implementation | Clean Code | 141-142 | Bad naming: `proc`, `d`, `f`, `r`, `x`. Not intention-revealing. |
| 17 | MINOR | Implementation | Clean Code | 150-152 | Dead code: `oldNotify` function never called. Remove it. |
| 18 | MINOR | Implementation | Clean Code | 147 | Duplicated email validation — same check could be extracted into a shared function. |
| 19 | NIT | Design | Type safety | 61, 62 | `Role string` and `Status string` — define typed constants or use a custom type with iota. |
| 20 | NIT | Implementation | Modern features | 36-49 | `fmt.Println` for logging — use `slog` for structured logging (Go 1.21+). |

## Coverage Check (General Principles)

- [x] OCP (findings 4, 5)
- [x] ISP (finding 6)
- [x] Architecture — anemic domain (finding 7)
- [x] FP — hidden side effects (finding 8)
- [x] Testability — non-deterministic (finding 9)
- [x] Testability — hard-coded dependencies (finding 10)
- [x] Clean Code — deep nesting (finding 12)
- [x] Clean Code — code duplication (findings 14, 18)
- [x] Clean Code — bad naming (finding 16)
- [x] Clean Code — dead code (finding 17)
- [x] Clean Code — mixed abstraction levels (finding 15)
- [x] Security — command injection (finding 1)
- [x] Security — path traversal (finding 2)
- [x] Security — auth gaps (finding 3)

## Notes

- Missing `bytes` import (line 80) would cause compile error. As a test sample, focus is on design/architecture issues.
- Go doesn't have LSP in the classic OOP sense (no class inheritance), so LSP is not tested here. It's covered in the TS, Python, and Java samples.
