# Review Rule Coverage

Generated from the inline Review Rule catalogs and Conformance Fixtures.
Run `uv run tests/scripts/sync_generated.py` after changing either.

## common

| Review Rule | Severity | Required evidence |
|---|---|---|
| `common/anemic-domain` | MAJOR | `go/user_service.go:55-63`<br>`java/PaymentService.java:184-194`<br>`python/user_management.py:72-80`<br>`rust/user_service.rs:53-60`<br>`typescript/notification-service.ts:183-191` |
| `common/authorization-gap` | MAJOR | `go/user_service.go:184-185`<br>`java/PaymentService.java:200`<br>`python/user_management.py:195-197`<br>`typescript/notification-service.ts:170` |
| `common/blocking-in-async` | BLOCKER | `python/order_service.py:90-93` |
| `common/circular-dependency` | MAJOR | `typescript/architecture-gaps.ts:1` |
| `common/command-injection` | BLOCKER | `go/user_service.go:170-171`<br>`java/PaymentService.java:201`<br>`python/user_management.py:177-182`<br>`rust/order_handler.rs:25-27` |
| `common/complex-construction` | MAJOR | `java/PaymentService.java:58-61` |
| `common/coupled-side-effect` | MAJOR | `typescript/architecture-gaps.ts:29-33` |
| `common/critical-change-risk` | MAJOR | `go/rate_limiter.go:45-73`<br>`python/pricing_engine.py:42-66` |
| `common/dead-code` | MINOR | `go/user_service.go:163-165`<br>`java/PaymentService.java:155`<br>`python/user_management.py:166-171`<br>`rust/user_service.rs:131-133`<br>`typescript/notification-service.ts:141`<br>`typescript/notification-service.ts:163-166` |
| `common/deep-nesting` | MINOR | `go/user_service.go:111-120`<br>`java/PaymentService.java:72-82`<br>`python/user_management.py:114-121`<br>`rust/user_service.rs:96-108`<br>`typescript/notification-service.ts:58-88` |
| `common/dependency-inversion` | MAJOR | `java/OrderController.java:42-46`<br>`rust/user_service.rs:137-139`<br>`typescript/order-service.ts:15-16` |
| `common/duplicated-logic` | MINOR | `go/user_service.go:131-139`<br>`go/user_service.go:155`<br>`java/PaymentService.java:150`<br>`python/user_management.py:130-139`<br>`python/user_management.py:160`<br>`typescript/notification-service.ts:62-65, 71-74, 82-85, 90-93, 95-98` |
| `common/eager-loading` | MAJOR | `typescript/architecture-gaps.ts:16-23` |
| `common/elevated-change-risk` | MINOR | `go/rate_limiter.go:33-42`<br>`python/pricing_engine.py:85-91` |
| `common/erased-failure` | MINOR | `rust/order_handler.rs:69-71` |
| `common/excess-complexity` | MINOR | `python/pricing_engine.py:69-82` |
| `common/framework-coupling` | MAJOR | `java/OrderController.java:39`<br>`typescript/architecture-gaps.ts:2, 9` |
| `common/god-module` | MAJOR | `go/order_handler.go:19-22`<br>`java/OrderController.java:21`<br>`python/order_service.py:33`<br>`rust/order_handler.rs:69-77`<br>`typescript/order-service.ts:13` |
| `common/graceful-shutdown` | NIT | `go/order_handler.go:120-125` |
| `common/hard-coded-dependency` | MAJOR | `go/user_service.go:95-96`<br>`java/PaymentService.java:136`<br>`python/user_management.py:107-108`<br>`rust/user_service.rs:67, 82`<br>`typescript/notification-service.ts:130-132`<br>`typescript/notification-service.ts:62, 71, 82, 90, 95` |
| `common/hidden-side-effect` | MAJOR | `go/user_service.go:77-79`<br>`java/PaymentService.java:104, 116-118`<br>`python/user_management.py:94-95, 98-99`<br>`rust/user_service.rs:65-71`<br>`typescript/notification-service.ts:105, 115-117` |
| `common/hot-path-allocation` | MINOR | `rust/order_handler.rs:48` |
| `common/ignored-error` | BLOCKER | `go/order_handler.go:38`<br>`go/order_handler.go:41`<br>`go/order_handler.go:81`<br>`go/order_handler.go:84`<br>`go/order_handler.go:107`<br>`go/user_service.go:101`<br>`go/user_service.go:127`<br>`java/PaymentService.java:119-121`<br>`python/order_service.py:47-48`<br>`typescript/order-service.ts:40` |
| `common/imperative-transformation` | MINOR | `typescript/order-service.ts:59-66` |
| `common/incomplete-error-handling` | MINOR | `go/order_handler.go:29-31`<br>`go/order_handler.go:114`<br>`java/OrderController.java:76`<br>`java/OrderController.java:99`<br>`java/OrderController.java:58`<br>`java/PaymentService.java:138`<br>`python/order_service.py:22, 88`<br>`typescript/order-service.ts:73` |
| `common/inefficient-data-structure` | MINOR | `typescript/architecture-gaps.ts:25-27` |
| `common/insecure-default` | MAJOR | `typescript/architecture-gaps.ts:10` |
| `common/interface-segregation` | MAJOR | `go/user_service.go:18-27`<br>`java/PaymentService.java:14-22`<br>`python/user_management.py:14-30`<br>`rust/user_service.rs:13-22`<br>`typescript/notification-service.ts:13-21`<br>`typescript/order-service.ts:26` |
| `common/language-idiom` | NIT | `go/order_handler.go:30, 114`<br>`go/user_service.go:34-46`<br>`java/OrderController.java:13-34`<br>`java/OrderController.java:96`<br>`python/order_service.py:95`<br>`python/order_service.py:90-95`<br>`typescript/order-service.ts:75-78` |
| `common/layer-violation` | MAJOR | `typescript/notification-service.ts:8-9` |
| `common/liskov-violation` | MAJOR | `java/PaymentService.java:44-46`<br>`python/user_management.py:47-50`<br>`typescript/notification-service.ts:37-50` |
| `common/magic-literal` | MINOR | `java/PaymentService.java:107`<br>`python/order_service.py:51`<br>`rust/order_handler.rs:87`<br>`typescript/order-service.ts:36` |
| `common/missing-abstraction` | MAJOR | `typescript/architecture-gaps.ts:46-54` |
| `common/missing-cache` | MINOR | `typescript/architecture-gaps.ts:35-44` |
| `common/missing-input-validation` | MAJOR | `java/OrderController.java:58`<br>`python/order_service.py:33` |
| `common/missing-timeout` | MINOR | `go/order_handler.go:110-111`<br>`java/OrderController.java:101-102, 106, 108`<br>`python/order_service.py:90-93` |
| `common/mixed-abstraction` | MINOR | `go/user_service.go:126-148`<br>`java/PaymentService.java:145-162`<br>`python/user_management.py:125`<br>`typescript/notification-service.ts:135-146` |
| `common/n-plus-one-query` | MAJOR | `go/order_handler.go:84-86`<br>`python/order_service.py:65-68`<br>`rust/order_handler.rs:42-46` |
| `common/nondeterministic-dependency` | MAJOR | `go/user_service.go:91`<br>`java/PaymentService.java:129`<br>`python/user_management.py:116`<br>`typescript/notification-service.ts:125-127` |
| `common/open-closed-violation` | MAJOR | `go/user_service.go:32-49`<br>`java/PaymentService.java:69-97`<br>`python/user_management.py:55-65`<br>`rust/user_service.rs:46`<br>`typescript/notification-service.ts:56-101` |
| `common/path-traversal` | BLOCKER | `go/user_service.go:180`<br>`python/user_management.py:189-191`<br>`rust/order_handler.rs:35`<br>`typescript/notification-service.ts:174` |
| `common/private-logic` | MINOR | `typescript/architecture-gaps.ts:61-65` |
| `common/resource-leak` | BLOCKER | `go/order_handler.go:70`<br>`java/PaymentService.java:116-118` |
| `common/sensitive-data-exposure` | MINOR | `go/order_handler.go:72`<br>`java/PaymentService.java:79`<br>`rust/order_handler.rs:81` |
| `common/shared-mutable-state` | MAJOR | `go/order_handler.go:35`<br>`java/OrderController.java:49`<br>`python/order_service.py:13`<br>`typescript/order-service.ts:9` |
| `common/sql-injection` | BLOCKER | `go/order_handler.go:44-49`<br>`go/order_handler.go:85`<br>`java/OrderController.java:62-68`<br>`java/OrderController.java:87-88`<br>`python/order_service.py:37-41`<br>`python/order_service.py:81-83`<br>`python/order_service.py:67`<br>`rust/order_handler.rs:9`<br>`rust/order_handler.rs:17`<br>`typescript/order-service.ts:30-33`<br>`typescript/order-service.ts:53-56` |
| `common/style-naming` | NIT | `typescript/order-service.ts:13` |
| `common/style-readability` | NIT | `typescript/architecture-gaps.ts:68-70` |
| `common/unbounded-query` | MAJOR | `go/order_handler.go:70`<br>`java/OrderController.java:54`<br>`python/order_service.py:61`<br>`rust/order_handler.rs:17-19`<br>`typescript/order-service.ts:21` |
| `common/unclear-name` | MINOR | `go/user_service.go:151-153`<br>`java/PaymentService.java:167, 169-173`<br>`python/user_management.py:153-162`<br>`rust/user_service.rs:120-128`<br>`typescript/notification-service.ts:151-153` |
| `common/unhandled-variant` | MAJOR | `go/user_service.go:32-50`<br>`python/user_management.py:55-65` |
| `common/unmanaged-concurrency` | MAJOR | `go/order_handler.go:63`<br>`go/order_handler.go:25, 106` |
| `common/unnecessary-mutation` | MAJOR | `python/order_service.py:16` |
| `common/unsafe-deserialization` | BLOCKER | `typescript/architecture-gaps.ts:12-14` |
| `common/weak-type-model` | MAJOR | `go/order_handler.go:36, 106`<br>`go/user_service.go:59-60`<br>`java/OrderController.java:13, 58, 81`<br>`java/OrderController.java:49, 52`<br>`java/PaymentService.java:186, 189`<br>`java/PaymentService.java:187`<br>`python/user_management.py:73`<br>`typescript/notification-service.ts:185, 190`<br>`typescript/order-service.ts:9, 26, 51, 59, 71` |
| `common/xss` | BLOCKER | `typescript/notification-service.ts:177-178` |

