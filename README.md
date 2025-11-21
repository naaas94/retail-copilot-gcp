# Retail Copilot (OSS Demo)

This is a **local-first** implementation of the Retail Copilot architecture, designed to demonstrate the core logic without requiring a GCP account.

## Architecture

It follows a **Modular Monolith** design with strict separation of concerns:

```
src/
├── core/             # PURE BUSINESS LOGIC
│   ├── router.py     # Decision logic (QA vs SQL vs Unsafe)
│   ├── planner.py    # Plan generation logic
│   ├── sql_generator.py # Plan -> SQL conversion
│   └── validator.py  # Safety checks (No DDL, etc.)
├── interfaces/       # PROTOCOLS (The "Architect" layer)
│   ├── llm.py        # LLMClient Protocol
│   └── db.py         # DatabaseClient Protocol
├── adapters/         # CONCRETE IMPLEMENTATIONS
│   ├── gemini.py     # Adapter for Google Gemini API
│   └── duckdb.py     # Adapter for DuckDB (Simulates BigQuery)
└── ui/
    └── app.py        # Streamlit Entrypoint
```

## Prerequisites

1.  **Python 3.10+**
2.  **Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/app/apikey))

## Quick Start (Docker)

The easiest way to run the application is via Docker Compose:

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 2. Run with Docker
docker-compose up --build
```

Access the app at `http://localhost:8501`.

## Developer Setup (Local)

1.  **Install Dependencies**:
    ```bash
    make install
    ```

2.  **Generate Mock Data**:
    ```bash
    python scripts/generate_mock_data.py
    ```

3.  **Run the App**:
    ```bash
    make run
    ```

## MLOps & Evaluation

This repository includes a systematic evaluation framework to validate the cognitive architecture against a "Golden Set" of test cases.

```bash
# Run the evaluation suite
make eval
```

This runs `scripts/evaluate_golden_set.py`, which:
1.  Loads test cases from `eval/golden_set/`.
2.  Runs each case through the **Router** and **Planner**.
3.  Compares the output against expected results (Route accuracy, Intent accuracy).
4.  Outputs a pass/fail report.

## Features to Demo

1.  **Routing**: Ask "Should we lay off staff?" -> See it route to **Handoff**.
2.  **Safety**: Ask "DROP TABLE sales" -> See the **Validator** block it.
3.  **Planning**: Ask "Show sales by region" -> See the **Planner** generate a JSON plan.
4.  **Multi-Tenancy**: See the `SecurityContext` in the sidebar enforcing tenant isolation.
5.  **Traceability**: Expand the "Architect Trace" in the UI to see the raw JSON and costs.

