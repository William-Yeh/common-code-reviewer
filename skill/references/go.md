# Go Review Rules

These rules supplement the common review framework. Apply them to `.go` files.

## Style Standard

Follow **Effective Go** and **Go Code Review Comments** (the official standards). Additionally:

- Run `gofmt` / `goimports` — formatting is non-negotiable in Go. Do not flag any formatting issue that these tools handle.
- Naming: short, concise names. `i` not `index` for loop vars. `ctx` not `context`. `err` not `error`. Exported names are the API — make them clear.
- Package names: lowercase, single word, no underscores. The package name is part of the call site (`http.Get`, not `httpPackage.Get`).
- No stutter: `http.HTTPServer` → `http.Server`. Package-qualified names should read naturally.
- Acronyms: `ID`, `URL`, `HTTP` in all caps when exported. `id`, `url`, `http` in lower when unexported.
- Getters: no `Get` prefix. `user.Name()` not `user.GetName()`. Setters use `Set` prefix: `user.SetName()`.
- Interface names: single-method interfaces use `-er` suffix: `Reader`, `Writer`, `Closer`, `Stringer`.
- Comment every exported name. Comments start with the name: `// Server represents an HTTP server.`
- No `init()` unless absolutely necessary — it hides side effects and makes testing harder.

## Prefer Modern Features

| Legacy Pattern | Prefer | Since |
|---|---|---|
| Manual error type switching | `errors.Is()`, `errors.As()` | 1.13 |
| `interface{}` | `any` (type alias) | 1.18 |
| Manual sort with `sort.Slice` | `slices.Sort`, `slices.SortFunc` | 1.21 |
| Manual min/max | `min()`, `max()` builtins | 1.21 |
| Manual contains check | `slices.Contains` | 1.21 |
| Type-specific containers | Generics with type parameters | 1.18 |
| `sync.Mutex` for simple atomics | `atomic.Int64`, `atomic.Bool`, etc. | 1.19 |
| `ioutil` package | `io` and `os` equivalents | 1.16 |
| `golang.org/x/exp/maps`, `slices` | `maps`, `slices` stdlib | 1.21 |
| Goroutine leak with bare `go func()` | `errgroup.Group` for managed goroutine lifecycle | — |
| Context-less function signatures | Accept `context.Context` as first parameter | 1.7 |
| `log.Println` / `log.Fatalf` | `slog` (structured logging) | 1.21 |
| Global logger | Inject `*slog.Logger` via dependency | 1.21 |

## Type System

- **Prefer small interfaces**: Interfaces with 1-2 methods are idiomatic Go. Flag interfaces with 5+ methods — likely too broad.
- **Define interfaces at the consumer, not the provider**: The package that *uses* the interface should define it. Flag interfaces defined next to their only implementation.
- **Accept interfaces, return structs**: Functions should accept interfaces for flexibility but return concrete types for clarity.
- **Struct embedding**: Use for composition, not inheritance. Flag embedded types that expose methods the outer type shouldn't have.
- **Generics**: Use for containers, algorithms, and utility functions. Flag generic code where a concrete type or interface would be simpler — don't over-generalize.
- **Type aliases vs definitions**: `type UserID string` (new type, prevents mixing) vs `type UserID = string` (alias, interchangeable). Flag aliases where a distinct type would provide safety.

## Functional Patterns

Go is not a functional language, but these patterns apply:

- Prefer value semantics over pointer semantics when structs are small — reduces aliasing bugs
- Flag mutation of slice/map parameters without documentation — callers may not expect it
- Prefer returning new slices/maps over mutating inputs
- Use functional options pattern (`func WithTimeout(d time.Duration) Option`) for configurable constructors
- First-class functions: use function types and closures for strategy patterns, middleware, decorators
- Flag global mutable state (`var` at package level) — inject dependencies instead

## Error Handling

Go's explicit error handling is a feature, not a problem. Review it carefully:

- **Never** `_ = someFunc()` that returns an error — BLOCKER unless explicitly justified
- **Never** bare `if err != nil { return err }` without wrapping context — use `fmt.Errorf("doing X: %w", err)` for wrapped errors
- Flag error messages starting with uppercase or ending with punctuation — Go convention is lowercase, no period
- Flag `panic` in library code — BLOCKER. Panics are for truly unrecoverable situations in `main` or `init`.
- Flag `log.Fatal` / `os.Exit` in library code — it kills the process. Only allowed in `main`.
- Encourage sentinel errors (`var ErrNotFound = errors.New(...)`) for expected failure modes
- Encourage custom error types implementing `error` for errors carrying structured data
- Flag `errors.New` in hot paths — pre-allocate as package-level vars
- Use `errors.Is()` and `errors.As()` for checking — not string comparison or type assertions

## Standard Library HTTP (`net/http`)