## dockerfile

| Review Rule | Severity | Required evidence |
|---|---|---|
| `dockerfile/baked-secret` | BLOCKER | `dockerfile/Dockerfile.app:10` |
| `dockerfile/broad-stage-copy` | MAJOR | `dockerfile/Dockerfile.builder:19` |
| `dockerfile/cache-hostile-copy` | MINOR | `dockerfile/Dockerfile.app:18-19` |
| `dockerfile/confused-build-runtime-config` | MINOR | `dockerfile/Dockerfile.builder:22-23` |
| `dockerfile/implicit-add` | MINOR | `dockerfile/Dockerfile.app:22` |
| `dockerfile/latest-base` | BLOCKER | `dockerfile/Dockerfile.app:5` |
| `dockerfile/missing-healthcheck` | MINOR | `dockerfile/Dockerfile.app:absent`<br>`dockerfile/Dockerfile.builder:absent` |
| `dockerfile/missing-workdir` | MINOR | `dockerfile/Dockerfile.app:5, 18` |
| `dockerfile/mutable-base` | MAJOR | `dockerfile/Dockerfile.builder:5, 12` |
| `dockerfile/root-runtime` | MAJOR | `dockerfile/Dockerfile.app:31`<br>`dockerfile/Dockerfile.builder:34` |
| `dockerfile/single-stage-toolchain` | MAJOR | `dockerfile/Dockerfile.app:5, 14` |
| `dockerfile/split-package-cleanup` | MAJOR | `dockerfile/Dockerfile.app:14-15` |
| `dockerfile/tls-disabled` | BLOCKER | `dockerfile/Dockerfile.app:25` |
| `dockerfile/unnamed-stage` | NIT | `dockerfile/Dockerfile.builder:12` |
| `dockerfile/unverified-artifact` | MAJOR | `dockerfile/Dockerfile.builder:26-28` |

