# Rust Review Rules

These rules supplement the common review framework. Apply them to `.rs` files.

## Style Standard

Follow the **Rust API Guidelines** and **Rust Style Guide** (the official standards). Additionally:

- Run `rustfmt` and `clippy` — formatting and most lints are non-negotiable. Do not flag any formatting issue or basic lint that these tools handle (e.g. `cargo clippy -- -D warnings`).
- Naming: `snake_case` for functions, variables, modules, and crates; `CamelCase` for types, traits, and enum variants; `SCREAMING_SNAKE_CASE` for constants and statics. Flag deviations.
- Acronyms are treated as one word: `Uuid`, `HttpClient`, `parse_id` — not `UUID`, `HTTPClient`, `parseID`.
- Conversions: `as_*` (borrow → borrow, cheap), `to_*` (borrow → owned, expensive), `into_*` (owned → owned, consuming). Flag a `to_*` method that is actually cheap, or `into_*` that doesn't consume `self`.
- Getters: no `get_` prefix for the common case — `user.name()` not `user.get_name()`. `get_` is reserved for the `Index`-like fallible accessor convention.
- Document every public item with `///` doc comments; document the crate/module with `//!`. Flag missing docs on `pub` items in a library crate.
- Prefer `#[non_exhaustive]` on public enums/structs that may grow — flag public enums likely to gain variants without it (forces downstream `_ =>` arms, easing SemVer evolution).

## Prefer Modern / Idiomatic Features

| Legacy / Non-idiomatic | Prefer | Notes |
|---|---|---|
| `match opt { Some(x) => x, None => return ... }` | `let Some(x) = opt else { return ... };` | let-else (1.65+) |
| `if let Some(x) = opt { ... } else { ... }` for binding-or-default | `let x = opt.unwrap_or(default);` / `unwrap_or_else` | clearer intent |
| Manual `impl` of `From`/`Display` for errors | `thiserror` derive (libraries) | less boilerplate |
| Stringly-typed errors / `Box<dyn Error>` everywhere | `anyhow::Result` (apps) / typed enums (libs) | see Error Handling |
| `vec.iter().map(...).collect::<Vec<_>>()` then loop | chain iterator adaptors, `collect` once | avoid intermediate allocations |
| `.clone()` to satisfy the borrow checker | borrow, restructure, or `Rc`/`Arc` deliberately | see Ownership |
| `lazy_static!` | `std::sync::LazyLock` / `OnceLock` (1.80+) | stdlib, no macro crate |
| `mem::replace(&mut x, Default::default())` | `mem::take(&mut x)` | clearer |
| Manual `Future` polling | `async`/`.await` | unless writing a runtime primitive |
| `extern crate` declarations | edition 2018+ implicit imports | remove |

## Type System & Ownership

Rust's type system encodes invariants — review whether the change *uses* it or *fights* it:

