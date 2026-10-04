# Review Rule Coverage

Generated from the inline Review Rule catalogs and Conformance Fixtures.
Run `uv run tests/scripts/sync_generated.py` after changing either.

## common

| Review Rule | Severity | Required evidence |
|---|---|---|
| `common/anemic-domain` | MAJOR | `go/user_service.go:48-56`<br>`java/PaymentService.java:161-170`<br>`python/user_management.py:64-72`<br>`rust/user_service.rs:46-53`<br>`typescript/notification-service.ts:158-166` |
| `common/api-misuse` | MAJOR | `typescript/task-board.tsx:15` |
| `common/assertion-free-test` | MAJOR | `java/InvoiceServiceTest.java:13-16` |
| `common/authorization-gap` | MAJOR | `go/user_service.go:162-163`<br>`python/user_management.py:172-174`<br>`typescript/notification-service.ts:148` |
| `common/blocking-in-async` | BLOCKER | `python/order_service.py:74-77` |
| `common/brittle-test` | MAJOR | `typescript/cart-pricing.test.ts:5-11` |
| `common/busy-wait` | MAJOR | `go/queue_drain.go:6-17` |
| `common/circular-dependency` | MAJOR | `typescript/architecture-gaps.ts:1` |
| `common/command-injection` | BLOCKER | `go/user_service.go:150-151`<br>`java/PaymentService.java:175`<br>`python/user_management.py:156-161`<br>`rust/order_handler.rs:17-19` |
| `common/complex-construction` | MAJOR | `java/PaymentService.java:52-54` |
| `common/coupled-side-effect` | MAJOR | `typescript/architecture-gaps.ts:29-33` |
| `common/critical-change-risk` | MAJOR | `go/rate_limiter.go:44-72`<br>`python/pricing_engine.py:42-66` |
| `common/dead-code` | MINOR | `go/user_service.go:144-146`<br>`java/PaymentService.java:136`<br>`python/user_management.py:146-151`<br>`rust/user_service.rs:116-118`<br>`typescript/notification-service.ts:123`<br>`typescript/notification-service.ts:142-145` |
| `common/deep-nesting` | MINOR | `go/user_service.go:98-107`<br>`java/PaymentService.java:63-72`<br>`python/user_management.py:101-107`<br>`rust/user_service.rs:84-96`<br>`typescript/notification-service.ts:49-77` |
| `common/dependency-inversion` | MAJOR | `rust/user_service.rs:121-123` |
| `common/deprecated-api` | MAJOR | `go/edge_proxy.go:29-33`<br>`go/edge_proxy.go:39` |
| `common/duplicated-logic` | MINOR | `java/PaymentService.java:132`<br>`python/user_management.py:141`<br>`typescript/notification-service.ts:52-55, 61-64, 71-74, 79-82, 84-87` |
| `common/eager-loading` | MAJOR | `typescript/architecture-gaps.ts:16-23` |
| `common/elevated-change-risk` | MINOR | `go/rate_limiter.go:32-41`<br>`python/pricing_engine.py:85-91` |
| `common/erased-failure` | MINOR | `rust/order_handler.rs:56-58` |
| `common/excess-complexity` | MINOR | `python/pricing_engine.py:69-82` |
| `common/framework-coupling` | MAJOR | `java/OrderController.java:9, 50, 69` |
| `common/god-module` | MAJOR | `go/order_handler.go:28`<br>`java/OrderController.java:34`<br>`python/order_service.py:26`<br>`typescript/order-service.ts:8` |
| `common/graceful-shutdown` | NIT | `go/order_handler.go:111-113` |
| `common/hard-coded-dependency` | MAJOR | `go/user_service.go:83-84`<br>`java/OrderController.java:36-40`<br>`java/PaymentService.java:53, 120`<br>`python/user_management.py:95-96`<br>`rust/user_service.rs:58, 71`<br>`typescript/notification-service.ts:114-116`<br>`typescript/notification-service.ts:52, 61, 71, 79, 84` |
| `common/hidden-side-effect` | MAJOR | `go/user_service.go:59, 68-70`<br>`java/PaymentService.java:92, 103-105`<br>`python/user_management.py:76, 84-85, 87-88`<br>`rust/user_service.rs:56-62`<br>`typescript/notification-service.ts:92, 101-103` |
| `common/hot-path-allocation` | MINOR | `go/scanner_stats.go:10` |
| `common/ignored-error` | BLOCKER | `go/order_handler.go:30`<br>`go/order_handler.go:68, 70, 77`<br>`go/order_handler.go:70`<br>`go/order_handler.go:20-25`<br>`go/order_handler.go:92`<br>`go/user_service.go:89`<br>`go/user_service.go:113`<br>`java/PaymentService.java:106-107`<br>`python/order_service.py:37-38`<br>`typescript/order-service.ts:29` |
| `common/imperative-transformation` | MINOR | `python/user_management.py:114-123`<br>`typescript/order-service.ts:44-51` |
| `common/incomplete-error-handling` | MINOR | `go/order_handler.go:44, 97`<br>`java/OrderController.java:63-64`<br>`java/OrderController.java:86`<br>`java/PaymentService.java:122`<br>`python/order_service.py:74-78`<br>`typescript/order-service.ts:59-63` |
| `common/inefficient-data-structure` | MINOR | `typescript/architecture-gaps.ts:25-27` |
| `common/insecure-default` | MAJOR | `typescript/architecture-gaps.ts:10` |
| `common/interface-segregation` | MAJOR | `go/user_service.go:14-23`<br>`java/PaymentService.java:10-18`<br>`python/user_management.py:10-26`<br>`rust/user_service.rs:10-19`<br>`typescript/notification-service.ts:8-16` |
| `common/language-idiom` | NIT | `go/order_handler.go:16, 20, 24, 91, 97`<br>`go/user_service.go:15, 29-41`<br>`java/OrderController.java:83`<br>`python/order_service.py:78`<br>`python/order_service.py:16, 73` |
| `common/layer-violation` | MAJOR | `typescript/notification-service.ts:1, 4-5, 48, 52, 61, 71, 79, 84, 92, 102-103, 109, 114-115, 118-119, 142, 144, 148, 151`<br>`typescript/order-service.ts:9-10` |
| `common/liskov-violation` | MAJOR | `java/PaymentService.java:39-41`<br>`python/user_management.py:42-45` |
| `common/magic-literal` | MINOR | `java/PaymentService.java:95`<br>`python/order_service.py:40`<br>`rust/order_handler.rs:72`<br>`typescript/order-service.ts:26` |
| `common/missing-abstraction` | MAJOR | `typescript/architecture-gaps.ts:46-54` |
| `common/missing-cache` | MINOR | `typescript/architecture-gaps.ts:35-44` |
| `common/missing-input-validation` | MAJOR | `go/order_handler.go:32`<br>`java/OrderController.java:50`<br>`python/order_service.py:26`<br>`typescript/order-service.ts:19` |
| `common/missing-timeout` | MINOR | `go/order_handler.go:94-95`<br>`java/OrderController.java:87-88, 91, 92`<br>`python/order_service.py:74-77` |
| `common/mixed-abstraction` | MINOR | `go/user_service.go:112-132`<br>`python/user_management.py:110`<br>`typescript/notification-service.ts:118-128` |
| `common/n-plus-one-hot-path` | BLOCKER | `go/order_handler.go:70-72`<br>`python/order_service.py:52-55` |
| `common/n-plus-one-query` | MAJOR | `rust/order_handler.rs:32-36` |
| `common/nondeterministic-dependency` | MAJOR | `go/user_service.go:80`<br>`java/PaymentService.java:114`<br>`python/user_management.py:102`<br>`typescript/notification-service.ts:110-112` |
| `common/open-closed-violation` | MAJOR | `go/user_service.go:26-43`<br>`java/PaymentService.java:61-86`<br>`python/user_management.py:49-59`<br>`typescript/notification-service.ts:48-89` |
| `common/path-traversal` | BLOCKER | `go/user_service.go:159`<br>`python/user_management.py:167-169`<br>`rust/order_handler.rs:26`<br>`typescript/notification-service.ts:151` |
| `common/private-logic` | MINOR | `typescript/architecture-gaps.ts:61-65` |
| `common/resource-leak` | BLOCKER | `go/order_handler.go:58`<br>`java/PaymentService.java:103-105` |
| `common/sensitive-data-exposure` | MINOR | `go/order_handler.go:60`<br>`java/PaymentService.java:69`<br>`rust/order_handler.rs:67`<br>`typescript/order-service.ts:57` |
| `common/shared-mutable-state` | MAJOR | `go/order_handler.go:14-18`<br>`java/OrderController.java:42`<br>`python/order_service.py:11`<br>`python/order_service.py:9`<br>`typescript/order-service.ts:5` |
| `common/speculative-abstraction` | MINOR | `java/ReportExporters.java:11-15, 26-30` |
| `common/sql-injection` | BLOCKER | `go/order_handler.go:34-39, 71`<br>`java/OrderController.java:52-58`<br>`java/OrderController.java:74-75`<br>`python/order_service.py:28-32`<br>`python/order_service.py:67-69`<br>`rust/order_handler.rs:5`<br>`rust/order_handler.rs:11`<br>`typescript/order-service.ts:21-24`<br>`typescript/order-service.ts:39-42` |
| `common/style-naming` | NIT | `typescript/order-service.ts:8` |
| `common/style-readability` | NIT | `typescript/architecture-gaps.ts:68-70` |
| `common/unbounded-query` | MAJOR | `go/order_handler.go:58`<br>`java/OrderController.java:46`<br>`python/order_service.py:49`<br>`rust/order_handler.rs:11-12`<br>`typescript/order-service.ts:14` |
| `common/unclear-name` | MINOR | `go/user_service.go:134-136`<br>`java/PaymentService.java:147, 148-151`<br>`python/user_management.py:135-143`<br>`rust/user_service.rs:106-114`<br>`typescript/notification-service.ts:132-134` |
| `common/unhandled-variant` | MAJOR | `go/user_service.go:27-44`<br>`python/user_management.py:49-59`<br>`rust/user_service.rs:40` |
| `common/unmanaged-concurrency` | MAJOR | `go/order_handler.go:52` |
| `common/unnecessary-mutation` | MAJOR | `python/pricing_engine.py:69-82` |
| `common/unsafe-deserialization` | BLOCKER | `typescript/architecture-gaps.ts:12-14` |
| `common/weak-type-model` | MAJOR | `go/order_handler.go:29, 91`<br>`go/user_service.go:15, 52-53`<br>`java/OrderController.java:42, 45`<br>`java/OrderController.java:17`<br>`java/PaymentService.java:163-166`<br>`python/user_management.py:64-65, 69-70`<br>`typescript/notification-service.ts:160, 165`<br>`typescript/order-service.ts:5, 19, 38, 44, 56` |
| `common/xss` | BLOCKER | `typescript/notification-service.ts:153-154` |

