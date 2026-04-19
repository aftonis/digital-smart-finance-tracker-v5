"""
streamlit_app.py — Smart Digital Finance Tracker Dashboard.
"""
import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.crew import run_crew
from src.tools.database import (
    setup_knowledge_db,
    save_run,
    save_transaction,
    get_transactions,
    get_spending_by_category,
)
from src.tools.debug_tools import run_smoke_test

st.set_page_config(
    page_title="Smart Digital Finance Tracker",
    page_icon="💰",
    layout="wide",
)

# ── Session state ──────────────────────────────────────────────────────────────
for key, default in [
    ("last_result", None),
    ("run_count", 0),
    ("last_topic", ""),
    ("debug_mode", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Ensure DB is ready
setup_knowledge_db()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("💰 Finance Tracker")
    st.markdown("**AI Pipeline Stack**")
    st.markdown("- 🤖 CrewAI A-A-R Pipeline")
    st.markdown("- 🔍 SerperDevTool (web search)")
    st.markdown("- 🗄️ SQLite (memory.db)")
    st.markdown("- 🔒 SafeQueryTool (read-only)")
    st.markdown("- 📁 FileReadTool (Semantic Vault)")
    st.divider()
    st.markdown("**Agents**")
    st.markdown("- 📊 Expense Analyst")
    st.markdown("- 💡 Financial Advisor")
    st.markdown("- 📝 Report Writer")
    st.divider()
    st.markdown("**Resilience Stack**")
    st.markdown("- L1: Exponential backoff retry")
    st.markdown("- L2: max_tokens=5000 cap")
    st.markdown("- L3: JSON schema enforcement")
    st.markdown("- L4: Reviewer metacognition")
    st.divider()
    st.session_state["debug_mode"] = st.toggle(
        "🔧 Debug Mode",
        value=st.session_state["debug_mode"],
    )
    st.markdown(f"**AI runs this session:** {st.session_state['run_count']}")
    if st.session_state["last_topic"]:
        st.markdown(f"**Last query:** {st.session_state['last_topic'][:40]}...")
    st.caption("Smart Digital Finance Tracker · Blueprint Blue")

# ── Main tabs ──────────────────────────────────────────────────────────────────
st.title("💰 Smart Digital Finance Tracker")
st.caption("A-A-R Pipeline: Analyse → Advise → Report  |  Powered by CrewAI")
st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add Transaction", "🤖 AI Analysis"])

# ─── Tab 1: Dashboard ─────────────────────────────────────────────────────────
with tab1:
    st.subheader("Spending Overview")

    transactions = get_transactions()
    category_totals = get_spending_by_category()

    if not transactions:
        st.info("No transactions yet. Add some in the **Add Transaction** tab.")
    else:
        # Spending by category chart
        if category_totals:
            df_cat = pd.DataFrame(category_totals, columns=["Category", "Total (£)"])
            fig = px.pie(
                df_cat,
                names="Category",
                values="Total (£)",
                title="Spending by Category",
                hole=0.4,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Recent transactions table
        st.subheader("Recent Transactions")
        df_tx = pd.DataFrame(transactions, columns=["Date", "Amount (£)", "Category", "Description"])
        df_tx["Amount (£)"] = df_tx["Amount (£)"].map("{:.2f}".format)
        st.dataframe(df_tx, use_container_width=True)

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        total_spent = sum(row[1] for row in transactions)
        num_tx = len(transactions)
        top_cat = category_totals[0][0] if category_totals else "N/A"

        col1.metric("Total Spent", f"£{total_spent:,.2f}")
        col2.metric("Transactions", num_tx)
        col3.metric("Top Category", top_cat)

# ─── Tab 2: Add Transaction ────────────────────────────────────────────────────
with tab2:
    st.subheader("Log a Transaction")

    with st.form("transaction_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            tx_date = st.date_input("Date", value=date.today())
            tx_amount = st.number_input("Amount (£)", min_value=0.01, step=0.01, format="%.2f")
        with col_b:
            tx_category = st.selectbox(
                "Category",
                ["Food & Dining", "Transport", "Housing", "Entertainment",
                 "Healthcare", "Shopping", "Utilities", "Savings", "Other"],
            )
            tx_description = st.text_input("Description", placeholder="e.g. Weekly groceries")

        add_tx = st.form_submit_button("Add Transaction", use_container_width=True)

    if add_tx:
        if tx_amount <= 0:
            st.warning("Please enter an amount greater than 0.")
        elif not tx_description.strip():
            st.warning("Please enter a description.")
        else:
            save_transaction(
                date=str(tx_date),
                amount=tx_amount,
                category=tx_category,
                description=tx_description.strip(),
            )
            st.success(f"Transaction added: {tx_category} — £{tx_amount:.2f}")
            st.rerun()

# ─── Tab 3: AI Analysis ───────────────────────────────────────────────────────
with tab3:
    st.subheader("AI Financial Analysis")
    st.markdown(
        "Ask the AI crew a finance question. The 3-agent pipeline will "
        "analyse your data, give advice, and produce a professional report."
    )

    with st.form("ai_form"):
        user_topic = st.text_input(
            "Finance Question",
            placeholder="e.g. How can I reduce my food spending this month?",
            value=st.session_state["last_topic"],
        )
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("🤖 Run AI Analysis", use_container_width=True)
        with col2:
            smoke_check = st.form_submit_button("🔬 Smoke Test", use_container_width=True)

    if smoke_check:
        with st.spinner("Running environment diagnostics..."):
            results = run_smoke_test()
        passed = sum(1 for ok, _ in results.values() if ok)
        total = len(results)
        if passed == total:
            st.success(f"✅ All {total} checks passed — ready for deployment.")
        else:
            st.warning(f"⚠️ {passed}/{total} checks passed.")
        with st.expander("Diagnostics Detail", expanded=True):
            for check, (ok, detail) in results.items():
                icon = "✅" if ok else "❌"
                st.markdown(f"{icon} **{check}** — {detail}")

    if submitted:
        if not user_topic.strip():
            st.warning("Please enter a finance question before running.")
        else:
            st.session_state["last_topic"] = user_topic.strip()
            try:
                with st.spinner("🤖 Agents are analysing your finances... (1-3 minutes)"):
                    result = run_crew(user_topic.strip())
                st.session_state["last_result"] = result
                st.session_state["run_count"] += 1
                save_run(user_topic=user_topic.strip(), result=result, status="success")
                st.success("✅ Analysis Complete!")
                st.divider()
                st.markdown("### 📄 Financial Report")
                st.markdown(result)
                st.download_button(
                    label="📥 Download Report",
                    data=result,
                    file_name=f"finance_report_{user_topic[:30].replace(' ', '_')}.md",
                    mime="text/markdown",
                )
            except Exception as e:
                save_run(user_topic=user_topic.strip(), result=str(e), status="failed")
                st.error(f"Analysis Error: {e}")

# ─── Debug Panel ──────────────────────────────────────────────────────────────
if st.session_state["debug_mode"]:
    st.divider()
    st.markdown("### 🔧 Debug Panel")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Session State**")
        st.json({
            "run_count" : st.session_state["run_count"],
            "last_topic": st.session_state["last_topic"],
            "has_result": st.session_state["last_result"] is not None,
        })
    with col_b:
        st.markdown("**Environment**")
        import platform
        st.json({
            "python"        : platform.python_version(),
            "os"            : platform.system(),
            "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
            "serper_key_set": bool(os.environ.get("SERPER_API_KEY")),
        })
    if st.session_state["last_result"]:
        with st.expander("Last Raw Result"):
            st.text(st.session_state["last_result"])
