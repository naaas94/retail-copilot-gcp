---
noteId: "e0129260c5a311f0ac47819087bbe0ed"
tags: []

---

# Prompt Changelog
# Tracks semantic diffs and version history for all prompts

## Versioning Scheme
- Format: `{component}-{domain}-v{number}.md`
- Breaking changes increment major version (v1 → v2)
- Non-breaking improvements increment minor/patch

## Router v1 (2025-01-01)
- Initial release
- Routes: qa, sql, unsafe, handoff, clarify
- Deterministic routing with temperature=0.0
- Policy-based unsafe detection

## Planner v2 (2025-01-01)
- Added "viz_hint" block to align with VizSpec generation
- Introduced "needs_disambiguation" boolean gate
- Reduced max tokens to 350 to control latency
- Semantic diff from v1:
  - Slot coverage must include time role in dimensions
  - Disallow measures with unspecified units
  - Added "reasoning" field for traceability

## Generator QA v1 (2025-01-01)
- Initial release for grounded text generation
- Citation format: [S#] inline citations
- Faithfulness requirements: ≥90% citation coverage
- Max 180 tokens for concise answers

## SQL Emitter v1 (2025-01-01)
- Template-based SQL generation (not freeform)
- Enforces tenant_id filter
- Requires LIMIT clause
- Blocks DDL/DML operations

## Review Process
- Changes require approval from Solutions Architect
- Semantic diffs must be documented
- Golden set regression tests must pass before promotion
- Breaking changes require golden set update

