# Prompts

This directory contains the system prompts used by the Retail Copilot.

## Versioning Strategy

Prompts are versioned by filename to ensure reproducibility and allow for A/B testing.
Format: `{component}-retail-v{version}.md`

## Active Prompts

- `router-retail-v1.md`: Used by the Router to classify user queries.
- `planner-retail-v2.md`: Used by the Planner to generate data retrieval plans.

## Deprecated Prompts

(None currently)

## How to Update

1. Create a new file with incremented version number (e.g., `router-retail-v2.md`).
2. Update `src/core/config.py` or the component loader to use the new version.
3. Run evaluation suite to verify performance improvements.