- **Make illegal states unrepresentable**: prefer enums over a struct with several `Option` fields and "only one is set" invariants. Flag `bool` flags or sentinel values where a 2–3 variant enum would be self-documenting and exhaustively checked.
- **Newtypes for domain values**: flag raw `String`/`u64` passed where mixing units/IDs is possible (`UserId`, `Cents`). A `struct UserId(u64)` prevents accidental argument swaps the compiler can't otherwise catch.
- **Borrow, don't own, in function signatures**: accept `&str` not `String`, `&[T]` not `Vec<T>`, `&T` not `T` when you only read. Flag owned parameters that force callers into needless clones/allocations.
- **`impl Trait` vs generics vs `dyn`**: `impl Trait` in argument position for simple cases; named generic `<T: Trait>` when the type is referenced more than once; `Box<dyn Trait>` only when you genuinely need heterogeneous types or dynamic dispatch. Flag `dyn` used purely to avoid writing a generic — it costs a vtable indirection.
- **`.clone()` as a borrow-checker escape hatch**: flag clones that exist only to sidestep a borrow error, especially in hot paths or on large owned types. Ask whether a borrow, a restructure, or `Rc`/`Arc` is the right tool. A `.clone()` of a `String` in a loop is a MINOR smell; cloning a large `Vec`/struct per iteration is MAJOR.
- **`Rc`/`Arc` + `RefCell`/`Mutex`**: this combination re-introduces shared mutability that the borrow checker normally prevents. Flag it when a simpler ownership model (single owner + borrows, or passing `&mut`) would work — it moves aliasing bugs and borrow violations from compile time to runtime (`RefCell` panics).
- **Lifetimes in public APIs**: flag gratuitous explicit lifetimes that elision would cover, and flag returning references tied to local data (won't compile, but the *design* of returning a borrow vs an owned value is worth a comment).

## Error Handling

Rust models errors as values — review them as carefully as Go's:

- **`.unwrap()` / `.expect()` in library code**: BLOCKER on any input-derived or fallible value — it panics the caller's process. Acceptable only for invariants that are *provably* infallible (and then `.expect("reason")` documenting why). Tests and `main`/prototypes are exempt.
- **`panic!` / `unreachable!` / `todo!` / `unimplemented!` in shipped library paths**: BLOCKER. Return a `Result` instead. `unreachable!` is acceptable only when the compiler can't see exhaustiveness but you can prove it.
- **`?` over manual matching**: prefer `?` for propagation. Flag verbose `match`/`if let` that only forwards the error — but ensure the error type implements `From` for the conversion, or use `.map_err(...)`.
- **Library vs application error strategy**: libraries should expose **typed** errors (an enum, ideally via `thiserror`) so callers can match on variants — flag a public API returning `anyhow::Error` or `Box<dyn Error>`, which erases the variant. Applications/binaries may use `anyhow`/`eyre` for convenience.
- **Don't swallow errors**: flag `let _ = fallible();` and `if let Ok(x) = ... {}` with no `else` that silently drops the error — equivalent to an empty catch block. Also flag `.ok()` used purely to discard an error without intent.
- **Error context**: flag bare propagation that loses context. Encourage `.with_context(|| ...)` (anyhow) or a wrapping variant so logs show *what operation* failed, not just the leaf cause.
- **`Result` must be used**: `Result` is `#[must_use]`, but flag any deliberate ignoring. Never `unwrap()` a `Result` whose `Err` carries information you discard.

## Unsafe

`unsafe` opts out of the compiler's guarantees — review it like security-critical code:

- **Every `unsafe` block needs a `// SAFETY:` comment** stating the invariants the caller/author guarantees. Flag missing SAFETY comments — MAJOR.
- **Justify the `unsafe`**: flag `unsafe` used for performance without a benchmark, or where a safe abstraction (`split_at_mut`, `slice::windows`, `Vec::with_capacity`) exists. Most application code should have zero `unsafe`.
- **`unsafe fn` must document preconditions** in a `# Safety` doc section. Flag public `unsafe fn` without it.
- **Raw pointers, `transmute`, `mem::uninitialized`/`MaybeUninit`, FFI**: scrutinize for UB — aliasing `&mut`, dangling pointers, invalid bit patterns, alignment, and uninitialized reads. Any potential UB is a BLOCKER.
- **`unwrap` inside `unsafe`** that panics across an FFI boundary is undefined behavior — BLOCKER.

## Functional & Iterator Patterns

- Prefer iterator chains (`.iter().filter().map().collect()`) over manual index loops — clearer and bounds-check-friendlier. But flag chains so long they obscure intent; extract named steps.
- Flag `.collect::<Vec<_>>()` immediately followed by another iteration — fuse the chain and `collect` once, or don't collect at all.
- Prefer `.unwrap_or`, `.unwrap_or_else`, `.map`, `.and_then`, `.ok_or` on `Option`/`Result` over manual `match` when it reads clearer.
- Flag `for` loops that merely accumulate — `sum()`, `product()`, `fold()`, `collect()` express intent and avoid mutable accumulators.
- Prefer immutability: a binding without `mut` is the default. Flag `let mut` that is never mutated (clippy catches this) and, more importantly, mutation-heavy code where a transformation pipeline would be clearer and alias-free.
- Closures capturing by `move` unnecessarily — flag `move` that forces clones when a borrow would do.

## Concurrency & Async

- **`Send`/`Sync` are the compiler's race guards** — but review what crosses threads. Flag `Arc<Mutex<T>>` protecting a large critical section, or a `Mutex` held across an `.await` point (deadlock / blocks the executor) — MAJOR/BLOCKER.
- **Blocking in async**: flag synchronous blocking calls (`std::fs`, `std::thread::sleep`, blocking DB drivers, heavy CPU work) inside an `async fn` — it stalls the runtime's worker thread. Use the async equivalent or `tokio::task::spawn_blocking`. BLOCKER in a server hot path.
- **`.await` holding a lock or `RefCell` borrow**: flag — the guard lives across the suspension point.
- **Spawned task lifecycle**: flag `tokio::spawn` whose `JoinHandle` is dropped with no supervision or cancellation path — detached tasks leak and swallow panics. Mirror Go's goroutine-leak rule.
- **`std::sync::Mutex` vs `tokio::sync::Mutex`**: in async code, use the async mutex only when the guard must cross `.await`; otherwise the std mutex is cheaper. Flag the wrong choice.
- **Channels**: prefer the right primitive (`mpsc`, `oneshot`, `broadcast`). Flag a busy-loop polling a `try_recv()` without backoff.
- **`unwrap()` in spawned threads/tasks**: panics there are isolated and silently lost — flag as a swallowed failure.

## Testing

- Unit tests live in a `#[cfg(test)] mod tests` block in the same file; integration tests in `tests/`. Flag tests that exercise private internals from `tests/` (they can't see them) or heavy logic with no `#[cfg(test)]` coverage.
- Prefer `assert_eq!`/`assert!` with informative messages. Flag `assert!(a == b)` where `assert_eq!` gives a better diff.
- Use `#[should_panic(expected = "...")]` with the `expected` substring — flag bare `#[should_panic]` that could mask the wrong panic.
- Flag `.unwrap()` chains in tests that obscure *which* step failed — acceptable but `.expect("...")` aids debugging.
- Encourage property-based tests (`proptest`/`quickcheck`) for pure functions with broad input domains; flag exhaustive hand-written cases where a property would be stronger.
- Flag tests depending on wall-clock time, filesystem, or network without isolation. Inject a clock or use a tempdir.
- For async tests use `#[tokio::test]` (or the runtime's macro) — flag `block_on` scattered in test bodies.

## Common Anti-Patterns

- **`.unwrap()` culture**: pervasive `.unwrap()` outside tests/prototypes — each is a latent panic. The most common Rust review finding.
- **Clone-to-compile**: sprinkling `.clone()` until the borrow checker is satisfied, instead of fixing ownership. Hides design problems and allocates.
- **`Arc<Mutex<_>>` as a default**: reaching for shared mutability before considering message passing or single-ownership designs.
- **Stringly-typed APIs**: `fn handle(action: &str)` with a match on string literals — use an enum; the compiler then enforces exhaustiveness (mirrors the OCP/switch anti-pattern).
- **`Box<dyn Error>` in library public APIs**: erases error types so callers can't match — return a typed enum.
- **`unsafe` for micro-optimization** without a benchmark proving the safe version is the bottleneck.
- **Over-use of generics**: deeply generic signatures (`fn f<T, U, V, W>(...)` with many bounds) where two concrete types or a `dyn` trait object would read far better and compile faster.
- **`pub` everything**: leaking internals as `pub` instead of `pub(crate)`/private — every `pub` item is part of your SemVer contract.
- **Ignoring `#[must_use]`**: discarding a `Result` or a builder's returned value.
- **Index-based loops over `.iter()`**: `for i in 0..v.len() { v[i] }` reintroduces bounds checks and panics the borrow checker would prevent.
