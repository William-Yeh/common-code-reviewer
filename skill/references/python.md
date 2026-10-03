# Python Review Rules

These rules supplement the common review framework. Apply them to `.py` and `.pyi` files.

## Style Standard

Follow **PEP 8** as the baseline, enforced by **Ruff** (or Black + isort). Additionally:

- **PEP 484 / PEP 526**: Type hints on all public function signatures. Internal functions should have hints when non-obvious.
- **PEP 585**: Use built-in generics (`list[str]`, `dict[str, int]`) not `typing.List`, `typing.Dict` (deprecated since 3.9).
- **PEP 604**: Use `X | Y` union syntax, not `Union[X, Y]` (3.10+).
- **PEP 695**: Use the `type X = ...` statement for type aliases and inline type parameters (`class Box[T]`, `def first[T](xs: list[T]) -> T`) instead of `TypeAlias` / explicit `TypeVar` declarations (3.12+).
- **PEP 673**: Use `Self` for methods returning the same class type.
- Docstrings: Google style or NumPy style — pick one and be consistent within the project. Flag mixed styles.
- Line length: 88 (Black default) or 120 — respect project config. Do not flag line length if a formatter is configured.

Do not flag formatting issues that Ruff/Black would auto-fix. Focus on semantic and structural issues. Ruff 0.16 enlarged its default rule set roughly sevenfold (59 → 413 rules), so in projects that run Ruff, leave lint-level findings to it.

Gate version-specific advice on the project's `requires-python` (or the oldest interpreter it supports), not on the newest release.

## Prefer Modern Features

Findings from this table are `common/language-idiom` unless a row's pattern also matches a more specific rule in this reference or the catalog; that rule's ID and severity take precedence.

| Legacy Pattern | Prefer | Since |
|---|---|---|
| `typing.Optional[X]` | `X \| None` | 3.10 |
| `typing.List`, `typing.Dict`, etc. | `list`, `dict`, `tuple`, `set` | 3.9 |
| `typing.Union[X, Y]` | `X \| Y` | 3.10 |
| `collections.namedtuple` / `NamedTuple("P", [...])` functional form | `class P(NamedTuple)` with annotated fields, or `@dataclass(frozen=True)` | 3.6+ |
| Plain dicts for structured data | `dataclass`, `TypedDict`, or Pydantic `BaseModel` | 3.7+ |
| `if/elif/elif` chains on a value | `match/case` (structural pattern matching) | 3.10 |
| `TypeAlias` / explicit `TypeVar` declarations | `type X = ...` statement and inline generics (`class Box[T]`, `def f[T]()`) | 3.12 |
| `.format()` templating with manual escaping | t-strings (template string literals) for safe custom string processing | 3.14 |
| Quoted forward references (`"User"`) or `from __future__ import annotations` in code that only supports 3.14+ | Unquoted annotations (deferred evaluation, PEP 649/749); read them with `annotationlib.get_annotations` | 3.14 |
| `asyncio.iscoroutinefunction` | `inspect.iscoroutinefunction` (the asyncio one is deprecated) | 3.14 |
| `if TYPE_CHECKING:` blocks or function-local imports used only to defer import cost | Module-level `lazy import x` / `lazy from x import Y` (PEP 810) | 3.15 |
| `MappingProxyType` or defensive `dict` copies for immutable mappings | `frozendict` (PEP 814; hashable when its contents are) | 3.15 |
| `_MISSING = object()` sentinels | built-in `sentinel` (PEP 661) | 3.15 |
| `itertools.chain.from_iterable` / nested comprehension to flatten | `[*xs for xs in lists]`, `{**d for d in dicts}` (PEP 798) | 3.15 |
| `re.match` | `re.prefixmatch` (soft deprecation, no warning) | 3.15 |
| `profile` module | `profiling.tracing` (`profile` is removed in 3.17) | 3.15 |
| `@abstractmethod` + `ABC` for protocols | `Protocol` (structural subtyping) | 3.8+ |
| `try/except` around ordinary branching on values you already hold | `if`/`match` guards (EAFP stays idiomatic for I/O, lookups, and races) | — |
| Manual `__enter__`/`__exit__` | `contextlib.contextmanager` or `contextlib.asynccontextmanager` | — |
| `os.path` | `pathlib.Path` | 3.4+ |
| `%` formatting or `.format()` | f-strings | 3.6+ |
| `dict.keys()` iteration | Iterate dict directly | — |
| Mutable default arguments | `field(default_factory=...)` or `None` sentinel | — |

## Type System

