# Review Rule Coverage

Generated from the inline Review Rule catalogs and Conformance Fixtures.
Run `uv run tests/scripts/sync_generated.py` after changing either.

## common

| Review Rule | Severity | Required evidence |
|---|---|---|
| `common/anemic-domain` | MAJOR | `go/user_service.go:56-64`<br>`java/PaymentService.java:157-165`<br>`python/user_management.py:68-76`<br>`rust/user_service.rs:57-66`<br>`typescript/notification-service.ts:157-164` |
| `common/authorization-gap` | MAJOR | `go/user_service.go:171-172`<br>`java/PaymentService.java:169`<br>`python/user_management.py:164-166`<br>`typescript/notification-service.ts:145` |
| `common/blocking-in-async` | BLOCKER | `python/order_service.py:84-88` |
| `common/circular-dependency` | MAJOR | `typescript/architecture-gaps.ts:1` |
| `common/command-injection` | BLOCKER | `go/user_service.go:160-162`<br>`java/PaymentService.java:171-173`<br>`python/user_management.py:147-153`<br>`rust/order_handler.rs:26-30` |
| `common/complex-construction` | MAJOR | `java/PaymentService.java:60-63` |
| `common/coupled-side-effect` | MAJOR | `typescript/architecture-gaps.ts:29-33` |
| `common/dead-code` | MINOR | `go/user_service.go:150-152`<br>`java/PaymentService.java:143`<br>`python/user_management.py:145-150`<br>`rust/user_service.rs:146-148`<br>`typescript/notification-service.ts:128`<br>`typescript/notification-service.ts:143-144` |
| `common/deep-nesting` | MINOR | `go/user_service.go:107-116`<br>`java/PaymentService.java:80-88`<br>`python/user_management.py:105-109`<br>`rust/user_service.rs:103-117`<br>`typescript/notification-service.ts:64-96` |
| `common/dependency-inversion` | MAJOR | `java/OrderController.java:43-46`<br>`rust/user_service.rs:152-154`<br>`typescript/order-service.ts:16-17` |
| `common/duplicated-logic` | MINOR | `go/user_service.go:124-130`<br>`go/user_service.go:147`<br>`java/PaymentService.java:140`<br>`python/user_management.py:117-124`<br>`python/user_management.py:139-140`<br>`typescript/notification-service.ts:82-87, 67-71` |
| `common/eager-loading` | MAJOR | `typescript/architecture-gaps.ts:16-23` |
| `common/erased-failure` | MINOR | `rust/order_handler.rs:77-78` |
| `common/framework-coupling` | MAJOR | `java/OrderController.java:38`<br>`typescript/architecture-gaps.ts:2, 9` |
| `common/god-module` | MAJOR | `go/order_handler.go:19-22`<br>`java/OrderController.java:21`<br>`python/order_service.py:35`<br>`rust/order_handler.rs:76-85`<br>`typescript/order-service.ts:13` |
| `common/graceful-shutdown` | NIT | `go/order_handler.go:119` |
| `common/hard-coded-dependency` | MAJOR | `go/user_service.go:95-96`<br>`java/PaymentService.java:126`<br>`python/user_management.py:99`<br>`rust/user_service.rs:73, 84-88`<br>`typescript/notification-service.ts:119-120`<br>`typescript/notification-service.ts:67-68, 72-73` |
| `common/hidden-side-effect` | MAJOR | `go/user_service.go:77-81`<br>`java/PaymentService.java:111-116`<br>`python/user_management.py:83-91`<br>`rust/user_service.rs:70-77`<br>`typescript/notification-service.ts:104-110` |
| `common/hot-path-allocation` | MINOR | `rust/order_handler.rs:58` |
| `common/ignored-error` | BLOCKER | `go/order_handler.go:38-39`<br>`go/order_handler.go:41`<br>`go/order_handler.go:82`<br>`go/order_handler.go:85`<br>`go/order_handler.go:106`<br>`go/user_service.go:101`<br>`go/user_service.go:121`<br>`java/PaymentService.java:117`<br>`python/order_service.py:47-48`<br>`typescript/order-service.ts:37` |
| `common/imperative-transformation` | MINOR | `typescript/order-service.ts:56-62` |
| `common/incomplete-error-handling` | MINOR | `go/order_handler.go:29-30`<br>`go/order_handler.go:113`<br>`java/OrderController.java:76`<br>`java/OrderController.java:93`<br>`java/OrderController.java:71`<br>`java/PaymentService.java:129`<br>`python/order_service.py:26, 83`<br>`typescript/order-service.ts:69` |
| `common/inefficient-data-structure` | MINOR | `typescript/architecture-gaps.ts:25-27` |
| `common/insecure-default` | MAJOR | `typescript/architecture-gaps.ts:10` |
| `common/interface-segregation` | MAJOR | `go/user_service.go:19-28`<br>`java/PaymentService.java:14-21`<br>`python/user_management.py:14-27`<br>`rust/user_service.rs:15-24`<br>`typescript/notification-service.ts:14-22`<br>`typescript/order-service.ts:25` |
| `common/language-idiom` | NIT | `go/order_handler.go:10`<br>`go/user_service.go:36-49`<br>`java/OrderController.java:13-34`<br>`java/OrderController.java:91`<br>`python/order_service.py:90`<br>`python/order_service.py:89`<br>`typescript/order-service.ts:72` |
| `common/layer-violation` | MAJOR | `typescript/notification-service.ts:9-10` |
| `common/liskov-violation` | MAJOR | `java/PaymentService.java:47-49`<br>`python/user_management.py:46-48`<br>`typescript/notification-service.ts:42-49` |
| `common/magic-literal` | MINOR | `java/PaymentService.java:106`<br>`python/order_service.py:52`<br>`rust/order_handler.rs:95`<br>`typescript/order-service.ts:35` |
| `common/missing-abstraction` | MAJOR | `typescript/architecture-gaps.ts:46-54` |
| `common/missing-cache` | MINOR | `typescript/architecture-gaps.ts:35-44` |
| `common/missing-input-validation` | MAJOR | `java/OrderController.java:59`<br>`python/order_service.py:35` |
| `common/missing-timeout` | MINOR | `go/order_handler.go:109`<br>`java/OrderController.java:97-100`<br>`python/order_service.py:85` |
| `common/mixed-abstraction` | MINOR | `go/user_service.go:120`<br>`java/PaymentService.java:136`<br>`python/user_management.py:113`<br>`typescript/notification-service.ts:123-131` |
| `common/n-plus-one-query` | MAJOR | `go/order_handler.go:85-94`<br>`python/order_service.py:65-69`<br>`rust/order_handler.rs:52-57` |
| `common/nondeterministic-dependency` | MAJOR | `go/user_service.go:91`<br>`java/PaymentService.java:121`<br>`python/user_management.py:103`<br>`typescript/notification-service.ts:115-116` |
| `common/open-closed-violation` | MAJOR | `go/user_service.go:34-51`<br>`java/PaymentService.java:71`<br>`python/user_management.py:55-63`<br>`rust/user_service.rs:50`<br>`typescript/notification-service.ts:62-97` |
| `common/path-traversal` | BLOCKER | `go/user_service.go:167`<br>`python/user_management.py:158-160`<br>`rust/order_handler.rs:35-36`<br>`typescript/notification-service.ts:148` |
| `common/private-logic` | MINOR | `typescript/architecture-gaps.ts:56-65` |
| `common/resource-leak` | BLOCKER | `go/order_handler.go:78`<br>`java/PaymentService.java:114` |
| `common/sensitive-data-exposure` | MINOR | `go/order_handler.go:54, 78`<br>`java/PaymentService.java:87`<br>`rust/order_handler.rs:89` |
| `common/shared-mutable-state` | MAJOR | `go/order_handler.go:35`<br>`java/OrderController.java:49`<br>`python/order_service.py:14`<br>`typescript/order-service.ts:10` |
| `common/sql-injection` | BLOCKER | `go/order_handler.go:44-49`<br>`go/order_handler.go:87`<br>`java/OrderController.java:63-68`<br>`java/OrderController.java:84-85`<br>`python/order_service.py:39-42`<br>`python/order_service.py:77-78`<br>`python/order_service.py:67`<br>`rust/order_handler.rs:8-9`<br>`rust/order_handler.rs:18`<br>`typescript/order-service.ts:30-32`<br>`typescript/order-service.ts:49-51` |
| `common/style-naming` | NIT | `typescript/order-service.ts:13` |
| `common/style-readability` | NIT | `typescript/architecture-gaps.ts:67-69` |
| `common/unbounded-query` | MAJOR | `go/order_handler.go:76`<br>`java/OrderController.java:54`<br>`python/order_service.py:62`<br>`rust/order_handler.rs:18-20`<br>`typescript/order-service.ts:21` |
| `common/unclear-name` | MINOR | `go/user_service.go:141-142`<br>`java/PaymentService.java:153-154`<br>`python/user_management.py:135-141`<br>`rust/user_service.rs:135-143`<br>`typescript/notification-service.ts:134-138` |
| `common/unhandled-variant` | MAJOR | `go/user_service.go:34-51`<br>`python/user_management.py:55-63` |
| `common/unmanaged-concurrency` | MAJOR | `go/order_handler.go:61`<br>`go/order_handler.go:26, 104` |
| `common/unnecessary-mutation` | MAJOR | `python/order_service.py:19` |
| `common/unsafe-deserialization` | BLOCKER | `typescript/architecture-gaps.ts:12-14` |
| `common/weak-type-model` | MAJOR | `go/order_handler.go:37, 104`<br>`go/user_service.go:61, 62`<br>`java/OrderController.java:13, 59, 81`<br>`java/OrderController.java:49, 52`<br>`java/PaymentService.java:160, 162`<br>`java/PaymentService.java:161`<br>`python/user_management.py:72-73`<br>`typescript/notification-service.ts:161, 163`<br>`typescript/order-service.ts:10, 42, 56, 67` |
| `common/xss` | BLOCKER | `typescript/notification-service.ts:151-152` |

