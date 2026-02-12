# CLI Demo Gap Analysis

**Repo:** `retail-copilot-gcp`  
**Scope:** What prevents a fully operational CLI demo (mock data, all components working, returning visualizations).

---

## 1. No CLI Entrypoint

- The only runnable surface is **Streamlit** (`src/ui/app.py`) via `make run` / `streamlit run src/ui/app.py`.
- There is **no CLI script** that runs the same pipeline (router → planner → SQL generator → validator → DuckDB) and prints or exports the result and trace.

**Needed:** A CLI entrypoint (e.g. `scripts/run_cli.py` or `src/cli.py`) that invokes the pipeline and prints (or exports) the result and trace.

---

## 2. Mandatory Real LLM (Gemini) in Three Places

- **Router** and **Planner** use `GeminiAdapter` and call the real API with `temperature=0.0`.
- **SQLGenerator** also uses the LLM to convert a `Plan` into SQL (no template path in the main app).
- **Config** requires `GOOGLE_API_KEY` (`GOOGLE_API_KEY: str` in `config.py` with no default), so the app does not start without it.

So the design is **not** “fully operational with mock data” in an offline sense: it depends on network and API key.

**Needed for a “mock data, no API” demo:** Either an **optional** API key and a **mock LLM adapter** that returns deterministic responses (e.g. from the golden set or canned JSON/SQL), or keep the real LLM and document that the CLI demo requires a key and network.

---

## 3. SQL Generation: Templates Not Wired

- The dossier and `sql/templates/` (e.g. `time_series_sales.sql`, `margin_by_category.sql`) describe a **template-based** path; `catalog/intents.yaml` maps intents to those templates.
- In the **actual app**, `SQLGenerator` uses the **LLM** to generate SQL from the plan (`app.py` ~95–101, `sql_generator.py`). The Jinja2 templates are **not** used in the main flow.

So “all components working” in the sense of a deterministic template path is only partially true: templates exist but are not in the pipeline. For a **deterministic CLI demo** you would either wire **Plan → intent → template → Jinja2**, or keep the LLM and accept non-determinism and API dependency.

---

## 4. Visualizations Are Streamlit-Only

- In `app.py` (lines 117–121), when the result has at least two columns and a numeric column, the app shows `st.bar_chart(...)`. There is no use of `Plan.viz_hint` to choose chart type.
- That logic is **tied to Streamlit**; there is no terminal or file-based visualization.

**Needed for “returning visualizations” in CLI:** Either **terminal visualization** (e.g. `rich`, `plotext`, or ASCII bar chart) from the same heuristic or from `viz_hint`, or **emit a spec** (e.g. JSON) and render elsewhere, or **write HTML/image** to disk and open it. Today, “returning visualizations” in a CLI sense does not exist.

---

## 5. Mock Data Is Present but Not Auto-Ensured

- `scripts/generate_mock_data.py` and `data/*.parquet` exist; the Streamlit app loads them in `get_components()` via DuckDB.
- So mock data **is** used; the gap is that the **CLI** does not exist to use it, and there is no “demo mode” that guarantees data exists (e.g. auto-run generator if `data/` is empty).

For a robust CLI demo you could add a check (e.g. “if no parquet files, run `generate_mock_data.py` or print clear instructions”).

---

## 6. Config and Startup Guard

- `Settings` requires `GOOGLE_API_KEY`. Streamlit also does `if not api_key: st.error(...); st.stop()`.
- Any entrypoint that uses `settings` or the same guard will **refuse to run** without a key. A CLI that should work with “mock only” would need either an optional key plus a mock LLM or a dedicated demo mode that does not require the key.

---

## 7. Golden Set `user_ctx` vs `SecurityContext`

- Golden files use `user_ctx` with `"tenant"`, `"role"`, `"region"` (e.g. `example_net_sales_001.json`), while `SecurityContext` expects `tenant_id`, `user_id`, `role`, `region`.
- The eval script passes the raw dict to `router.route()`; Pydantic may coerce or fail depending on content. This is not a CLI blocker per se, but worth aligning if you want the CLI to run golden-set-driven demos without errors.

---

## Summary Table

| Blocker | Current State | What’s Needed for a Full CLI Demo |
|--------|----------------|-----------------------------------|
| **CLI entrypoint** | None | Add a script that runs router → planner → SQL gen → validator → DuckDB and prints (or exports) result and trace. |
| **Offline / mock LLM** | Router, Planner, SQLGenerator all use real Gemini; API key required | Optional API key and a mock LLM adapter that returns deterministic RouterOutput / Plan / SQL, or accept “API required” for CLI. |
| **Visualizations** | Only `st.bar_chart` in Streamlit | Implement terminal or file-based viz (e.g. from first dimension + first numeric measure, or from `viz_hint`) for CLI. |
| **Mock data** | Present and loaded in app | Ensure CLI (or demo mode) uses the same data and optionally ensures it exists (e.g. run generator or document one-time step). |
| **Templates in pipeline** | Not used in main flow | Optional: wire intent → Jinja2 templates for a deterministic, no-LLM SQL path in the CLI. |

---

## Conclusion

What prevents a **fully operational CLI demo** with mock data and visualizations:

1. **No CLI entrypoint** to run the pipeline from the command line.
2. **No way to run without a real Gemini API key** (no mock LLM).
3. **No visualization path outside Streamlit** (no terminal or file-based viz).
4. **SQL generation in the app is LLM-based**, not template-based.

Mock data and DuckDB are already in place; the rest is wiring and a demo-mode / mock-LLM strategy.