## rust

| Review Rule | Severity | Required evidence |
|---|---|---|
| `rust/blocking-in-async` | BLOCKER | `rust/order_handler.rs:65` |
| `rust/clone-to-compile` | MINOR | `rust/user_service.rs:90, 101, 124` |
| `rust/discarded-result` | BLOCKER | `rust/order_handler.rs:73` |
| `rust/erased-public-error` | MAJOR | `rust/user_service.rs:16-21, 27, 81, 137` |
| `rust/lock-across-await` | BLOCKER | `rust/order_handler.rs:57-60` |
| `rust/non-send-async-state` | MAJOR | `rust/non_send_future.rs:4-6, 10` |
| `rust/panic-in-library` | BLOCKER | `rust/order_handler.rs:11`<br>`rust/order_handler.rs:29, 30, 36, 74`<br>`rust/user_service.rs:69` |
| `rust/raw-domain-value` | NIT | `rust/user_service.rs:57, 58` |
| `rust/shared-mutex-overuse` | MINOR | `rust/user_service.rs:76` |
| `rust/stringly-typed-domain` | MAJOR | `rust/user_service.rs:27-48` |
| `rust/unsafe-without-safety` | BLOCKER | `rust/user_service.rs:116` |

## Summary

**Coverage: 82/82 Review Rules (100%)**
