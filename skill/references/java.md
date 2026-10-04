# Java Review Rules

These rules supplement the common review framework. Apply them to `.java` files.

Target the current LTS — **Java 25** (GA September 2025) — when recommending modern features. Java 21 remains a widely-deployed LTS; gate suggestions on the project's actual toolchain version rather than assuming the latest. Java 26 and 27 are non-LTS releases; the next LTS is Java 29 (planned September 2027).

Never recommend a preview or incubator feature (anything that needs `--enable-preview` or an `incubator` module). As of Java 27 these include primitive patterns in `switch`/`instanceof`, structured concurrency, lazy constants (formerly `StableValue`), PEM encodings, and the Vector API.

## Style Standard

Follow the **Google Java Style Guide** as the baseline:

- 2-space or 4-space indentation (respect project config). Google uses 2, many enterprises use 4.
- Braces on same line (K&R style). No single-statement blocks without braces — `common/style-readability`.
- Column limit: 100 (Google) or 120. Respect project config.
- Static imports grouped separately, after all non-static imports. Wildcard imports (`*`) discouraged — `common/style-readability`.
- Javadoc on all public API members. `@param`, `@return`, `@throws` for non-trivial methods — `common/style-readability`.
- `@Override` on every overriding method — flag missing annotation — `common/language-idiom`.
- Constants: `UPPER_SNAKE_CASE`. Everything else: `camelCase` / `PascalCase` per Java convention — `common/style-naming`.
- Annotations on their own line before the annotated element, not inline.

Do not flag formatting issues that Checkstyle / Spotless / google-java-format would auto-fix.

## Prefer Modern Features

Findings from this table are `common/language-idiom` unless a row's pattern also matches a more specific rule in this reference or the catalog; that rule's ID and severity take precedence.

| Legacy Pattern | Prefer | Since |
|---|---|---|
| Verbose data classes (getters, setters, equals, hashCode, toString) | `record` | 17 |
| `instanceof` + manual cast | Pattern matching `instanceof` | 16 |
| Long `if/else if` chains on type | `switch` with pattern matching | 21 |
| `ThreadLocal` for request-scoped context | Scoped Values (`ScopedValue`) | 25 |
| Boilerplate validation/`this(...)` before constructor body | Flexible constructor bodies (statements before `super()`/`this()`) | 25 |
| Extensive class hierarchies for variants | `sealed` classes/interfaces | 17 |
| `Optional.get()` without check | `orElse`, `orElseThrow`, `map`, `ifPresent` | 8 |
| `Collections.unmodifiableList(new ArrayList<>(...))` | `List.of()`, `Map.of()`, `Set.of()` | 9 |
| Anonymous inner classes (single method) | Lambda expressions | 8 |
| External iteration (`for` loop) | Stream API or enhanced for-each | 8 |
| `Thread` / `ExecutorService` for concurrent tasks | Virtual threads (`Thread.ofVirtual()`) | 21 |
| String concatenation in loops | `StringBuilder` or `String.join()` or `"""` text blocks | 15 |
| `SimpleDateFormat` | `java.time` API (`LocalDate`, `Instant`, `DateTimeFormatter`) | 8 |
| Checked exceptions for domain errors | Custom unchecked exceptions or Result types | — |
| `null` as return value for "not found" | `Optional<T>` | 8 |
| Raw types (`List` without generics) | Parameterized types (`List<String>`) | 5 |

## Type System

- **Flag raw types**: `List`, `Map` without type parameters — `common/weak-type-model`.
- **Flag unchecked casts**: `(List<String>) obj` without prior type check. Use pattern matching instanceof — `common/weak-type-model`.
- **Encourage sealed interfaces**: For domain types with known subtypes — enables exhaustive switch — `common/language-idiom`.
- **Records for DTOs**: If a class is just data (getters, equals, hashCode), it should be a `record`. Flag manual implementations of what a record gives free — `common/language-idiom`.
- **Var for local variables**: Encourage `var` when the right-hand side makes the type obvious. Flag `var` when it obscures the type — `common/style-readability`.
- **Generics**: Flag method signatures with more than 2 wildcards (`? extends`, `? super`) — likely too complex. Consider a named type parameter — `common/style-readability`.

## Functional Patterns