- **Flag untyped public APIs**: All public functions, methods, and class attributes should have type annotations.
- **Flag `Any`**: Same rule as `any` in TypeScript — MAJOR unless justified.
- **Encourage `Protocol`** over `ABC` when you only need structural compatibility, not inheritance.
- **Encourage `TypeIs`** (3.13+) for custom type narrowing functions; it narrows in both branches. Keep `TypeGuard` only when the narrowed type is not a subtype of the input type.
- **Flag `cast()`** the same way as TypeScript's `as` — it bypasses checking.
- **Generics**: Prefer PEP 695 inline type parameters (`class Box[T]`, `def f[T]()`) over module-level `TypeVar` declarations (3.12+). Use constraints/bounds (`[T: numbers.Real]`) where applicable. Flag unbounded type parameters on public APIs — it's the Python equivalent of `any`.
- **`TypedDict`** for dictionaries with known keys. Flag raw `dict[str, Any]` for structured data. On 3.15+, use `closed=True` or `extra_items=` (PEP 728) when the extra keys are known to be absent or uniformly typed.
- **`Literal`** types for string enums and fixed values. Flag `str` where only specific values are valid.

## Functional Patterns

- Prefer list/dict/set comprehensions over `map`/`filter` with lambdas — more Pythonic and readable
- Prefer generator expressions for large sequences — lazy evaluation, lower memory
- Flag mutable default arguments (`def foo(items=[])`) — `common/shared-mutable-state`: the default object is shared across calls
- Encourage `functools.reduce`, `itertools` for complex transformations
- Flag mutation of function parameters — create new objects instead
- Encourage `@dataclass(frozen=True)` for immutable value objects
- Use `tuple` for fixed-size immutable sequences, `frozenset` for immutable sets

## Error Handling

- **Never** bare `except:` or `except Exception:` without re-raising — BLOCKER
- Prefer specific exception types. Flag `except Exception as e: pass`.
- Use custom exception hierarchies for domain errors — not `ValueError` for everything.
- Flag `except` blocks that silently swallow and return a default — MAJOR if the default hides data integrity issues.
- Encourage `ExceptionGroup` and `except*` for concurrent error handling (3.11+).
- Flag `return`, `break`, or `continue` inside a `finally` block — `common/ignored-error`. It silently discards the in-flight exception; 3.14 emits a `SyntaxWarning` for it (PEP 765).
- `except A, B:` without parentheses is valid from 3.14 (PEP 758; parentheses are still required with `as`). Flag it only when `requires-python` admits 3.13 or earlier, where it is a `SyntaxError` — `common/deprecated-api`.

## Runtime Defaults

- **Multiprocessing start method**: Since 3.14 the default on Linux is `forkserver`, not `fork`. Flag code that relies on fork-inherited globals or passes unpicklable targets without calling `set_start_method` or using `get_context("fork")` — `common/shared-mutable-state`.
- **Text encoding**: Python 3.15 defaults `open()` to UTF-8 (PEP 686), but older interpreters use the locale encoding. While `requires-python` admits anything older than 3.15, flag text-mode `open()` without `encoding=` — `common/nondeterministic-dependency`.
- **Lazy imports**: Flag `lazy import` of a module whose import side effects matter, such as plugin or ORM model registration — `common/hidden-side-effect`. `lazy` is only legal at module scope.
- Logging: use `logger.exception()` in catch blocks (includes traceback), not `logger.error(str(e))`.

## FastAPI

- **Pydantic models for all I/O**: Flag raw dicts or untyped parameters in route handlers. All request bodies, query params, and responses should use Pydantic `BaseModel`.
- **Dependency injection**: Use `Depends()` for shared logic (auth, DB sessions, config). Flag manual instantiation in route handlers.
- **Response models**: Every route needs a declared output type, which drives output validation, serialization, and OpenAPI docs. Prefer the return type annotation (`-> UserOut`); use `response_model` only when the declared output type differs from what the function returns (e.g. returning an ORM object filtered through a narrower model).
- **Current FastAPI**: Flag `pydantic.v1` imports in FastAPI apps (support dropped) and `ORJSONResponse` / `UJSONResponse` (deprecated; declare a return type and let Pydantic serialize) — `common/deprecated-api`. Flag `strict_content_type=False` without a documented client constraint — `common/insecure-default`. Code that iterates or mutates `router.routes` as a flat list breaks on 0.137+, where it is a tree — `common/deprecated-api`.
- **Status codes**: Use `status.HTTP_xxx` constants, not magic integers. Flag `return {"error": "..."}` — use `HTTPException` or custom exception handlers.
- **Async consistency**: If the route is `async def`, all I/O inside must be awaited. Flag sync I/O (e.g., `open()`, `requests.get()`) in async routes — use `aiofiles`, `httpx`, or run in executor.
- **Path operations**: Flag business logic in route functions. Route handlers should validate input, call a service, and return output.
- **Security**: Flag routes missing dependency-injected auth. Flag `Depends()` chains that don't propagate auth context.
- **Background tasks**: Use `BackgroundTasks` for fire-and-forget work, not bare `asyncio.create_task()` — FastAPI manages lifecycle.

## Pydantic