## dockerfile

| Review Rule | Severity | Required evidence |
|---|---|---|
| `dockerfile/baked-secret` | BLOCKER | `dockerfile/Dockerfile.app:8` |
| `dockerfile/broad-stage-copy` | MAJOR | `dockerfile/Dockerfile.builder:16` |
| `dockerfile/cache-hostile-copy` | MINOR | `dockerfile/Dockerfile.app:16-17` |
| `dockerfile/confused-build-runtime-config` | MINOR | `dockerfile/Dockerfile.builder:17-18` |
| `dockerfile/implicit-add` | MINOR | `dockerfile/Dockerfile.app:22` |
| `dockerfile/latest-base` | BLOCKER | `dockerfile/Dockerfile.app:4` |
| `dockerfile/missing-healthcheck` | MINOR | `dockerfile/Dockerfile.app:absent`<br>`dockerfile/Dockerfile.builder:absent` |
| `dockerfile/missing-workdir` | MINOR | `dockerfile/Dockerfile.app:4` |
| `dockerfile/mutable-base` | MAJOR | `dockerfile/Dockerfile.builder:4` |
| `dockerfile/root-runtime` | MAJOR | `dockerfile/Dockerfile.app:24`<br>`dockerfile/Dockerfile.builder:13` |
| `dockerfile/single-stage-toolchain` | MAJOR | `dockerfile/Dockerfile.app:4` |
| `dockerfile/split-package-cleanup` | MAJOR | `dockerfile/Dockerfile.app:13-14` |
| `dockerfile/tls-disabled` | BLOCKER | `dockerfile/Dockerfile.app:20` |
| `dockerfile/unnamed-stage` | NIT | `dockerfile/Dockerfile.builder:11` |
| `dockerfile/unverified-artifact` | MAJOR | `dockerfile/Dockerfile.builder:19-21` |

