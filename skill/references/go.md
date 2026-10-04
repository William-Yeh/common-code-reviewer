# Go Review Rules

These rules supplement the common review framework. Apply them to `.go` files.

## Language-Owned Review Rules

| Rule ID | Severity | Review Rule |
|---|---|---|
| `go/panic-in-library` | BLOCKER | Library code panics on a recoverable condition instead of returning an error. |

## Style Standard

Follow **Effective Go** and **Go Code Review Comments** (the official standards). Additionally:

- Run `gofmt` / `goimports` — formatting is non-negotiable in Go. Do not flag any formatting issue that these tools handle.
- Naming: short, concise names. `i` not `index` for loop vars. `ctx` not `context`. `err` not `error`. Exported names are the API — make them clear — `common/style-naming`.
- Package names: lowercase, single word, no underscores. The package name is part of the call site (`http.Get`, not `httpPackage.Get`) — `common/style-naming`.
- No stutter: `http.HTTPServer` → `http.Server`. Package-qualified names should read naturally — `common/style-naming`.
- Acronyms: `ID`, `URL`, `HTTP` in all caps when exported. `id`, `url`, `http` in lower when unexported — `common/style-naming`.
- Getters: no `Get` prefix. `user.Name()` not `user.GetName()`. Setters use `Set` prefix: `user.SetName()` — `common/style-naming`.
- Interface names: single-method interfaces use `-er` suffix: `Reader`, `Writer`, `Closer`, `Stringer` — `common/style-naming`.
- Comment every exported name. Comments start with the name: `// Server represents an HTTP server.` — `common/style-readability`
- No `init()` unless absolutely necessary — it hides side effects and makes testing harder — `common/hidden-side-effect`.

## Prefer Modern Features

Findings from this table are `common/language-idiom` unless a row's pattern also matches a more specific rule in this reference or the catalog; that rule's ID and severity take precedence. Gate each row on the `go` directive in `go.mod`. Since 1.26, `go fix ./...` applies most of these rewrites automatically (the modernizers, plus `//go:fix inline` directives for API migrations). When several rows fire in one change, recommend running it instead of listing each occurrence.

| Legacy Pattern | Prefer | Since |
|---|---|---|
| Manual error type switching | `errors.Is()` | 1.13 |
| `var target *E; errors.As(err, &target)` | `target, ok := errors.AsType[*E](err)` | 1.26 |
| Temporary variable only to take its address (`v := f(); p := &v`) | `new(f())` | 1.26 |
| `strings.LastIndex` + slicing around a separator | `strings.CutLast` / `bytes.CutLast` | 1.27 |
| Third-party UUID module (`google/uuid`, `gofrs/uuid`) in new code | stdlib `uuid` package | 1.27 |
| `for i := 0; i < n; i++` with `i` used only as a counter | `for i := range n` | 1.22 |
| `x := x` copies of loop variables | delete them (per-iteration loop variables) | 1.22 |
| `math/rand` | `math/rand/v2` | 1.22 |
| Callback-style or hand-rolled iterator APIs | `iter.Seq` / `iter.Seq2`, with `slices.Collect`, `slices.Sorted`, `maps.Keys` | 1.23 |
| `strings.Split` / `strings.Fields` consumed only by a `range` loop | `strings.SplitSeq`, `strings.FieldsSeq`, `strings.Lines` | 1.24 |
| `omitempty` on struct or `time.Time` fields (never omits them) | `omitzero` | 1.24 |
| `runtime.SetFinalizer` | `runtime.AddCleanup` | 1.24 |
| `tools.go` with blank imports to pin tool versions | `tool` directive in `go.mod` (`go get -tool`) | 1.24 |
| `fmt.Sprintf("%s:%d", host, port)` for dial addresses (breaks IPv6) | `net.JoinHostPort` | — |
| `interface{}` | `any` (type alias) | 1.18 |
| Manual sort with `sort.Slice` | `slices.Sort`, `slices.SortFunc` | 1.21 |
| Manual min/max | `min()`, `max()` builtins | 1.21 |
| Manual contains check | `slices.Contains` | 1.21 |
| Type-specific containers | Generics with type parameters | 1.18 |
| `sync.Mutex` for simple atomics | `atomic.Int64`, `atomic.Bool`, etc. | 1.19 |
| `ioutil` package | `io` and `os` equivalents | 1.16 |
| `golang.org/x/exp/maps`, `slices` | `maps`, `slices` stdlib | 1.21 |
| Goroutine leak with bare `go func()` | `errgroup.Group`, or `sync.WaitGroup.Go` for fire-and-wait without error collection | 1.25 |
| Context-less function signatures | Accept `context.Context` as first parameter | 1.7 |
| `log.Println` / `log.Fatalf` | `slog` (structured logging) | 1.21 |
| Global logger | Inject `*slog.Logger` via dependency | 1.21 |

