---
noteId: "2d993890c5a411f0ac47819087bbe0ed"
tags: []

---

# Changelog
# All notable changes to the Retail Copilot architecture and scaffolding

## [Unreleased]

### Added
- Initial repository structure with spec-first architecture
- Catalog definitions (intents, glossary, policies)
- Prompt templates (router, planner, generator, SQL emitter)
- SQL templates and validation policies
- Golden set examples and unit test scaffolds
- Operations documentation (runbook, monitoring, gates)

## [1.0.0] - 2025-01-01

### Added
- **Catalog**:
  - `catalog/intents.yaml`: Intent taxonomy with 4 core intents (net_sales, margin_by_category, inventory_turnover, avg_ticket)
  - `catalog/glossary.md`: Business glossary mapping terms to schema, units, synonyms
  - `catalog/policies.yaml`: Tenant-aware policies, query limits, cost controls, promotion gates

- **Prompts**:
  - `prompts/router-retail-v1.md`: Query routing with policy enforcement
  - `prompts/planner-retail-v2.md`: NL → structured plan with glossary grounding
  - `prompts/generator-qa-grounded-v1.md`: Text generation with citations
  - `prompts/sql-emitter-retail-v1.md`: Template-based SQL generation

- **SQL**:
  - `sql/templates/time_series_sales.sql`: Time series sales query template
  - `sql/templates/margin_by_category.sql`: Margin by category template
  - `sql/sql_policies.yaml`: SQL validation rules and guardrails

- **Evaluation**:
  - `eval/golden_set/example_net_sales_001.json`: Canonical net sales test case
  - `eval/golden_set/example_margin_001.json`: Canonical margin test case
  - `eval/golden_set/example_disambiguation_001.json`: Disambiguation test case

- **Tests**:
  - `tests/test_router.py`: Router unit tests
  - `tests/test_planner.py`: Planner unit tests
  - `tests/test_sql_lints.py`: SQL validation tests

- **Operations**:
  - `ops/runbook.md`: Incident response and troubleshooting procedures
  - `ops/monitoring_dashboards.json`: Dashboard definitions for metrics
  - `ops/gates.yaml`: Promotion gate configuration

### Documentation
- `README.md`: Architecture overview and component descriptions
- `CHANGELOG.md`: Version history (this file)

## Future Enhancements

### Planned
- Additional SQL templates (inventory_turnover, avg_ticket)
- Expanded golden set with more paraphrases and edge cases
- RAG components (semantic catalog, embedding space, retrieval pipeline)
- Visualization spec examples and schema
- CI/CD pipeline scripts (aggregate_eval.py, check_gates.py)
- Terraform infrastructure as code
- Vertex AI Pipeline definitions for batch evaluation

### Considerations
- Multi-tenant isolation implementation details
- Looker integration for VizSpec rendering
- Cost optimization strategies
- A/B testing framework for prompt/template variants
- Drift detection and retraining triggers