## rust

| Review Rule | Severity | Required evidence |
|---|---|---|
| `rust/blocking-in-async` | BLOCKER | `rust/order_handler.rs:71-73` |
| `rust/clone-to-compile` | MINOR | `rust/user_service.rs:96-97, 109, 140` |
| `rust/discarded-result` | BLOCKER | `rust/order_handler.rs:81` |
| `rust/erased-public-error` | MAJOR | `rust/user_service.rs:17-24, 35, 79` |
| `rust/lock-across-await` | BLOCKER | `rust/order_handler.rs:62-66` |
| `rust/non-send-async-state` | MAJOR | `rust/non_send_future.rs:4-6, 10` |
| `rust/panic-in-library` | BLOCKER | `rust/order_handler.rs:11`<br>`rust/order_handler.rs:28, 31, 37, 67`<br>`rust/user_service.rs:75` |
| `rust/raw-domain-value` | NIT | `rust/user_service.rs:61, 62` |
| `rust/shared-mutex-overuse` | MINOR | `rust/user_service.rs:82` |
| `rust/stringly-typed-domain` | MAJOR | `rust/user_service.rs:31-52` |
| `rust/unsafe-without-safety` | BLOCKER | `rust/user_service.rs:130` |

## Summary

**Coverage: 79/79 Review Rules (100%)**
