import sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]  # project root
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import streamlit as st
import pandas as pd
import time
import os
from src.core.router import Router
from src.core.planner import Planner
from src.core.validator import Validator
from src.core.utils import PromptLoader
from src.adapters.gemini import GeminiAdapter
from src.adapters.duckdb_adapter import DuckDBAdapter
from src.core.sql_generator import SQLGenerator

from src.core.config import settings
from src.core.context import get_mock_context

# Page Config
st.set_page_config(page_title=settings.APP_NAME, layout="wide")

# Sidebar - Configuration
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=settings.GOOGLE_API_KEY or "")

if not api_key:
    st.error("Please provide a Gemini API Key in the sidebar or .env file.")
    st.stop()

# Mock Context (Simulating Middleware)
user_ctx = get_mock_context(role="admin")
st.sidebar.markdown(f"**User Context**:\n- Tenant: `{user_ctx.tenant_id}`\n- Role: `{user_ctx.role}`")

# Initialize Components (Singleton-ish)
@st.cache_resource
def get_components(key):
    llm = GeminiAdapter(api_key=key)
    loader = PromptLoader("prompts")
    router = Router(llm, loader)
    planner = Planner(llm, loader)
    validator = Validator()
    sql_generator = SQLGenerator(llm)
    db = DuckDBAdapter()
    
    # Load data
    db.load_parquet("fct_sales", "data/fct_sales.parquet")
    db.load_parquet("dim_product", "data/dim_product.parquet")
    db.load_parquet("dim_store", "data/dim_store.parquet")
    
    return router, planner, validator, db, sql_generator

router, planner, validator, db, sql_generator = get_components(api_key)

# Main UI
st.title("🛒 Retail Analytics Copilot")
st.markdown("### Ask questions about Sales, Products, and Stores.")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "trace" in message:
            with st.expander("🔍 Architect Trace (Debug)"):
                st.json(message["trace"])
        if "data" in message:
            st.dataframe(message["data"])

if prompt := st.chat_input("Ex: Show top 5 products by sales in Q3"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        trace_data = {"steps": []}

        try:
            # 1. Router
            with st.status("Thinking...", expanded=True) as status:
                st.write("Routing query...")
                route_out = router.route(prompt, user_ctx=user_ctx)
                trace_data["router"] = route_out.model_dump()
                
                if route_out.route == "sql":
                    st.write("Generating Plan...")
                    plan_out = planner.plan(prompt, user_ctx=user_ctx)
                    trace_data["plan"] = plan_out.model_dump()
                    
                    if plan_out.needs_disambiguation:
                        full_response = f"**Clarification Needed:** {plan_out.reasoning}"
                        status.update(label="Needs Clarification", state="complete")
                    else:
                        st.write("Generating SQL...")
                        # Simple Template Filling (Mocking the SQL Emitter for speed)
                        # In a real app, we'd use the sql-emitter prompt.
                        # Here we do a quick heuristic generation for the demo to work without 4 LLM calls.
                        # We'll just ask the LLM to write the SQL directly based on the plan for this PoC.
                        
                        st.write("Generating SQL...")
                        sql = sql_generator.generate_sql(plan_out)
                        trace_data["sql_generated"] = sql
                        
                        st.write("Validating SQL...")
                        validator.validate(sql, tenant_id=user_ctx.tenant_id)
                        
                        st.write("Executing Query...")
                        df = db.execute_query(sql)
                        trace_data["rows_returned"] = len(df)
                        
                        full_response = f"Here is the data based on your request."
                        status.update(label="Complete", state="complete")
                        
                        st.markdown(full_response)
                        st.dataframe(df)
                        
                        # Simple Viz
                        if not df.empty and len(df.columns) >= 2:
                            numeric_cols = df.select_dtypes(include=['number']).columns
                            if len(numeric_cols) > 0:
                                st.bar_chart(df.set_index(df.columns[0])[numeric_cols[0]])

                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": full_response,
                            "trace": trace_data,
                            "data": df
                        })

                elif route_out.route == "unsafe":
                    full_response = f"🚫 **Request Blocked**: {route_out.reason}"
                    status.update(label="Blocked", state="error")
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response, "trace": trace_data})

                elif route_out.route == "clarify":
                    full_response = f"🤔 **Clarification Needed**: {route_out.clarify_question}"
                    status.update(label="Clarification", state="complete")
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response, "trace": trace_data})
                
                else:
                    full_response = f"I can't handle this request type yet: {route_out.route}"
                    status.update(label="Unhandled", state="complete")
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response, "trace": trace_data})

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
