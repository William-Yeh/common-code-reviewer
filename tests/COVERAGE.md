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
- `RS1` = rust/order_handler.rs
- `RS2` = rust/user_service.rs
- `DF1` = dockerfile/Dockerfile-app
- `DF2` = dockerfile/Dockerfile-builder

---

## Architecture

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Layer violations (domain → infrastructure) | TS2 #7, JV2 #7 | ✅ |
| Circular dependencies | — | ❌ Not testable in single-file samples. Requires multi-file test. |
| God classes/modules (SRP) | TS1 #4, PY1 #8, JV1 #4, GO1 #8, RS1 #11 | ✅ |
| Anemic domain models | TS2 #8, PY2 #8, JV2 #8, GO2 #7, RS2 #5 | ✅ |
| Missing/incorrect abstractions | TS2 #4 (OCP implies missing abstraction) | ✅ (indirect) |
| Tight coupling to frameworks | JV2 #7 (direct HTTP in domain) | ✅ |

## Security

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Missing input validation | TS1 #7, PY1 #9, JV1 #9 | ✅ |
| SQL injection | TS1 #1,#2, PY1 #1,#2,#3, JV1 #1,#2, GO1 #1,#2, RS1 #1,#2 | ✅ |
| Command injection | PY2 #1, JV2 #1, GO2 #1, RS1 #3 | ✅ |
| XSS | TS2 #2 | ✅ |
| Path traversal | TS2 #1, PY2 #2, GO2 #2, RS1 #4 | ✅ |
| Auth/authz gaps | TS2 #3, PY2 #3, JV2 #12, GO2 #3 | ✅ |
| Sensitive data exposure | JV2 #2 (card number logged), GO1 #15 (error details), RS1 #13 | ✅ |
| Insecure defaults | GO1 #21 (no graceful shutdown) | ✅ (indirect) |
| Unsafe deserialization | — | ❌ Not covered. Low priority — less common in these stacks. |

## Performance

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| N+1 query patterns | PY1 #6, GO1 #10, RS1 #9 | ✅ |
| Unbounded queries (no LIMIT) | TS1 #8, PY1 #7, JV1 #8, GO1 #11, RS1 #10 | ✅ |
| Unnecessary allocations in hot paths | RS1 #14, RS2 #10 (clone in loop) | ✅ |
| Blocking calls in async contexts | PY1 #10, RS1 #7 | ✅ |
| Missing caching for expensive ops | — | ❌ Context-dependent, hard to demonstrate in isolation. |
| Inefficient data structures | — | ❌ Requires algorithmic sample. |
| Unnecessary eager loading | — | ❌ Requires ORM relationship sample. |

## Design — SOLID

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| SRP | TS1 #4, PY1 #8, JV1 #4, GO1 #8, RS1 #11 | ✅ |
| OCP | TS2 #4, PY2 #4, JV2 #4, GO2 #4, RS2 #3,#4 | ✅ |
| LSP | TS2 #5, PY2 #6, JV2 #5 | ✅ (Go, Rust excluded — no implementation inheritance) |
| ISP | TS2 #6, PY2 #7, JV2 #6, GO2 #6, RS2 #2 | ✅ |
| DIP | TS1 #5, JV1 #5, TS2 #7, JV2 #7, RS2 #14 | ✅ |

## Design — Functional Programming

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Mutable where immutable works | TS1 #9, PY1 #11, GO1 #9 | ✅ |
| Hidden side effects | TS2 #9, PY2 #9, JV2 #9, GO2 #8, RS2 #7 | ✅ |
| Shared mutable state | TS1 #9, PY1 #11, JV1 #16, GO1 #9, RS2 #9 (Arc<Mutex> overuse) | ✅ |
| Imperative loops where FP clearer | TS1 #10 (forEach → map) | ✅ |
| Missing Result/Option types | RS1 #15 (bool → Result), RS2 #6 (Box<dyn Error> erases type) | ✅ |

## Implementation — Clean Code

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Names not revealing intent | TS2 #15, PY2 #15, JV2 #17, GO2 #16, RS2 #12 | ✅ |
| Functions too long / mixed abstraction | TS2 #18, PY2 #14, JV2 #18, GO2 #15, RS1 #11 | ✅ |
| Magic numbers/strings | TS1 #11, PY1 #12, JV2 #14, RS1 #16 | ✅ |
| Dead code / commented-out code | TS2 #16,#17, PY2 #16, JV2 #16, GO2 #17, RS2 #13 | ✅ |
| Deep nesting (3+ levels) | TS2 #13, PY2 #12, JV2 #13, GO2 #12, RS2 #11 | ✅ |
| Code duplication | TS2 #14, PY2 #13,#17, JV2 #15, GO2 #14,#18 | ✅ |

