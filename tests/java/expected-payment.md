# Expected Findings: Java — PaymentService.java

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Command injection | 171-173 | `ProcessBuilder("sh", "-c", "payment-export --format " + format)` — unsanitized `format` parameter passed to shell. Use `ProcessBuilder` with argument list, no shell. |
| 2 | BLOCKER | Security | Sensitive data | 87 | Credit card number logged via `System.out.println`. PCI-DSS violation — card numbers must never be logged in plain text. |
| 3 | BLOCKER | Implementation | Error handling | 117 | Empty catch block in `calculateFee` — `IOException` silently swallowed. Fee log failure goes unnoticed. |
| 4 | MAJOR | Design | OCP | 71 | `processPayment` uses switch on payment method string. Every new method requires modifying this function. Use strategy pattern or polymorphism. |
| 5 | MAJOR | Design | LSP | 47-49 | `LegacyGateway.pay()` returns `null` for large amounts. Base class contract says "never returns null; throws on failure." Callers get `NullPointerException`. |
| 6 | MAJOR | Design | ISP | 14-21 | `PaymentProcessor` interface has 7 methods. A refund-only implementation must stub 5 unrelated methods. Split into focused interfaces. |
| 7 | MAJOR | Architecture | Layer violation | 60-63 | `PaymentService` directly creates `HttpURLConnection` in constructor. Domain logic tightly coupled to HTTP infrastructure. Inject a gateway client. |
| 8 | MAJOR | Architecture | Anemic domain | 157-165 | `Payment` class is a pure data bag with public mutable fields. All behavior lives in `PaymentService`. Move validation and state transitions into domain object. |
| 9 | MAJOR | Design | FP / Side effects | 111-116 | `calculateFee` writes to filesystem. Function name implies pure calculation. Extract logging side effect. |
| 10 | MAJOR | Implementation | Testability | 121 | `isWithinRefundWindow` uses `LocalDateTime.now()` directly. Non-deterministic — inject a `Clock`. |
| 11 | MAJOR | Implementation | Testability | 126 | `loadGatewayConfig` hardcodes `/etc/payments/gateway.properties`. Cannot test without real filesystem. Inject path or config object. |
| 12 | MAJOR | Security | Auth/Authz | 169 | `exportAll` has no authorization check. Any caller can export all payment transactions. |
| 13 | MINOR | Implementation | Clean Code | 80-88 | Deep nesting — 3 levels of `if` inside switch case. Flatten with early returns or extract validation. |
| 14 | MINOR | Implementation | Clean Code | 106 | Magic numbers `0.029` and `0.30` — credit card processing fees should be named constants. |
| 15 | MINOR | Implementation | Clean Code | 140 | Code duplication — amount validation `amt <= 0 \|\| amt >= 100000` repeated from `processPayment`. Extract shared validation. |
| 16 | MINOR | Implementation | Clean Code | 143 | Dead code — `debugTimestamp` computed but never used. |
| 17 | MINOR | Implementation | Clean Code | 153-154 | Bad naming: `Util.process`, `data`, `t`, `res`, `d`, `a` — none reveal intent. |
| 18 | MINOR | Implementation | Clean Code | 136 | Mixed abstraction levels — `refund` does config loading, validation, and response building in one method. |
| 19 | MINOR | Implementation | Error handling | 129 | `e.printStackTrace()` in production — use SLF4J logger. |
| 20 | MINOR | Implementation | Resource management | 114 | `FileWriter` not wrapped in try-with-resources. Resource leak if `write()` throws. |
| 21 | NIT | Design | Type safety | 160, 162 | `String method` and `String status` — use enums or sealed types. |
| 22 | NIT | Design | Type safety | 161 | `double amount` for money — use `BigDecimal`. |

## Coverage Check (General Principles)

- [x] OCP (finding 4)
- [x] LSP (finding 5)
- [x] ISP (finding 6)
- [x] Architecture — layer violation (finding 7)
- [x] Architecture — anemic domain (finding 8)
- [x] FP — hidden side effects (finding 9)
- [x] Testability — non-deterministic (finding 10)
- [x] Testability — hard-coded dependencies (finding 11)
- [x] Clean Code — deep nesting (finding 13)
- [x] Clean Code — magic numbers (finding 14)
- [x] Clean Code — code duplication (finding 15)
- [x] Clean Code — dead code (finding 16)
- [x] Clean Code — bad naming (finding 17)
- [x] Clean Code — mixed abstraction levels (finding 18)
- [x] Security — command injection (finding 1)
- [x] Security — sensitive data exposure (finding 2)
- [x] Security — auth gaps (finding 12)