## dockerfile

| Review Rule | Severity | Required evidence |
|---|---|---|
| `dockerfile/baked-secret` | BLOCKER | `dockerfile/Dockerfile.web:4` |
| `dockerfile/broad-stage-copy` | MAJOR | `dockerfile/Dockerfile.builder:12` |
| `dockerfile/cache-hostile-copy` | MINOR | `dockerfile/Dockerfile.web:10-11` |
| `dockerfile/confused-build-runtime-config` | MINOR | `dockerfile/Dockerfile.builder:14, 24` |
| `dockerfile/heavy-runtime-base` | MAJOR | `dockerfile/Dockerfile.worker:12` |
| `dockerfile/implicit-add` | MINOR | `dockerfile/Dockerfile.web:13` |
| `dockerfile/latest-base` | BLOCKER | `dockerfile/Dockerfile.web:1` |
| `dockerfile/missing-healthcheck` | MINOR | `dockerfile/Dockerfile.builder:absent`<br>`dockerfile/Dockerfile.web:absent` |
| `dockerfile/missing-workdir` | MINOR | `dockerfile/Dockerfile.web:absent` |
| `dockerfile/mutable-base` | MAJOR | `dockerfile/Dockerfile.builder:1, 7` |
| `dockerfile/root-runtime` | MAJOR | `dockerfile/Dockerfile.builder:absent`<br>`dockerfile/Dockerfile.web:absent` |
| `dockerfile/single-stage-toolchain` | MAJOR | `dockerfile/Dockerfile.web:1, 7` |
| `dockerfile/split-package-cleanup` | MAJOR | `dockerfile/Dockerfile.web:7-8` |
| `dockerfile/tls-disabled` | BLOCKER | `dockerfile/Dockerfile.web:15` |
| `dockerfile/unnamed-stage` | NIT | `dockerfile/Dockerfile.builder:7` |
| `dockerfile/unverified-artifact` | MAJOR | `dockerfile/Dockerfile.builder:17-19` |

