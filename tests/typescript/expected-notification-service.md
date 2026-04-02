# Expected Findings: TypeScript — notification-service.ts

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Path traversal | 148 | User-controlled `template` query param used directly in `fs.readFileSync` path. Attacker can read arbitrary files via `../../etc/passwd`. |
| 2 | BLOCKER | Security | XSS | 151-152 | User input `req.query.name` rendered directly into HTML without escaping. |
| 3 | MAJOR | Security | Auth/Authz | 145 | No authentication or authorization check on the preview endpoint. |
| 4 | MAJOR | Design | OCP | 62-97 | `sendNotification` requires modification for every new notification type. Violates Open-Closed Principle. Use strategy pattern — map of type → handler. |
| 5 | MAJOR | Design | LSP | 42-49 | `Square` extends `Rectangle` but silently couples width and height. Code treating a `Square` as a `Rectangle` with independent dimensions gets unexpected behavior. |
| 6 | MAJOR | Design | ISP | 14-22 | `INotificationChannel` has 7 methods. An SMS-only implementation would need to stub `sendEmail`, `sendPush`, `sendSlack`, `generateReport`, etc. Split into focused interfaces. |
| 7 | MAJOR | Architecture | Layer violation | 9-10 | Domain logic directly imports `axios` and `fs`. Infrastructure concerns (HTTP, filesystem) should be behind abstractions injected from outside. |
| 8 | MAJOR | Architecture | Anemic domain | 157-164 | `Notification` class is a pure data bag. All behavior (sending, scheduling, stats) lives in standalone functions. Move behavior into the domain object or use a proper service layer. |
| 9 | MAJOR | Design | FP / Side effects | 104-110 | `calculateNotificationStats` has hidden side effects: `console.log`, `fs.writeFileSync`, `axios.post`. Function name implies pure calculation. Extract side effects or rename. |
| 10 | MAJOR | Implementation | Testability | 115-116 | `shouldSendNow` uses `Date.now()` directly — non-deterministic, untestable. Inject a clock/time provider. |
| 11 | MAJOR | Implementation | Testability | 119-120 | `loadTemplate` hardcodes filesystem path. Cannot test without real filesystem. Inject a template loader. |
| 12 | MAJOR | Implementation | Testability | 67-68, 72-73 | `sendNotification` hardcodes `axios.post` calls — cannot mock without module patching. Accept an HTTP client parameter or use DI. |
| 13 | MINOR | Implementation | Clean Code | 64-96 | Deep nesting — 3+ levels of `if` inside `sendNotification`. Flatten with early returns or extract per-type handlers. |
| 14 | MINOR | Implementation | Clean Code | 82-87, 67-71 | Code duplication — HTTP POST logic repeated for each notification type with minor variations. Extract a common sender. |
| 15 | MINOR | Implementation | Clean Code | 134-138 | Bad naming: `d`, `temp`, `x` — not intention-revealing. Use `notifications`, `validEmails`, `index` (or `for...of`). |
| 16 | MINOR | Implementation | Clean Code | 128 | Dead code: `debugInfo` variable assigned but never used. |
| 17 | MINOR | Implementation | Clean Code | 143-144 | Dead code: `legacyNotify` function never called. Remove instead of keeping "just in case." |
| 18 | MINOR | Implementation | Clean Code | 123-131 | `processScheduled` mixes abstraction levels — file I/O, scheduling logic, template rendering, and sending all in one method. |
| 19 | NIT | Design | Type safety | 161, 163 | `type: string` and `status: string` — should use `NotificationType` union and a status union. |

## Coverage Check (General Principles)

- [x] OCP (finding 4)
- [x] LSP (finding 5)
- [x] ISP (finding 6)
- [x] Architecture — layer violation (finding 7)
- [x] Architecture — anemic domain (finding 8)
- [x] FP — hidden side effects (finding 9)
- [x] Testability — non-deterministic (finding 10)
- [x] Testability — hard-coded dependencies (findings 11, 12)
- [x] Clean Code — deep nesting (finding 13)
- [x] Clean Code — code duplication (finding 14)
- [x] Clean Code — bad naming (finding 15)
- [x] Clean Code — dead code (findings 16, 17)
- [x] Clean Code — mixed abstraction levels (finding 18)
- [x] Security — path traversal (finding 1)
- [x] Security — XSS (finding 2)
- [x] Security — auth gaps (finding 3)