## Type System

- **Prefer small interfaces**: Interfaces with 1-2 methods are idiomatic Go. Flag interfaces with 5+ methods — likely too broad — `common/interface-segregation`.
- **Define interfaces at the consumer, not the provider**: The package that *uses* the interface should define it. Flag interfaces defined next to their only implementation — `common/language-idiom`.
- **Accept interfaces, return structs**: Functions should accept interfaces for flexibility but return concrete types for clarity — `common/language-idiom`.
- **Struct embedding**: Use for composition, not inheritance. Flag embedded types that expose methods the outer type shouldn't have — `common/language-idiom`.
- **Generics**: Use for containers, algorithms, and utility functions. Flag generic code where a concrete type or interface would be simpler — don't over-generalize — `common/language-idiom`. Since 1.27 a method may declare its own type parameters (`func (s *Set[T]) Map[U any](f func(T) U) *Set[U]`); do not flag that as a compile error. Interface methods still cannot declare type parameters, and a generic method cannot satisfy an interface method.
- **Type aliases vs definitions**: `type UserID string` (new type, prevents mixing) vs `type UserID = string` (alias, interchangeable). Flag aliases where a distinct type would provide safety — `common/weak-type-model`.

## Functional Patterns

Go is not a functional language, but these patterns apply:

- Prefer value semantics over pointer semantics when structs are small — reduces aliasing bugs — `common/language-idiom`
- Flag mutation of slice/map parameters without documentation — callers may not expect it — `common/hidden-side-effect`
- Prefer returning new slices/maps over mutating inputs — `common/unnecessary-mutation`
- Use functional options pattern (`func WithTimeout(d time.Duration) Option`) for configurable constructors — `common/language-idiom`
- First-class functions: use function types and closures for strategy patterns, middleware, decorators — `common/language-idiom`
- Flag global mutable state (`var` at package level) — inject dependencies instead — `common/shared-mutable-state`

## Error Handling

Go's explicit error handling is a feature, not a problem. Review it carefully:

- **Never** `_ = someFunc()` that returns an error — `common/ignored-error`, unless explicitly justified
- **Never** bare `if err != nil { return err }` without wrapping context — use `fmt.Errorf("doing X: %w", err)` for wrapped errors — `common/incomplete-error-handling`
- Flag error messages starting with uppercase or ending with punctuation — Go convention is lowercase, no period — `common/language-idiom`
- Flag `panic` in library code on input-derived or recoverable conditions — `go/panic-in-library`. Return an `error` instead. Panics belong in `main`, in `init`, and in `Must*` helpers whose argument is a compile-time constant (`regexp.MustCompile`).
- Flag `log.Fatal` / `os.Exit` in library code — it kills the process. Only allowed in `main` — `go/panic-in-library`.
- Encourage sentinel errors (`var ErrNotFound = errors.New(...)`) for expected failure modes — `common/erased-failure`
- Encourage custom error types implementing `error` for errors carrying structured data — `common/erased-failure`
- Flag `errors.New` in hot paths — pre-allocate as package-level vars — `common/hot-path-allocation`
- Use `errors.Is()` and `errors.AsType[E]()` (1.26+; `errors.As()` before that) for checking — not string comparison or type assertions — `common/language-idiom`

## Standard Library HTTP (`net/http`)