## Implementation — Testability

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Hard-coded dependencies | TS2 #11,#12, PY2 #10, JV2 #11, GO2 #10, RS2 #8 | ✅ |
| Side effects coupled to logic | TS2 #9, PY2 #9, JV2 #9, GO2 #8, RS2 #7 | ✅ |
| Non-deterministic behavior | TS2 #10, PY2 #11, JV2 #10, GO2 #9, RS2 #8 | ✅ |
| Complex constructors | JV2 (PaymentService constructor with side effect) | ✅ (indirect) |
| Private methods with significant logic | — | ❌ Hard to demonstrate without larger class. Low priority. |

## Style

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| Naming convention inconsistencies | TS1 #14, GO2 #19 | ✅ |
| Minor readability improvements | Various NIT findings across all samples | ✅ |

---

## Rust-Specific Rules

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| `.unwrap()`/`.expect()` in library code | RS1 #5,#6 | ✅ |
| `panic!`/`unimplemented!` in shipped paths | RS1 #6 (unwrap family) | ✅ (related) |
| Blocking call inside `async fn` | RS1 #7 | ✅ |
| Lock/guard held across `.await` | RS1 #8 | ✅ |
| `unsafe` without `// SAFETY:` (and UB) | RS2 #1 | ✅ |
| `Box<dyn Error>` in public lib API | RS2 #6 | ✅ |
| `Arc<Mutex<_>>` overuse | RS2 #9 | ✅ |
| Clone-to-satisfy-borrow-checker | RS1 #14, RS2 #10 | ✅ |
| Stringly-typed where enum fits (OCP) | RS2 #3,#4 | ✅ |
| Newtype / enum over raw String | RS2 #15 | ✅ |
| Swallowed/discarded `Result` | RS1 #12 | ✅ |

---

## Dockerfile-Specific Rules

| Rule | Covered By | Finding # |
|------|-----------|-----------|
| FROM latest / unpinned tag | DF1 #1 | ✅ |
| Mutable tag (no digest) | DF2 #1 | ✅ |
| No USER in final stage (runs as root) | DF1 #4, DF2 #2 | ✅ |
| Secret in ENV/ARG | DF1 #2 | ✅ |
| curl -k / TLS disabled | DF1 #3 | ✅ |
| Unverified artifact download | DF2 #4 | ✅ |
| Single-stage with build tools | DF1 #5 | ✅ |
| Overly broad COPY --from | DF2 #3 | ✅ |
| apt cleanup in separate RUN layer | DF1 #6 | ✅ |
| COPY . . before dependency install | DF1 #7 | ✅ |
| ADD instead of COPY | DF1 #8 | ✅ |
| Missing WORKDIR | DF1 #9 | ✅ |
| Missing HEALTHCHECK | DF1 #10, DF2 #6 | ✅ |
| ARG vs ENV semantics | DF2 #5 | ✅ |
| Unnamed multi-stage | DF2 #7 | ✅ |

---

## Summary

| Category | Rules | Covered | Not Covered |
|----------|-------|---------|-------------|
| Architecture | 6 | 5 | 1 (circular deps) |
| Security | 8 | 7 | 1 (unsafe deserialization) |
| Performance | 7 | 4 | 3 (caching, data structures, eager loading) |
| Design — SOLID | 5 | 5 | 0 |
| Design — FP | 5 | 5 | 0 |
| Clean Code | 6 | 6 | 0 |
| Testability | 5 | 4 | 1 (private methods) |
| Style | 2 | 2 | 0 |
| Rust | 11 | 11 | 0 |
| Dockerfile | 15 | 15 | 0 |
| **Total** | **70** | **64** | **6** |

**Coverage: 91% (64/70)**

Adding Rust closed two previously-uncovered general rules: *unnecessary allocations in hot paths* (clone-in-loop) and *missing Result/Option types* (both core Rust idioms).

### Uncovered Rules — Analysis

| Rule | Why Not Covered | Risk |
|------|----------------|------|
| Circular dependencies | Requires multi-file sample | Low — LLM can recognize this from imports |
| Unsafe deserialization | Rare in TS/Python/Go, Java-specific (ObjectInputStream) | Low |
| Missing caching | Context-dependent | Low — architecture decision |
| Inefficient data structures | Requires algorithmic code | Low |
| Unnecessary eager loading | Requires ORM relationships | Medium — could add to PY1/JV1 |
| Private methods with logic | Requires larger class context | Low |

The 6 uncovered rules are either hard to demonstrate in single-file samples or low-risk items that LLMs handle well without explicit examples.