## go

| Review Rule | Severity | Required evidence |
|---|---|---|
| `go/panic-in-library` | BLOCKER | `go/edge_proxy.go:59` |

## rust

| Review Rule | Severity | Required evidence |
|---|---|---|
| `rust/blocking-in-async` | BLOCKER | `rust/order_handler.rs:53` |
| `rust/clone-to-compile` | MINOR | `rust/user_service.rs:78, 89, 110` |
| `rust/discarded-result` | BLOCKER | `rust/order_handler.rs:60` |
| `rust/erased-public-error` | MAJOR | `rust/user_service.rs:13-18, 22, 70, 121` |
| `rust/hot-loop-clone` | MAJOR | `rust/order_handler.rs:128` |
| `rust/lock-across-await` | BLOCKER | `rust/order_handler.rs:46-49` |
| `rust/non-send-async-state` | MAJOR | `rust/non_send_future.rs:4-6, 10` |
| `rust/panic-in-library` | BLOCKER | `rust/order_handler.rs:6`<br>`rust/order_handler.rs:6, 21, 22, 27, 61`<br>`rust/user_service.rs:60` |
| `rust/raw-domain-value` | NIT | `rust/user_service.rs:47, 52` |
| `rust/shared-mutex-overuse` | MINOR | `rust/user_service.rs:66` |
| `rust/stringly-typed-domain` | MAJOR | `rust/user_service.rs:22-42`<br>`rust/user_service.rs:50, 51` |
| `rust/unsafe-without-safety` | BLOCKER | `rust/user_service.rs:103` |

## Summary

**Coverage: 92/92 Review Rules (100%)**