- Use `http.NewServeMux` (1.22+) with method-based routing: `mux.HandleFunc("GET /users/{id}", handler)` — `common/language-idiom`
- Flag `http.DefaultServeMux` in production — it's a global, shared across packages — `common/shared-mutable-state`
- Set timeouts on `http.Server`: `ReadTimeout`, `WriteTimeout`, `IdleTimeout`. Flag zero-value servers — `common/insecure-default` (slowloris risk).
- Flag handlers that don't check `r.Context().Done()` for long-running operations — `common/unmanaged-concurrency`
- Use `http.MaxBytesReader` on request bodies — flag unbounded `io.ReadAll(r.Body)` (DoS risk) — `common/missing-input-validation`
- Middleware: use `func(http.Handler) http.Handler` pattern. Flag middleware that doesn't call `next.ServeHTTP` on its success path — `common/api-misuse`.
- **CSRF**: Since 1.25, `http.CrossOriginProtection` rejects unsafe cross-origin browser requests using Fetch metadata, with no tokens. Flag cookie-authenticated state-changing endpoints with no CSRF protection — `common/insecure-default`. Prefer `CrossOriginProtection` over a hand-rolled token check — `common/language-idiom`.
- **User-supplied paths**: Flag `filepath.Join(base, userPath)` followed by `os.Open` — `common/path-traversal`. Since 1.24, open files through `os.OpenRoot(base)` / `os.Root`, which rejects paths that escape the root, including through symlinks.
- **Reverse proxies**: Flag `httputil.ReverseProxy.Director` — `common/deprecated-api` (deprecated in 1.26: a client can strip headers the `Director` adds by naming them hop-by-hop). Use `Rewrite`.

## Toolchain and Security Deprecations

- Flag `rsa.EncryptPKCS1v15`, `rsa.DecryptPKCS1v15`, and `rsa.DecryptPKCS1v15SessionKey` — `common/deprecated-api` (deprecated in 1.26 as unsafe padding). Use `rsa.EncryptOAEP` / `DecryptOAEP`.
- Flag `godebug` lines in `go.mod` or `//go:debug` comments that pin a removed setting to its old value — `common/deprecated-api`. From 1.27 the `go` command fails the build on them; the removed settings are `asynctimerchan`, `gotypesalias`, `tls10server`, `tls3des`, `tlsrsakex`, `tlsunsafeekm`, and `x509keypairleaf`.

## Gin

- **Context abuse**: `gin.Context` is both request context and response writer. Flag storing `*gin.Context` beyond the handler scope — it's not safe after the handler returns — `common/shared-mutable-state`.
- **Binding and validation**: Use `ShouldBindJSON` (returns error) not `BindJSON` (writes 400 automatically). Let the handler control the error response — `common/incomplete-error-handling`.
- **Middleware**: Flag `c.Next()` misuse. `c.Abort()` should be followed by a return — `common/incomplete-error-handling`.
- **Route grouping**: Group routes by resource/domain. Flag flat route registration with 20+ routes — `common/style-readability`.
- **Error handling**: Use `c.Error()` to collect errors and handle them in middleware, not `c.JSON(500, ...)` scattered in handlers — `common/duplicated-logic`.
- **Avoid global Gin engine**: Flag `gin.Default()` at package level. Create the engine in `main` or a constructor — `common/shared-mutable-state`.

## gRPC

- **Error codes**: Use proper gRPC status codes (`codes.NotFound`, `codes.InvalidArgument`). Flag `codes.Internal` for all errors — be specific — `common/erased-failure`.
- **Interceptors**: Use interceptors for cross-cutting concerns (auth, logging, tracing). Flag auth checks in individual RPC methods — `common/duplicated-logic`.
- **Streaming**: Flag server-side streams that don't check `stream.Context().Err()` — clients may disconnect — `common/unmanaged-concurrency`.
- **Deadlines**: Flag RPC calls without deadline/timeout set on the context — `context.WithTimeout`. Unbounded RPCs can hang forever — `common/missing-timeout`.

## Concurrency

Go concurrency requires careful review:

- **Goroutine lifecycle**: Every `go func()` must have a clear termination path. Flag goroutines without cancellation (context) or done channels — goroutine leak risk, `common/unmanaged-concurrency`.
- **Prefer `errgroup.Group`** over bare goroutine spawning — manages lifecycle, collects errors, propagates cancellation — `common/unmanaged-concurrency`.
- **Channel direction**: Function parameters should specify direction (`chan<- T` or `<-chan T`). Flag bidirectional channels in function signatures — `common/language-idiom`.
- **sync.Once for initialization**: Flag double-checked locking patterns — use `sync.Once` — `common/shared-mutable-state`.
- **Race conditions**: Flag shared state accessed from goroutines without synchronization. Suggest `-race` flag in tests — `common/shared-mutable-state`.
- **Context propagation**: Pass `context.Context` through the call chain. Flag functions that create their own `context.Background()` when a caller could provide one — `common/unmanaged-concurrency`.
- **Select with default**: Flag `select` with `default` in loops without a sleep/backoff — busy loop (CPU burn) — `common/busy-wait`.
- **Leak evidence**: Since 1.27 the `goroutineleak` profile (`runtime/pprof`, `/debug/pprof/goroutineleak`) reports leaked goroutines. When a leak finding is disputed, point to it as the way to confirm.