- Flag `@model_validator(mode="after")` functions written as classmethods (first parameter `cls`) — `common/deprecated-api`. Since 2.12, after-validators are instance methods taking `self`.
- Flag `model.model_fields` / `model.model_computed_fields` accessed on an instance — `common/deprecated-api` (deprecated in 2.11); use `type(model).model_fields`.

## SQLAlchemy

- **Session management**: Flag sessions created without a context manager or `try/finally`. Use `with Session() as session:` or FastAPI's `Depends(get_db)`.
- **N+1 queries**: Flag relationship access in loops without `joinedload()`, `selectinload()`, or `subqueryload()`. Inside a route handler or anything it calls per request, this is `common/n-plus-one-hot-path`; in batch jobs and scripts, `common/n-plus-one-query`.
- **Raw SQL**: Flag `text()` queries that interpolate user input — SQL injection risk (BLOCKER). Use bound parameters.
- **Model design**: Flag models mixing domain logic with ORM mapping. Keep models thin — business logic belongs in services.
- **Migrations (Alembic)**: Flag manual schema changes without a migration. Flag `op.execute()` with raw DDL that could be expressed as Alembic operations.
- **Eager loading strategy**: Flag `lazy="select"` (the default) on relationships accessed in list views — use `lazy="selectin"` or explicit loading.
- **Prefer 2.0 style**: Flag legacy `Query` API (`session.query(...)`) — use `select()` statements with `session.execute()`.
- **SQLAlchemy 2.1**:
  - Async engines need the `sqlalchemy[asyncio]` extra; greenlet is no longer installed by default. Flag async usage whose dependency spec omits the extra — `common/deprecated-api`.
  - `mapped_column(default=..., insert_default=...)` together raises; flag it — `common/deprecated-api`.
  - Type statements as `Select[int, str]`, not `Select[Tuple[int, str]]` — `common/language-idiom`.
  - On 3.14+, prefer `tstring(t"... {value}")` over `text()` with manual binds; it binds interpolations as parameters — `common/language-idiom`.
- **Transaction boundaries**: Flag commits inside loops. Prefer a single commit per unit of work.

## Testing

- Use `pytest` idioms: plain functions over `unittest.TestCase` classes
- Use `pytest.fixture` for setup, not `setUp`/`tearDown`
- Flag `mock.patch` on internal implementation details — mock at boundaries (HTTP, DB, file system)
- Use `pytest.raises` with `match` parameter for exception messages
- Prefer `factory_boy` or fixture factories over complex manual test data setup
- Flag tests without assertions — `common/assertion-free-test` (false green)
- Parameterize related test cases with `@pytest.mark.parametrize` instead of copy-paste

## Common Enterprise Anti-Patterns

- **Circular imports**: Usually indicates wrong module boundaries. Suggest restructuring first. For annotation-only cycles, 3.14's deferred annotations remove the need for quoting, and 3.15's `lazy from x import Y` replaces `if TYPE_CHECKING:` blocks; use `TYPE_CHECKING` only on older targets.
- **God modules**: A `utils.py` or `helpers.py` with 500+ lines — split by domain.
- **Stringly-typed code**: Using `str` for statuses, types, modes — use `Enum`, `Literal`, or `StrEnum`.
- **Global mutable state**: Module-level mutable variables shared across requests — use dependency injection or request-scoped state.
- **Ignoring async**: Using synchronous libraries (e.g., `requests`) in an async application — causes thread starvation.
- **Over-inheriting**: Deep class hierarchies where composition would be simpler and more flexible.
- **Missing `__all__`**: Public modules should define `__all__` to make the public API explicit.

## Change Risk

### Scored Units

`def` and `async def` at module level, in classes (including `__init__`,
properties, and dunder methods), and named nested `def`s. `lambda` bodies fold
into the enclosing unit. Not scored, having no body: `@overload` signatures,
`Protocol` and abstract methods whose body is only `...` or `pass`, `.pyi` stubs.

### Decision Points

| Category | Python |
|---|---|
| Branch | `if`, `elif`, comprehension `if` filter |
| Loop | `for`, `async for`, `while`, comprehension `for` |
| Case arm | each `case` in `match`; `case _` free |
| Exception handler | each `except` |
| Short-circuit operator | `and`, `or` |
| Conditional expression | `x if c else y` |
| Early-return operator | none |

Not counted: `else`, `finally`, `with`, `assert`, loop `else`, `:=`.

### Test Files

`test_*.py`, `*_test.py`, `conftest.py`, and anything under `tests/` or `test/`.

### Coverage Evidence

`pytest --cov=<package> --cov-report=lcov` writes `coverage.lcov`;
`--cov-report=xml` writes Cobertura `coverage.xml`. Both carry coverage.py line
data; the lines inside the unit's range give cov.

### Oracle Deviations

`lizard` matches this profile except that it counts `case _` (+1). ruff and
flake8 `C901` (mccabe) do not count `and`/`or`, so their CC runs lower. radon
`cc` matches.
