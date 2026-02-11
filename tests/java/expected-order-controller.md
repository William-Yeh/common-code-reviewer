# Expected Findings: Java — OrderController.java

## Expected Verdict: REQUEST CHANGES

## Findings

| # | Severity | Category | Principle | Line(s) | Description |
|---|----------|----------|-----------|---------|-------------|
| 1 | BLOCKER | Security | Input validation | 63-68 | SQL injection via string concatenation in `createOrder`. User input directly concatenated into SQL. Use parameterized queries. |
| 2 | BLOCKER | Security | Input validation | 84-85 | SQL injection via string concatenation in `searchOrders`. Same pattern repeated. |
| 3 | BLOCKER | Implementation | Error handling | 76 | `e.printStackTrace()` instead of proper logging. In production, stack traces go to stderr and may be lost. Use SLF4J logger. |
| 4 | MAJOR | Architecture | SRP | 38 | God class — `OrderController` acts as controller, service, and repository. Should separate into layered architecture. |
| 5 | MAJOR | Design | DIP | 43-46 | Field injection via `@Autowired`. Use constructor injection for testability and explicit dependency declaration. |
| 6 | MAJOR | Architecture | DTO separation | 13, 59, 81 | JPA `Entity` used directly as `@RequestBody` and response. Exposes internal DB model to API consumers. Use DTOs (records). |
| 7 | MAJOR | Design | Type safety | 49, 52 | Raw types: `Map cache = new HashMap()` and `List getAllOrders()` without generic parameters. |
| 8 | MAJOR | Performance | Bounded queries | 54 | Unbounded JPQL query `SELECT o FROM Order o` with no pagination (`setMaxResults`, `Pageable`). |
| 9 | MAJOR | Design | Validation | 59 | No `@Valid` on `@RequestBody`. No input validation constraints. Entity lacks Bean Validation annotations. |
| 10 | MAJOR | Implementation | Clean Code | 21 | `double` for monetary value `price`. Floating-point precision causes rounding errors. Use `BigDecimal`. |
| 11 | MAJOR | Performance | Timeouts | 97-100 | No timeout set on `HttpURLConnection`. No try-with-resources for streams. Connection/stream leak risk. |
| 12 | MINOR | Design | Modern features | 13-34 | Verbose entity class with manual getters/setters. Consider `record` for DTOs or Lombok `@Data` for entities (with caveats). |
| 13 | MINOR | Implementation | Error handling | 93 | `throws Exception` — overly broad. Declare specific exception types. |
| 14 | MINOR | Design | Transaction | 71 | No `@Transactional` annotation on write operation. Read-after-write without transaction boundary. |
| 15 | MINOR | Design | Modern features | 91 | `.collect(Collectors.toList())` — use `.toList()` (JDK 16+) for unmodifiable list. |
| 16 | NIT | Design | Thread safety | 49 | `HashMap` cache without synchronization. Concurrent requests cause data races. Consider `ConcurrentHashMap` or proper caching solution. |

## Coverage Check

- [x] Architecture (findings 4, 6)
- [x] Security (findings 1, 2)
- [x] Performance (findings 8, 11)
- [x] Design — SOLID (findings 5, 9)
- [x] Design — Modern features (findings 7, 12, 15)
- [x] Implementation — Clean Code (findings 3, 10)
- [x] Implementation — Error Handling (findings 3, 13)
- [x] Style (finding 16)
- [x] All severity levels represented

## Notes

- Finding 10 (`double` for money) is a classic enterprise Java mistake — tests domain-specific review depth.
- Finding 6 (entity as DTO) is a Spring Boot-specific rule — tests framework reference loading.
- Finding 16 is listed as NIT but could reasonably be MAJOR in high-concurrency scenarios. The reviewer should adjust based on context.
