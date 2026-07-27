# Code Review

This context defines the review knowledge distributed by the installable skill and
the evidence used in this repository to verify that knowledge.

## Language

**Review Rule**:
A canonical statement of review knowledge, identified independently of its wording
or position, with one severity. Different merge impact means a different rule
identity. A rule shared by languages has one identity; behavior unique to a language
has its own rule. Review Rules belong to the installable skill artifact.
_Avoid_: Check, guideline, principle

**Language Reference**:
Language-specific detection and remediation knowledge for shared Review Rules,
plus Review Rules unique to that language. Each Language Reference is an adapter
within the installable skill artifact.
_Avoid_: Language guide, rules file

**Review Finding**:
An observed violation of a Review Rule at a specific location in reviewed input.
_Avoid_: Issue, warning

**Conformance Fixture**:
Reviewed input paired with required Review Findings and, where evidence warrants
it, forbidden Review Findings. Findings not named in either set remain allowed.
_Avoid_: Sample, test case

**Review Conformance**:
Evidence that the skill produces the expected Review Findings for its Conformance
Fixtures and that every claimed Review Rule is covered. Additional Review Findings
do not invalidate conformance.
_Avoid_: Review accuracy, structural validation

**Conformance Run**:
Review Conformance evidence produced by one explicitly identified runtime and
model. A Conformance Run does not certify other compatible runtimes.
_Avoid_: Universal conformance, skill certification
