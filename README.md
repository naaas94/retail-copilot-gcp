---
noteId: "2b91cfd0c5a411f0ac47819087bbe0ed"
tags: []

---

# Retail Analytics Copilot - Architecture & Scaffolding

Architecture + scaffolding for a Retail Analytics Copilot on GCP that turns natural language into validated SQL + VizSpec JSON over BigQuery. This repo mirrors the structure of a challenge dossier I delivered: problem framing, system design, NL→SQL, guardrails, MLOps, tenancy.

## Architecture Overview

The system follows a **spec-first, not a running product** approach. The architecture is designed as a multi-stage pipeline:

```
User Query
  ↓
API Gateway (AuthZ, rate limits)
  ↓
Router (classify: qa/sql/unsafe/handoff/clarify)
  ↓
Planner (NL → intent + slots + SQL template selection)
  ↓
SQL Validator (allowlist, tenant filters, cost checks)
  ↓
BigQuery (execution with RLS/CLS)
  ↓
Answer Assembler (SQL provenance + VizSpec JSON)
  ↓
Response (streamed to user)
```

**Key Design Principles:**
- **Spec-first**: This repository contains specifications, prompts, templates, and test scaffolds—not a running implementation.
- **Safety-first**: Multiple layers of validation (SQL linting, allowlists, cost controls, tenant isolation).
- **Observable**: Every answer emits a trace bundle for replayability.
- **Testable**: Golden set evaluation with automated promotion gates.

## Key Components

### `catalog/` – Intent taxonomy, golden-set scaffolds, business glossary
- **`intents.yaml`**: Canonical intent definitions (net_sales, margin_by_category, inventory_turnover, avg_ticket) with measures, dimensions, filters, and SQL template mappings.
- **`glossary.md`**: Business terms → database schema mappings (tables/columns), units, synonyms, ambiguity notes.
- **`policies.yaml`**: Tenant-aware guardrails, query limits, allowed tables/columns, cost controls, PII policies, promotion gates.

### `prompts/` – Router, planner, generator, SQL emitter prompts + changelog
- **`router-retail-v1.md`**: Routes queries to qa/sql/unsafe/handoff/clarify with policy enforcement.
- **`planner-retail-v2.md`**: Converts NL → structured plan (intent, measures, dimensions, filters, time_window, viz_hint).
- **`generator-qa-grounded-v1.md`**: Generates text answers from retrieved evidence with citations.
- **`sql-emitter-retail-v1.md`**: Fills SQL template slots from plan JSON (template-based, not freeform).
- **`CHANGELOG.md`**: Version history and semantic diffs for prompt changes.

### `sql/` – Templates per intent, plus validator policies
- **`templates/`**: Parameterized SQL templates (Jinja2-style `{{placeholders}}`) for each intent:
  - `time_series_sales.sql`: Net sales time series queries
  - `margin_by_category.sql`: Margin breakdown by category
- **`sql_policies.yaml`**: SQL validation rules (allowed/denied operations, schema allowlist, complexity limits, cost controls).

### `eval/` – Examples of golden-set cases and unit tests for router/planner/SQL/viz
- **`golden_set/`**: Curated test cases with:
  - Canonical phrasing examples
  - Paraphrase variants
  - Adversarial/edge cases
  - Expected outputs (route, plan, SQL structure, viz_spec)
  - Validation criteria (schema, accuracy thresholds)

### `tests/` – Unit tests for components
- **`test_router.py`**: Router determinism, schema validation, policy enforcement, golden set coverage.
- **`test_planner.py`**: Planner JSON schema validation, slot coverage, glossary grounding, disambiguation triggers.
- **`test_sql_lints.py`**: SQL validation (DDL/DML blocking, allowlist enforcement, tenant filters, budget checks).

### `ops/` – Runbook, monitoring surfaces, promotion gates, SLOs
- **`runbook.md`**: Incident response procedures (P0-P3), troubleshooting, deployment/rollback procedures, maintenance tasks.
- **`monitoring_dashboards.json`**: Dashboard definitions for performance (latency, error rate), quality (faithfulness, golden set pass rate), usage (queries per day, cost per answer).
- **`gates.yaml`**: Promotion gate configuration (quality thresholds, performance SLOs, cost limits, rollback triggers, canary deployment rules).

## How to Read / Evaluate This Repo

1. **Start with `docs/dossier.pdf` (or README) for architecture.**
   - Understand the overall flow: API → Router → Planner → Validator → BigQuery → Answer Assembler.
   - Review the tenancy model (dataset-per-tenant, RLS/CLS, service account impersonation).

2. **Then inspect `catalog/` + `prompts/` to see how NL→SQL is grounded.**
   - `catalog/intents.yaml`: See how business questions map to intents and SQL templates.
   - `catalog/glossary.md`: Understand how terms like "margin" or "net sales" map to tables/columns.
   - `prompts/planner-retail-v2.md`: See how the planner converts NL → structured plan with glossary grounding.

3. **Look at `eval/tests` + `ops/gates.yaml` for how I'd enforce promotions.**
   - `eval/golden_set/*.json`: Example test cases with expected outputs.
   - `tests/test_*.py`: Unit tests for router, planner, SQL validation.
   - `ops/gates.yaml`: Promotion gate thresholds (80% golden set pass, p95 < 2s, cost < $0.01/query).

