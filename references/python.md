# Python Review Rules

These rules supplement the common review framework. Apply them to `.py` and `.pyi` files.

## Style Standard

Follow **PEP 8** as the baseline, enforced by **Ruff** (or Black + isort). Additionally:

- **PEP 484 / PEP 526**: Type hints on all public function signatures. Internal functions should have hints when non-obvious.
- **PEP 585**: Use built-in generics (`list[str]`, `dict[str, int]`) not `typing.List`, `typing.Dict` (deprecated since 3.9).
- **PEP 604**: Use `X | Y` union syntax, not `Union[X, Y]` (3.10+).
- **PEP 657**: Use fine-grained `TypeAlias` for complex type expressions.
- **PEP 673**: Use `Self` for methods returning the same class type.
- Docstrings: Google style or NumPy style — pick one and be consistent within the project. Flag mixed styles.
- Line length: 88 (Black default) or 120 — respect project config. Do not flag line length if a formatter is configured.

Do not flag formatting issues that Ruff/Black would auto-fix. Focus on semantic and structural issues.

## Prefer Modern Features

| Legacy Pattern | Prefer | Since |
|---|---|---|
| `typing.Optional[X]` | `X \| None` | 3.10 |
| `typing.List`, `typing.Dict`, etc. | `list`, `dict`, `tuple`, `set` | 3.9 |
| `typing.Union[X, Y]` | `X \| Y` | 3.10 |
| `NamedTuple` class syntax | `@dataclass(frozen=True)` or `NamedTuple` functional form | 3.7+ |
| Plain dicts for structured data | `dataclass`, `TypedDict`, or Pydantic `BaseModel` | 3.7+ |
| `if/elif/elif` chains on a value | `match/case` (structural pattern matching) | 3.10 |
| `@abstractmethod` + `ABC` for protocols | `Protocol` (structural subtyping) | 3.8+ |
| `try/except` for flow control | LBYL with guards, or `match/case` | — |
| Manual `__enter__`/`__exit__` | `contextlib.contextmanager` or `contextlib.asynccontextmanager` | — |
| `os.path` | `pathlib.Path` | 3.4+ |
| `%` formatting or `.format()` | f-strings | 3.6+ |
| `dict.keys()` iteration | Iterate dict directly | — |
| Mutable default arguments | `field(default_factory=...)` or `None` sentinel | — |

## Type System

- **Flag untyped public APIs**: All public functions, methods, and class attributes should have type annotations.
- **Flag `Any`**: Same rule as `any` in TypeScript — MAJOR unless justified.
- **Encourage `Protocol`** over `ABC` when you only need structural compatibility, not inheritance.
- **Encourage `TypeGuard` / `TypeIs`** for custom type narrowing functions.
- **Flag `cast()`** the same way as TypeScript's `as` — it bypasses checking.
- **Generics**: Use `TypeVar` with constraints or bounds. Flag unbounded `TypeVar` on public APIs — it's the Python equivalent of `any`.
- **`TypedDict`** for dictionaries with known keys. Flag raw `dict[str, Any]` for structured data.
- **`Literal`** types for string enums and fixed values. Flag `str` where only specific values are valid.

## Functional Patterns

- Prefer list/dict/set comprehensions over `map`/`filter` with lambdas — more Pythonic and readable
- Prefer generator expressions for large sequences — lazy evaluation, lower memory
- Flag mutable default arguments (`def foo(items=[])`) — BLOCKER, shared state bug
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
- Logging: use `logger.exception()` in catch blocks (includes traceback), not `logger.error(str(e))`.

## FastAPI

- **Pydantic models for all I/O**: Flag raw dicts or untyped parameters in route handlers. All request bodies, query params, and responses should use Pydantic `BaseModel`.
- **Dependency injection**: Use `Depends()` for shared logic (auth, DB sessions, config). Flag manual instantiation in route handlers.
- **Response models**: All routes should specify `response_model` — this enforces output validation and drives OpenAPI docs.
- **Status codes**: Use `status.HTTP_xxx` constants, not magic integers. Flag `return {"error": "..."}` — use `HTTPException` or custom exception handlers.
- **Async consistency**: If the route is `async def`, all I/O inside must be awaited. Flag sync I/O (e.g., `open()`, `requests.get()`) in async routes — use `aiofiles`, `httpx`, or run in executor.
- **Path operations**: Flag business logic in route functions. Route handlers should validate input, call a service, and return output.
- **Security**: Flag routes missing dependency-injected auth. Flag `Depends()` chains that don't propagate auth context.
- **Background tasks**: Use `BackgroundTasks` for fire-and-forget work, not bare `asyncio.create_task()` — FastAPI manages lifecycle.

## SQLAlchemy

- **Session management**: Flag sessions created without a context manager or `try/finally`. Use `with Session() as session:` or FastAPI's `Depends(get_db)`.
- **N+1 queries**: Flag relationship access in loops without `joinedload()`, `selectinload()`, or `subqueryload()`. This is a BLOCKER in production.
- **Raw SQL**: Flag `text()` queries that interpolate user input — SQL injection risk (BLOCKER). Use bound parameters.
- **Model design**: Flag models mixing domain logic with ORM mapping. Keep models thin — business logic belongs in services.
- **Migrations (Alembic)**: Flag manual schema changes without a migration. Flag `op.execute()` with raw DDL that could be expressed as Alembic operations.
- **Eager loading strategy**: Flag `lazy="select"` (the default) on relationships accessed in list views — use `lazy="selectin"` or explicit loading.
- **Prefer 2.0 style**: Flag legacy `Query` API (`session.query(...)`) — use `select()` statements with `session.execute()`.
- **Transaction boundaries**: Flag commits inside loops. Prefer a single commit per unit of work.

## Testing

- Use `pytest` idioms: plain functions over `unittest.TestCase` classes
- Use `pytest.fixture` for setup, not `setUp`/`tearDown`
- Flag `mock.patch` on internal implementation details — mock at boundaries (HTTP, DB, file system)
- Use `pytest.raises` with `match` parameter for exception messages
- Prefer `factory_boy` or fixture factories over complex manual test data setup
- Flag tests without assertions (MAJOR — false green)
- Parameterize related test cases with `@pytest.mark.parametrize` instead of copy-paste

## Common Enterprise Anti-Patterns

- **Circular imports**: Usually indicates wrong module boundaries. Suggest restructuring or using `TYPE_CHECKING` imports.
- **God modules**: A `utils.py` or `helpers.py` with 500+ lines — split by domain.
- **Stringly-typed code**: Using `str` for statuses, types, modes — use `Enum`, `Literal`, or `StrEnum`.
- **Global mutable state**: Module-level mutable variables shared across requests — use dependency injection or request-scoped state.
- **Ignoring async**: Using synchronous libraries (e.g., `requests`) in an async application — causes thread starvation.
- **Over-inheriting**: Deep class hierarchies where composition would be simpler and more flexible.
- **Missing `__all__`**: Public modules should define `__all__` to make the public API explicit.
