# ADR-0008: Judge conformance by recall over repeated runs

Date: 2026-10-03

## Status

Accepted

## Decision

A change to the skill is judged by recall, meaning required findings found
over required findings expected, summed over at least three live runs on the
same model. `run_conformance.py --summarize` reports it overall and per rule.
It also separates systematic misses (never found in any run) from flaky
expectations (found in some runs). Forbidden findings and severity drift must
stay at zero.

When a change to the skill is measured, the fixtures stay frozen. When
fixtures do change, saved runs are re-scored against the new fixtures. That
way the before and after figures always share one set of expectations.

A fixture expectation changes only for a reason the repository can show, in
one of four ways:

- **Widen**: the reviewer reported the same rule at another genuine instance
  of the same issue, such as a call site instead of the import.
- **Remap**: judged against the catalog's one-line definitions, another rule
  plainly fits the code better.
- **Drop**: the code does not show the issue. Every rule must keep at least
  one required finding somewhere.
- **Keep**: the issue is real and the rule is right, so the miss stays as
  signal.

A systematic miss for a rule that fits the code is fixed in the skill, with a
trigger or a named rule. The expectation is never rewritten for it.

## Considered Options

- Fixture pass rate as the headline was rejected. One miss fails a fixture of
  twenty expectations, so the figure mostly measures fixture size. Every
  focused fixture passed while every multi-issue fixture failed.
- Judging from a single run was rejected. Recall varied by about four hits
  between runs of the same commit, so one run cannot tell a flaky miss from a
  systematic one.
- Letting an expectation accept either of two rules was rejected. It raises
  recall by blurring rule boundaries instead of making the reviewer choose
  better.
- Splitting the multi-issue fixtures into single-issue ones was rejected. It
  would remove most flakiness, but each run would cost two to three times as
  much, and it would test a less realistic input than a diff with many
  defects.

## Consequences

Each measured step costs about six dollars for three sonnet runs. Saved runs
live in the git-ignored `conformance-runs/`. About five percent of
expectations stay flaky, which leaves a practical recall ceiling of about 92
to 94 percent. Beyond that, gains would come from fitting fixtures to one
model's choices, which this decision forbids.

## Amendment (2026-10-04)

The run-to-run variation was larger than this decision assumed. Two 3-run
sets on identical model inputs (`377e61d` re-scored, and `36da1df`) scored
600 and 594 of 642 required findings, a gap of 6 hits (about 1%). Within
each set, single runs varied by up to 5 hits. One expectation that had been
missed in three sets in a row (Go's `CreateOrder` god function) was then
found, and three expectations that had been flaky were missed in all three
runs of the new set.

Two thresholds follow:

- A difference of less than about 1% of required findings between two 3-run
  sets is noise. Changes that move recall by less than that need more runs
  before they count as gains or regressions.
- An expectation counts as a systematic miss only after six runs without a
  hit. Missing it in three runs makes it a candidate for investigation, not
  evidence for a skill or fixture change.

Pooling every run made on the same model inputs gives the best estimate of
current recall. For `36da1df` that is 1194 of 1284 (93.0%).

## Amendment (2026-10-04, model comparison)

The ceiling stated under Consequences was too low. After the expectations
that the code did not support were dropped, Sonnet 5.5 reached 94.5% over six
runs, Opus 5.5 96.7% over three, and Fable 5.1 97.2% over three. The ceiling
depends on the model, so it is not a property of the suite.

Above about 97% the suite stops telling models apart. Fable's lead over Opus
was 3 of 633 expectations, which is inside the 1% noise threshold. The
remaining misses are mostly flaky expectations that any model finds in some
runs. The suite also scores only pre-listed findings, so a model gets no
credit for a correct finding nobody expected. Fable's report of a real bug in
the `queue_drain.go` fixture is an example.