- Use `http.NewServeMux` (1.22+) with method-based routing: `mux.HandleFunc("GET /users/{id}", handler)`
- Flag `http.DefaultServeMux` in production — it's a global, shared across packages
- Set timeouts on `http.Server`: `ReadTimeout`, `WriteTimeout`, `IdleTimeout`. Flag zero-value servers — MAJOR (slowloris risk).
- Flag handlers that don't check `r.Context().Done()` for long-running operations
- Use `http.MaxBytesReader` on request bodies — flag unbounded `io.ReadAll(r.Body)` (DoS risk)
- Middleware: use `func(http.Handler) http.Handler` pattern. Flag middleware that doesn't call `next.ServeHTTP`.

## Gin

- **Context abuse**: `gin.Context` is both request context and response writer. Flag storing `*gin.Context` beyond the handler scope — it's not safe after the handler returns.
- **Binding and validation**: Use `ShouldBindJSON` (returns error) not `BindJSON` (writes 400 automatically). Let the handler control the error response.
- **Middleware**: Flag `c.Next()` misuse. `c.Abort()` should be followed by a return.
- **Route grouping**: Group routes by resource/domain. Flag flat route registration with 20+ routes.
- **Error handling**: Use `c.Error()` to collect errors and handle them in middleware, not `c.JSON(500, ...)` scattered in handlers.
- **Avoid global Gin engine**: Flag `gin.Default()` at package level. Create the engine in `main` or a constructor.

## gRPC

- **Proto design**: Flag overly large messages (50+ fields). Use composition with nested messages.
- **Error codes**: Use proper gRPC status codes (`codes.NotFound`, `codes.InvalidArgument`). Flag `codes.Internal` for all errors — be specific.
- **Interceptors**: Use interceptors for cross-cutting concerns (auth, logging, tracing). Flag auth checks in individual RPC methods.
- **Streaming**: Flag server-side streams that don't check `stream.Context().Err()` — clients may disconnect.
- **Deadlines**: Flag RPC calls without deadline/timeout set on the context — `context.WithTimeout`. Unbounded RPCs can hang forever.
- **Proto backwards compatibility**: Flag removal or renumbering of fields in `.proto` files — BLOCKER. Use `reserved` for removed fields.

## Concurrency

Go concurrency requires careful review:

- **Goroutine lifecycle**: Every `go func()` must have a clear termination path. Flag goroutines without cancellation (context) or done channels — goroutine leak risk (BLOCKER).
- **Prefer `errgroup.Group`** over bare goroutine spawning — manages lifecycle, collects errors, propagates cancellation.
- **Channel direction**: Function parameters should specify direction (`chan<- T` or `<-chan T`). Flag bidirectional channels in function signatures.
- **Mutex scope**: Keep critical sections small. Flag mutexes protecting entire function bodies — rethink the design.
- **sync.Once for initialization**: Flag double-checked locking patterns — use `sync.Once`.
- **Race conditions**: Flag shared state accessed from goroutines without synchronization. Suggest `-race` flag in tests.
- **Context propagation**: Pass `context.Context` through the call chain. Flag functions that create their own `context.Background()` when a caller could provide one.
- **Select with default**: Flag `select` with `default` in loops without a sleep/backoff — busy loop (CPU burn).

## Testing

- Table-driven tests: use `[]struct{ name string; ... }` with `t.Run(tc.name, ...)`. Flag repetitive test functions that could be parameterized.
- `t.Helper()`: call in test helper functions for correct error line reporting.
- `t.Parallel()`: encourage for independent tests. Flag tests that share mutable state.
- Prefer stdlib `testing` over testify when possible. If using testify, use `assert` (continues) vs `require` (stops) deliberately.
- `t.Cleanup()` for teardown instead of `defer` — survives subtests.
- Flag `time.Sleep` in tests — use channels, tickers, or `testing.T` deadlines for synchronization.
- For HTTP handlers: use `httptest.NewRecorder()` and `httptest.NewRequest()`.
- Flag tests that depend on network, filesystem, or environment without build tags or skip conditions.

## Common Enterprise Anti-Patterns

- **Interface pollution**: Defining interfaces before there are multiple implementations. Define interfaces at the consumer when you actually need the abstraction.
- **Package `util` / `common` / `helpers`**: Dumping ground for unrelated functions. Name packages by what they provide, not by how vague they are.
- **Premature channels**: Using channels for simple mutex-protected state. Channels are for communication between goroutines, not as a generic synchronization primitive.
- **Ignoring context**: Functions that accept `context.Context` but don't pass it to downstream calls. Every I/O call should respect context.
- **Over-packaging**: 50 packages for a simple service. Go favors fewer, larger packages over Java-style one-class-per-package.
- **Error string matching**: `if err.Error() == "not found"` — fragile. Use sentinel errors or `errors.Is`.
- **Pointer overuse**: Using `*Foo` everywhere "for performance." Value semantics are often faster (less GC pressure) and safer for small structs.
- **Missing graceful shutdown**: `http.ListenAndServe` without signal handling. Use `signal.NotifyContext` + `server.Shutdown(ctx)`.
