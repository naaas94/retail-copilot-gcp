# Retail Copilot (local proof of concept)

This repository is a **local-first** implementation of a retail analytics copilot: it runs entirely on your machine, uses **DuckDB** instead of a cloud warehouse, and calls **Google Gemini** where the pipeline needs a language model. It is intended for **development, demonstration, and evaluation** of the cognitive flow (routing → planning → SQL generation and validation), not as a drop-in replacement for a full GCP-hosted product.

**What you get:** a modular Python service with a Streamlit UI, prompt-driven router and planner, SQL linting and safety checks, mock retail data generation, a small golden-set evaluation script, and unit tests. **What you do not get:** managed identity, BigQuery, or production operations; those remain out of scope here by design.

---

## Repository layout

The code follows a **modular monolith** with explicit boundaries: core logic does not import concrete SDKs; adapters implement interfaces.

```
src/
├── core/                 # Domain logic (no UI, no vendor SDKs in contracts)
│   ├── router.py         # Classifies user input (e.g. QA vs SQL vs handoff)
│   ├── planner.py        # Produces structured plans from routed intent
│   ├── sql_generator.py  # Plan → SQL
│   ├── validator.py      # Safety checks (e.g. blocking DDL)
│   ├── types.py          # Shared models
│   ├── config.py         # Settings (env / .env)
│   ├── context.py        # Tenant / security context
│   └── utils.py          # Prompt loading and helpers
├── interfaces/           # Protocols (LLM, database)
│   ├── llm.py
│   └── db.py
├── adapters/             # Gemini (LLM) and DuckDB (warehouse)
│   ├── gemini.py
│   └── duckdb_adapter.py
└── ui/
    └── app.py            # Streamlit entrypoint
```

Prompts and catalog artifacts live under `prompts/` and `catalog/`; evaluation fixtures under `eval/golden_set/`. Operational reference material is under `ops/` and `docs/` for readers who need broader context.

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| Python 3.10+ | As used by dependencies in `requirements.txt` |
| Google Gemini API key | Required for LLM-backed paths in the UI and for `make eval`. Obtain a key from [Google AI Studio](https://aistudio.google.com/app/apikey). |
| Environment file | Copy `.env.example` to `.env` and set `GOOGLE_API_KEY` (and optional variables such as `LLM_MODEL`, `DUCKDB_PATH`). |

---

## Run with Docker Compose

Reproducible local run with the app exposed on port 8501:

```bash
cp .env.example .env
# Edit .env: set GOOGLE_API_KEY

docker-compose up --build
```

Open `http://localhost:8501` in a browser.

---

## Run without Docker

1. Install dependencies:

   ```bash
   make install
   ```

2. Generate mock DuckDB data (if you have not already):

   ```bash
   python scripts/generate_mock_data.py
   ```

3. Start the UI:

   ```bash
   make run
   ```

---

## Tests and CI

```bash
make test
```

Runs `pytest` on `tests/`. A GitHub Actions workflow in `.github/workflows/ci.yml` runs the same command on pushes and pull requests targeting the `main` branch (Python 3.11 and 3.12).

---

## Golden-set evaluation

```bash
make eval
```

This invokes `scripts/evaluate_golden_set.py`, which loads JSON cases from `eval/golden_set/`, runs them through the **Router** and **Planner**, and compares outputs to expected routes and intents. **If `GOOGLE_API_KEY` is unset, the script prints a message and exits without calling the API**—configure `.env` first for a meaningful run.

---

## Suggested scenarios in the UI

These examples illustrate behavior described in the code paths above; exact wording may need to match your prompts and catalog.

1. **Routing / policy:** sensitive or out-of-scope questions (e.g. operational HR) should route toward handoff or a non-SQL path rather than executing analytics SQL.
2. **Safety:** destructive or DDL-style requests (e.g. dropping tables) should be rejected by validation, not executed.
3. **Planning:** analytical questions (e.g. sales by region) should yield a structured plan before SQL is considered.
4. **Tenant context:** the UI surfaces security context so you can see how tenant-scoped behavior is wired.
5. **Traceability:** expand trace or debug sections in the UI to inspect intermediate JSON and usage where implemented.

---

## License and status

Treat this tree as an **engineering demonstration**: APIs, prompts, and evaluation sets evolve with the product spec. For release-level history, see `CHANGELOG.md`.