- Prefer Stream API for collection transformations — `filter`, `map`, `flatMap`, `collect` — `common/imperative-transformation`
- Flag streams that mutate external state — streams should be pure pipelines — `common/unnecessary-mutation`
- Prefer method references (`String::toLowerCase`) over trivial lambdas (`s -> s.toLowerCase()`) — `common/language-idiom`
- Flag `Optional` used as a field type or method parameter — `Optional` is for return values only — `common/language-idiom`
- Flag `Optional.get()` without `isPresent()` check — use `orElseThrow()` or `map`/`flatMap` chains — `common/incomplete-error-handling`
- Encourage `Collectors.toUnmodifiableList()` or `Stream.toList()` (16+) over `Collectors.toList()` — `common/language-idiom`
- Flag nested streams (stream inside a stream's `map`) — usually indicates a need for `flatMap` or extracting a method — `common/style-readability`

## Error Handling

- **Never** empty catch block — `common/ignored-error`. At minimum, log and rethrow or explain why ignored.
- Flag `catch (Exception e)` / `catch (Throwable t)` at fine-grained level — catch specific types — `common/incomplete-error-handling`.
- Flag `throws Exception` on method signatures — be specific about what can fail — `common/erased-failure`.
- Encourage domain-specific exception hierarchy: `DomainException` → `OrderNotFoundException`, etc — `common/erased-failure`.
- Flag checked exceptions used for business logic flow — prefer unchecked exceptions or result types — `common/language-idiom`.
- Use try-with-resources for all `AutoCloseable` — flag manual `finally` blocks for resource cleanup — `common/language-idiom`.
- Flag `e.printStackTrace()` — use a logging framework (SLF4J + Logback/Log4j2) — `common/incomplete-error-handling`.

## Spring Boot

- **Constructor injection only**: Flag `@Autowired` on fields — use constructor injection (preferably with Lombok `@RequiredArgsConstructor` or manual constructor). Field injection hides dependencies and breaks testability — `common/hard-coded-dependency`.
- **Layer discipline**: Controller → Service → Repository. Flag controllers calling repositories directly. Flag services importing Spring Web types (`HttpServletRequest`, `ResponseEntity`) — `common/layer-violation`.
- **DTO ↔ Entity separation**: Flag JPA entities exposed in API responses/requests. Use DTOs (records) at the API boundary — `common/framework-coupling`.
- **Validation**: Use `@Valid` / `@Validated` on request DTOs with Bean Validation annotations. Flag manual validation in controllers for common rules — `common/language-idiom`.
- **Exception handling**: Use `@ControllerAdvice` / `@RestControllerAdvice` with `@ExceptionHandler`. Flag try/catch in individual controllers for error-to-response mapping — `common/duplicated-logic`.
- **Profiles and configuration**: Flag hardcoded URLs and feature flags — `common/magic-literal` — and hardcoded credentials — `common/sensitive-data-exposure`. Use `@Value` / `@ConfigurationProperties` with profiles.
- **Transaction management**: `@Transactional` on service methods, not repositories or controllers. Flag `@Transactional` on read-only queries without `readOnly = true` — `common/language-idiom`.
- **Avoid `@Component` scanning abuse**: Flag `@Service` / `@Component` on classes that should be explicitly configured as `@Bean` (e.g., third-party wrappers, conditional beans) — `common/language-idiom`.
- **Security**: Flag endpoints missing `@PreAuthorize` or Spring Security config — `common/authorization-gap`. Flag disabled CSRF without justification — `common/insecure-default`.
- **Spring Boot 4 / Framework 7** (when the build declares Boot 4.x):
  - Boot 4 defaults to Jackson 3 (`tools.jackson` packages, `@JacksonComponent`). Flag new `com.fasterxml.jackson.databind` or `@JsonComponent` usage — `common/deprecated-api`. (`com.fasterxml.jackson.annotation` is unchanged in Jackson 3; do not flag it.)
  - Retry and concurrency limiting are in the core framework (`@Retryable`, `@ConcurrencyLimit`, enabled by `@EnableResilientMethods`). Flag a new `spring-retry` dependency or a hand-rolled retry loop — `common/language-idiom`.
  - Null-safety annotations moved to JSpecify. Flag new `org.springframework.lang.Nullable` / `NonNull` — `common/deprecated-api`; prefer `org.jspecify.annotations`.

## Quarkus

- **CDI over Spring DI**: Use `@Inject`, `@ApplicationScoped`, `@RequestScoped`. Flag Spring-specific annotations in Quarkus code — `common/language-idiom`.
- **Quarkus REST** (`quarkus-rest`, named RESTEasy Reactive before 3.9): the method signature picks the thread. Endpoints returning `Uni<T>` / `Multi<T>` run on the I/O event loop; endpoints returning plain types run on a worker thread. Flag blocking calls inside `Uni`/`Multi`-returning endpoints that lack `@Blocking` — `common/blocking-in-async`. Do not flag missing `@Blocking` on plain-return endpoints.
- **Panache**: Prefer Active Record or Repository pattern via Panache over raw JPA `EntityManager` for standard CRUD — `common/language-idiom`.
- **Configuration**: Use `@ConfigProperty` or MicroProfile Config. Flag hardcoded values — `common/magic-literal`.
- **Dev Services**: Leverage Quarkus Dev Services for tests. Flag manual container setup in tests when Dev Services would work — `common/language-idiom`.

## Testing

- Use JUnit Jupiter (`@Test` from `org.junit.jupiter`, JUnit 5 or 6). Flag JUnit 4 (`org.junit.Test`) in new code — `common/deprecated-api` on JUnit 6, which deprecates the Vintage engine that runs JUnit 4 tests.
- Prefer AssertJ (`assertThat`) over JUnit assertions — more readable, better error messages — `common/language-idiom`.
- `@Nested` classes for grouping related tests (replaces descriptive naming conventions).
- Flag `@SpringBootTest` when a `@WebMvcTest` or `@DataJpaTest` slice would suffice — startup cost — `common/language-idiom`.
- Use `@MockitoBean` / `@MockitoSpyBean` (Spring Framework 6.2+) or Mockito `@Mock` + `@InjectMocks`. Flag `@MockBean` / `@SpyBean` — `common/deprecated-api` (deprecated in Boot 3.4, removed in Boot 4.0; replace with `@MockitoBean` / `@MockitoSpyBean`). Flag mock setup that reaches 3+ levels deep — indicates the code under test has too many dependencies — `common/complex-construction`.
- On Boot 4, `@SpringBootTest` no longer provides `MockMvc` or `TestRestTemplate` beans. Flag injecting them without `@AutoConfigureMockMvc` / `@AutoConfigureTestRestTemplate` — `common/deprecated-api`.
- Flag tests without assertions — `common/assertion-free-test`. A test whose only check is "no exception thrown" should say so with `assertDoesNotThrow`.
- Parameterized tests (`@ParameterizedTest` + `@CsvSource` / `@MethodSource`) for data-driven tests — `common/duplicated-logic`.
- For Quarkus: use `@QuarkusTest` for integration, `@QuarkusTestResource` for external dependencies.

## Common Enterprise Anti-Patterns

- **God service**: `XxxService` with 20+ methods. Split by use case or aggregate — `common/god-module`.
- **Anemic domain model**: Entities are pure data bags, all logic in services. Move behavior to domain objects where it belongs — `common/anemic-domain`.
- **Overuse of `@Transactional`**: Every method annotated — transactions should be at the use-case level, not per-method — `common/language-idiom`.
- **Stringly-typed code**: Using `String` for IDs, statuses, currency codes. Use `record`-wrapped primitives or enums — `common/weak-type-model`.
- **`Util` / `Helper` classes**: Static method dumping grounds. Refactor into domain-specific methods or extension services — `common/god-module`.
- **Lombok abuse**: `@Data` on JPA entities (breaks equals/hashCode with lazy-loaded fields). Use `@Getter` + `@Setter` + explicit `@EqualsAndHashCode` excluding lazy fields, or use records for DTOs. — `common/api-misuse`
- **Over-abstraction**: `AbstractBaseService<T>` with a single implementation — YAGNI. Create abstractions when the second use case arrives — `common/speculative-abstraction`.
- **Ignoring `java.time`**: Using `Date`, `Calendar`, `Timestamp` in new code. Always use `java.time` types — `common/language-idiom`.
- **Reflective writes to `final` fields**: `Field.setAccessible(true)` followed by `set` on a `final` field warns since Java 26 (JEP 500) and will be denied in a future release. Flag it, and flag `--enable-final-field-mutation` added only to silence the warning — `common/deprecated-api`. Prefer constructor injection or a redesign.
- **`synchronized` and virtual threads**: Since Java 24 (JEP 491), `synchronized` no longer pins the carrier thread. Do not recommend replacing `synchronized` with `ReentrantLock` solely for virtual-thread friendliness.
- **Mutable `ThreadLocal` for context**: On Java 25+, prefer immutable `ScopedValue` for request/task-scoped context — it has clearer lifetime semantics and works cleanly with virtual threads and structured concurrency. Flag `ThreadLocal` set-and-forget that risks leaking across pooled threads — `common/shared-mutable-state`.

## Change Risk

### Scored Units

Methods and constructors, including static methods, default interface methods,
and methods of named nested or inner classes. Lambdas and anonymous-class method
bodies fold into the enclosing unit. Not scored, having no body: abstract
methods, interface signatures, `native` methods.

### Decision Points

| Category | Java |
|---|---|
| Branch | `if`, `else if` |
| Loop | `for`, enhanced `for`, `while`, `do` |
| Case arm | each `case` label or arrow arm in switch statements and expressions; `default` free |
| Exception handler | each `catch` |
| Short-circuit operator | `&&`, `\|\|` |
| Conditional expression | `?:` |
| Early-return operator | none |

Not counted: `else`, `finally`, `throw`, try-with-resources.

### Test Files

Anything under `src/test/`, plus `*Test.java`, `*Tests.java`, `*IT.java`.

### Coverage Evidence

JaCoCo XML: Maven writes `target/site/jacoco/jacoco.xml`, Gradle writes
`build/reports/jacoco/test/jacocoTestReport.xml`. Each `<method>` carries `LINE`
and `COMPLEXITY` counters; cov is `LINE covered / (missed + covered)`, and
`COMPLEXITY missed + covered` is a bytecode CC usable as a cross-check.

### Oracle Deviations

`lizard` and PMD `CyclomaticComplexity` match this profile. JaCoCo reports each
lambda as a separate synthetic `lambda$` method, so its CC for the enclosing
method runs lower.
