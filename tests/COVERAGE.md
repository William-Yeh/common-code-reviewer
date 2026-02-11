# Test Coverage Matrix

Maps every general rule from SKILL.md to at least one test sample + finding.

**Legend:**
- `TS1` = typescript/order-service.ts
- `TS2` = typescript/notification-service.ts
- `PY1` = python/order_service.py
- `PY2` = python/user_management.py
- `JV1` = java/OrderController.java
- `JV2` = java/PaymentService.java
- `GO1` = go/order_handler.go
- `GO2` = go/user_service.go

---

## Architecture

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Layer violations (domain → infrastructure) | TS2 #7, JV2 #7 | ✅ |
| Circular dependencies | — | ❌ Not testable in single-file samples. Requires multi-file test. |
| God classes/modules (SRP) | TS1 #4, PY1 #8, JV1 #4, GO1 #8 | ✅ |
| Anemic domain models | TS2 #8, PY2 #8, JV2 #8, GO2 #7 | ✅ |
| Missing/incorrect abstractions | TS2 #4 (OCP implies missing abstraction) | ✅ (indirect) |
| Tight coupling to frameworks | JV2 #7 (direct HTTP in domain) | ✅ |

## Security

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Missing input validation | TS1 #7, PY1 #9, JV1 #9 | ✅ |
| SQL injection | TS1 #1,#2, PY1 #1,#2,#3, JV1 #1,#2, GO1 #1,#2 | ✅ |
| Command injection | PY2 #1, JV2 #1, GO2 #1 | ✅ |
| XSS | TS2 #2 | ✅ |
| Path traversal | TS2 #1, PY2 #2, GO2 #2 | ✅ |
| Auth/authz gaps | TS2 #3, PY2 #3, JV2 #12, GO2 #3 | ✅ |
| Sensitive data exposure | JV2 #2 (card number logged), GO1 #15 (error details) | ✅ |
| Insecure defaults | GO1 #21 (no graceful shutdown) | ✅ (indirect) |
| Unsafe deserialization | — | ❌ Not covered. Low priority — less common in these stacks. |

## Performance

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| N+1 query patterns | PY1 #6, GO1 #10 | ✅ |
| Unbounded queries (no LIMIT) | TS1 #8, PY1 #7, JV1 #8, GO1 #11 | ✅ |
| Unnecessary allocations in hot paths | — | ❌ Requires performance-specific sample. Low priority for functional review. |
| Blocking calls in async contexts | PY1 #10 | ✅ |
| Missing caching for expensive ops | — | ❌ Context-dependent, hard to demonstrate in isolation. |
| Inefficient data structures | — | ❌ Requires algorithmic sample. |
| Unnecessary eager loading | — | ❌ Requires ORM relationship sample. |

## Design — SOLID

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| SRP | TS1 #4, PY1 #8, JV1 #4, GO1 #8 | ✅ |
| OCP | TS2 #4, PY2 #4, JV2 #4, GO2 #4 | ✅ |
| LSP | TS2 #5, PY2 #6, JV2 #5 | ✅ (Go excluded — no class inheritance) |
| ISP | TS2 #6, PY2 #7, JV2 #6, GO2 #6 | ✅ |
| DIP | TS1 #5, JV1 #5, TS2 #7, JV2 #7 | ✅ |

## Design — Functional Programming

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Mutable where immutable works | TS1 #9, PY1 #11, GO1 #9 | ✅ |
| Hidden side effects | TS2 #9, PY2 #9, JV2 #9, GO2 #8 | ✅ |
| Shared mutable state | TS1 #9, PY1 #11, JV1 #16, GO1 #9 | ✅ |
| Imperative loops where FP clearer | TS1 #10 (forEach → map) | ✅ |
| Missing Result/Option types | — | ❌ Language-specific. Partially tested via error handling rules. |

## Implementation — Clean Code

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Names not revealing intent | TS2 #15, PY2 #15, JV2 #17, GO2 #16 | ✅ |
| Functions too long / mixed abstraction | TS2 #18, PY2 #14, JV2 #18, GO2 #15 | ✅ |
| Magic numbers/strings | TS1 #11, PY1 #12, JV2 #14 | ✅ |
| Dead code / commented-out code | TS2 #16,#17, PY2 #16, JV2 #16, GO2 #17 | ✅ |
| Deep nesting (3+ levels) | TS2 #13, PY2 #12, JV2 #13, GO2 #12 | ✅ |
| Code duplication | TS2 #14, PY2 #13,#17, JV2 #15, GO2 #14,#18 | ✅ |

## Implementation — Testability

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Hard-coded dependencies | TS2 #11,#12, PY2 #10, JV2 #11, GO2 #10 | ✅ |
| Side effects coupled to logic | TS2 #9, PY2 #9, JV2 #9, GO2 #8 | ✅ |
| Non-deterministic behavior | TS2 #10, PY2 #11, JV2 #10, GO2 #9 | ✅ |
| Complex constructors | JV2 (PaymentService constructor with side effect) | ✅ (indirect) |
| Private methods with significant logic | — | ❌ Hard to demonstrate without larger class. Low priority. |

## Style

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Naming convention inconsistencies | TS1 #14, GO2 #19 | ✅ |
| Minor readability improvements | Various NIT findings across all samples | ✅ |

---

## Summary

| Category | Rules | Covered | Not Covered |
|----------|-------|---------|-------------|
| Architecture | 6 | 5 | 1 (circular deps) |
| Security | 8 | 7 | 1 (unsafe deserialization) |
| Performance | 7 | 3 | 4 (allocations, caching, data structures, eager loading) |
| Design — SOLID | 5 | 5 | 0 |
| Design — FP | 5 | 4 | 1 (Result/Option types) |
| Clean Code | 6 | 6 | 0 |
| Testability | 5 | 4 | 1 (private methods) |
| Style | 2 | 2 | 0 |
| **Total** | **44** | **36** | **8** |

**Coverage: 82% (36/44)**

### Uncovered Rules — Analysis

| Rule | Why Not Covered | Risk |
|------|----------------|------|
| Circular dependencies | Requires multi-file sample | Low — LLM can recognize this from imports |
| Unsafe deserialization | Rare in TS/Python/Go, Java-specific (ObjectInputStream) | Low |
| Unnecessary allocations | Requires profiling context | Low — perf micro-optimization |
| Missing caching | Context-dependent | Low — architecture decision |
| Inefficient data structures | Requires algorithmic code | Low |
| Unnecessary eager loading | Requires ORM relationships | Medium — could add to PY1/JV1 |
| Missing Result/Option types | Covered indirectly via error handling | Low |
| Private methods with logic | Requires larger class context | Low |

The 8 uncovered rules are either hard to demonstrate in single-file samples or low-risk items that LLMs handle well without explicit examples.
