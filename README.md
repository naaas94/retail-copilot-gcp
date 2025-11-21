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

## Setup & Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Generate Mock Data**:
    ```bash
    python scripts/generate_mock_data.py
    ```

3.  **Run the App**:
    ```bash
    streamlit run src/ui/app.py
    ```

4.  **Enter your API Key** in the sidebar.

## Features to Demo

1.  **Routing**: Ask "Should we lay off staff?" -> See it route to **Handoff**.
2.  **Safety**: Ask "DROP TABLE sales" -> See the **Validator** block it.
3.  **Planning**: Ask "Show sales by region" -> See the **Planner** generate a JSON plan.
4.  **Execution**: See the SQL generated and executed against the local DuckDB.
5.  **Traceability**: Expand the "Architect Trace" in the UI to see the raw JSON and costs.
