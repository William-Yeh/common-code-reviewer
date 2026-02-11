# Java Review Rules

These rules supplement the common review framework. Apply them to `.java` files.

## Style Standard

Follow the **Google Java Style Guide** as the baseline:

- 2-space or 4-space indentation (respect project config). Google uses 2, many enterprises use 4.
- Braces on same line (K&R style). No single-statement blocks without braces.
- Column limit: 100 (Google) or 120. Respect project config.
- Static imports grouped separately, after all non-static imports. Wildcard imports (`*`) discouraged.
- Javadoc on all public API members. `@param`, `@return`, `@throws` for non-trivial methods.
- `@Override` on every overriding method — flag missing annotation.
- Constants: `UPPER_SNAKE_CASE`. Everything else: `camelCase` / `PascalCase` per Java convention.
- Annotations on their own line before the annotated element, not inline.

Do not flag formatting issues that Checkstyle / Spotless / google-java-format would auto-fix.

## Prefer Modern Features

| Legacy Pattern | Prefer | Since |
|---|---|---|
| Verbose data classes (getters, setters, equals, hashCode, toString) | `record` | 17 |
| `instanceof` + manual cast | Pattern matching `instanceof` | 16 |
| Long `if/else if` chains on type | `switch` with pattern matching | 21 |
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

- **Flag raw types**: `List`, `Map` without type parameters — MAJOR.
- **Flag unchecked casts**: `(List<String>) obj` without prior type check. Use pattern matching instanceof.
- **Encourage sealed interfaces**: For domain types with known subtypes — enables exhaustive switch.
- **Records for DTOs**: If a class is just data (getters, equals, hashCode), it should be a `record`. Flag manual implementations of what a record gives free.
- **Var for local variables**: Encourage `var` when the right-hand side makes the type obvious. Flag `var` when it obscures the type.
- **Generics**: Flag method signatures with more than 2 wildcards (`? extends`, `? super`) — likely too complex. Consider a named type parameter.

## Functional Patterns

- Prefer Stream API for collection transformations — `filter`, `map`, `flatMap`, `collect`
- Flag streams that mutate external state — streams should be pure pipelines
- Prefer method references (`String::toLowerCase`) over trivial lambdas (`s -> s.toLowerCase()`)
- Flag `Optional` used as a field type or method parameter — `Optional` is for return values only
- Flag `Optional.get()` without `isPresent()` check — use `orElseThrow()` or `map`/`flatMap` chains
- Encourage `Collectors.toUnmodifiableList()` or `Stream.toList()` (16+) over `Collectors.toList()`
- Flag nested streams (stream inside a stream's `map`) — usually indicates a need for `flatMap` or extracting a method

## Error Handling

- **Never** empty catch block — BLOCKER. At minimum, log and rethrow or explain why ignored.
- Flag `catch (Exception e)` / `catch (Throwable t)` at fine-grained level — catch specific types.
- Flag `throws Exception` on method signatures — be specific about what can fail.
- Encourage domain-specific exception hierarchy: `DomainException` → `OrderNotFoundException`, etc.
- Flag checked exceptions used for business logic flow — prefer unchecked exceptions or result types.
- Use try-with-resources for all `AutoCloseable` — flag manual `finally` blocks for resource cleanup.
- Flag `e.printStackTrace()` — use a logging framework (SLF4J + Logback/Log4j2).

## Spring Boot

- **Constructor injection only**: Flag `@Autowired` on fields — use constructor injection (preferably with Lombok `@RequiredArgsConstructor` or manual constructor). Field injection hides dependencies and breaks testability.
- **Layer discipline**: Controller → Service → Repository. Flag controllers calling repositories directly. Flag services importing Spring Web types (`HttpServletRequest`, `ResponseEntity`).
- **DTO ↔ Entity separation**: Flag JPA entities exposed in API responses/requests. Use DTOs (records) at the API boundary.
- **Validation**: Use `@Valid` / `@Validated` on request DTOs with Bean Validation annotations. Flag manual validation in controllers for common rules.
- **Exception handling**: Use `@ControllerAdvice` / `@RestControllerAdvice` with `@ExceptionHandler`. Flag try/catch in individual controllers for error-to-response mapping.
- **Profiles and configuration**: Flag hardcoded URLs, credentials, feature flags. Use `@Value` / `@ConfigurationProperties` with profiles.
- **Transaction management**: `@Transactional` on service methods, not repositories or controllers. Flag `@Transactional` on read-only queries without `readOnly = true`.
- **Avoid `@Component` scanning abuse**: Flag `@Service` / `@Component` on classes that should be explicitly configured as `@Bean` (e.g., third-party wrappers, conditional beans).
- **Security**: Flag endpoints missing `@PreAuthorize` or Spring Security config. Flag disabled CSRF without justification.

## Quarkus

- **CDI over Spring DI**: Use `@Inject`, `@ApplicationScoped`, `@RequestScoped`. Flag Spring-specific annotations in Quarkus code.
- **Native-image awareness**: Flag reflection-heavy patterns that break GraalVM native compilation. Use `@RegisterForReflection` when necessary.
- **RESTEasy Reactive**: Prefer reactive endpoints (`@GET` returning `Uni<T>` / `Multi<T>`) for non-blocking I/O. Flag blocking calls without `@Blocking` annotation.
- **Panache**: Prefer Active Record or Repository pattern via Panache over raw JPA `EntityManager` for standard CRUD.
- **Configuration**: Use `@ConfigProperty` or MicroProfile Config. Flag hardcoded values.
- **Health and metrics**: Flag missing health checks (`@Liveness`, `@Readiness`) in production services.
- **Dev Services**: Leverage Quarkus Dev Services for tests. Flag manual container setup in tests when Dev Services would work.

## Testing

- Use JUnit 5 (`@Test` from `org.junit.jupiter`). Flag JUnit 4 (`org.junit.Test`) in new code.
- Prefer AssertJ (`assertThat`) over JUnit assertions — more readable, better error messages.
- `@Nested` classes for grouping related tests (replaces descriptive naming conventions).
- Flag `@SpringBootTest` when a `@WebMvcTest` or `@DataJpaTest` slice would suffice — startup cost.
- Use `@MockBean` or Mockito `@Mock` + `@InjectMocks`. Flag mock setup that reaches 3+ levels deep — indicates the code under test has too many dependencies.
- Flag tests without assertions — MAJOR.
- Parameterized tests (`@ParameterizedTest` + `@CsvSource` / `@MethodSource`) for data-driven tests.
- For Quarkus: use `@QuarkusTest` for integration, `@QuarkusTestResource` for external dependencies.

## Common Enterprise Anti-Patterns

- **God service**: `XxxService` with 20+ methods. Split by use case or aggregate.
- **Anemic domain model**: Entities are pure data bags, all logic in services. Move behavior to domain objects where it belongs.
- **Overuse of `@Transactional`**: Every method annotated — transactions should be at the use-case level, not per-method.
- **Stringly-typed code**: Using `String` for IDs, statuses, currency codes. Use `record`-wrapped primitives or enums.
- **`Util` / `Helper` classes**: Static method dumping grounds. Refactor into domain-specific methods or extension services.
- **Lombok abuse**: `@Data` on JPA entities (breaks equals/hashCode with lazy-loaded fields). Use `@Getter` + `@Setter` + explicit `@EqualsAndHashCode` excluding lazy fields, or use records for DTOs.
- **Over-abstraction**: `AbstractBaseService<T>` with a single implementation — YAGNI. Create abstractions when the second use case arrives.
- **Ignoring `java.time`**: Using `Date`, `Calendar`, `Timestamp` in new code. Always use `java.time` types.