## Testing

- Table-driven tests: use `[]struct{ name string; ... }` with `t.Run(tc.name, ...)`. Flag repetitive test functions that could be parameterized — `common/duplicated-logic`.
- `t.Helper()`: call in test helper functions for correct error line reporting — `common/language-idiom`.
- `t.Parallel()`: encourage for independent tests. Flag tests that share mutable state — `common/shared-mutable-state`.
- Prefer stdlib `testing` over testify when possible. If using testify, use `assert` (continues) vs `require` (stops) deliberately — `common/language-idiom`.
- `t.Cleanup()` for teardown instead of `defer` — survives subtests — `common/language-idiom`.
- Since 1.24: use `t.Context()` instead of `context.Background()` in tests, `t.Chdir` instead of `os.Chdir`, and `for b.Loop()` instead of `for i := 0; i < b.N; i++` in benchmarks — `common/language-idiom`.
- Flag `time.Sleep` in tests — use channels, tickers, or `testing.T` deadlines for synchronization. For testing concurrent code with virtual time, prefer `testing/synctest` (GA in 1.25) over real sleeps — `common/nondeterministic-dependency`; since 1.27, `synctest.Sleep` combines `time.Sleep` and `synctest.Wait`.
- For HTTP handlers: use `httptest.NewRecorder()` and `httptest.NewRequest()` — `common/language-idiom`.
- Flag tests that depend on network, filesystem, or environment without build tags or skip conditions — `common/nondeterministic-dependency`.

## Common Enterprise Anti-Patterns

- **Interface pollution**: Defining interfaces before there are multiple implementations. Define interfaces at the consumer when you actually need the abstraction — `common/language-idiom`.
- **Package `util` / `common` / `helpers`**: Dumping ground for unrelated functions. Name packages by what they provide, not by how vague they are — `common/god-module`.
- **Premature channels**: Using channels for simple mutex-protected state. Channels are for communication between goroutines, not as a generic synchronization primitive — `common/language-idiom`.
- **Ignoring context**: Functions that accept `context.Context` but don't pass it to downstream calls. Every I/O call should respect context — `common/unmanaged-concurrency`.
- **Over-packaging**: 50 packages for a simple service. Go favors fewer, larger packages over Java-style one-class-per-package — `common/speculative-abstraction`.
- **Error string matching**: `if err.Error() == "not found"` — fragile. Use sentinel errors or `errors.Is` — `common/language-idiom`.
- **Pointer overuse**: Using `*Foo` everywhere "for performance." Value semantics are often faster (less GC pressure) and safer for small structs — `common/language-idiom`.
- **Missing graceful shutdown**: `http.ListenAndServe` without signal handling. Use `signal.NotifyContext` + `server.Shutdown(ctx)` — `common/graceful-shutdown`.

## Change Risk

### Scored Units

`func` declarations and methods. Function literals fold into the enclosing
unit. Interface method sets have no body and are not scored.

### Decision Points

| Category | Go |
|---|---|
| Branch | `if`, `else if` |
| Loop | every `for` form |
| Case arm | each `case` in `switch`, type switch, and `select`; `default` free |
| Exception handler | none |
| Short-circuit operator | `&&`, `\|\|` |
| Conditional expression | none |
| Early-return operator | none |

Not counted: `else`, `defer`, `go`, `goto`, labels. `if err != nil` is an
ordinary branch.

### Test Files

`*_test.go` and anything under `testdata/`.

### Coverage Evidence

`go test -coverprofile=coverage.out ./...` writes a coverprofile. Each line is
`file:startLine.col,endLine.col statements count`; blocks with count 0 inside the
unit's range are uncovered, and cov is covered statements over statements.
`gocover-cobertura` converts it to Cobertura when a team prefers that.

### Oracle Deviations

gocyclo matches this profile exactly. `lizard` scores function literals as
separate anonymous units, so its CC for the enclosing function runs lower on
callback-heavy code.
