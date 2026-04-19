"""
Smart Digital Finance Tracker — Main Dashboard
"""
import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.crew import run_crew
from src.tools.database import (
    setup_knowledge_db,
    save_run,
    save_transaction,
    get_transactions,
    get_spending_by_category,
)

st.set_page_config(
    page_title="Smart Digital Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00C896, #0078FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #8B949E;
        font-size: 0.9rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00C896;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #8B949E;
        margin-top: 4px;
    }
    .report-box {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 24px;
        margin-top: 16px;
    }
    div[data-testid="stTabs"] button {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Init ───────────────────────────────────────────────────────────────────────
setup_knowledge_db()

for key, default in [
    ("last_result", None),
    ("run_count", 0),
    ("last_ticker", "AAPL"),
    ("last_query", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 Smart Finance")
    st.markdown("---")

    st.markdown("### 📌 Quick Tickers")
    quick = {
        "🍎 Apple": "AAPL",
        "🔍 Google": "GOOGL",
        "₿ Bitcoin": "BTC-USD",
        "Ξ Ethereum": "ETH-USD",
        "📦 Amazon": "AMZN",
        "🤖 NVIDIA": "NVDA",
        "📱 Tesla": "TSLA",
        "🏦 S&P 500": "^GSPC",
    }
    for label, ticker in quick.items():
        if st.button(label, use_container_width=True, key=f"btn_{ticker}"):
            st.session_state["last_ticker"] = ticker

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    period = st.selectbox("Chart Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)
    st.markdown("---")
    st.caption("Smart Digital Finance Tracker v1.0")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">💰 Smart Digital Finance Tracker</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time markets · AI-powered analysis · Personal finance tracking</p>', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Markets", "🤖 AI Analysis", "📊 My Finances", "➕ Add Transaction"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKETS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_input, col_go = st.columns([4, 1])
    with col_input:
        ticker_input = st.text_input(
            "Stock / Crypto Ticker",
            value=st.session_state["last_ticker"],
            placeholder="e.g. AAPL, BTC-USD, TSLA, NVDA",
            label_visibility="collapsed",
        )
    with col_go:
        load_chart = st.button("Load Chart", use_container_width=True, type="primary")

    if load_chart or ticker_input:
        ticker = ticker_input.strip().upper()
        st.session_state["last_ticker"] = ticker

        try:
            import yfinance as yf

            with st.spinner(f"Loading {ticker}..."):
                stock = yf.Ticker(ticker)
                hist  = stock.history(period=period, interval=interval)
                info  = stock.info

            if hist.empty:
                st.error(f"No data found for **{ticker}**. Check the ticker symbol and try again.")
            else:
                # ── Key metrics ────────────────────────────────────────────
                name        = info.get("longName") or info.get("shortName") or ticker
                price       = info.get("currentPrice") or info.get("regularMarketPrice") or hist["Close"].iloc[-1]
                prev_close  = info.get("previousClose") or hist["Close"].iloc[-2] if len(hist) > 1 else price
                change      = price - prev_close
                change_pct  = (change / prev_close * 100) if prev_close else 0
                market_cap  = info.get("marketCap")
                volume      = info.get("volume") or info.get("regularMarketVolume")
                fifty2_high = info.get("fiftyTwoWeekHigh")
                fifty2_low  = info.get("fiftyTwoWeekLow")

                st.markdown(f"### {name} &nbsp; `{ticker}`")

                c1, c2, c3, c4, c5 = st.columns(5)
                arrow = "▲" if change >= 0 else "▼"
                color = "#00C896" if change >= 0 else "#FF4B4B"

                c1.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color:{color}">${price:,.2f}</div>
                    <div class="metric-label">Current Price</div></div>""", unsafe_allow_html=True)
                c2.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color:{color}">{arrow} {change_pct:+.2f}%</div>
                    <div class="metric-label">Change</div></div>""", unsafe_allow_html=True)
                c3.markdown(f"""<div class="metric-card">
                    <div class="metric-value">{f'${market_cap/1e9:.1f}B' if market_cap else 'N/A'}</div>
                    <div class="metric-label">Market Cap</div></div>""", unsafe_allow_html=True)
                c4.markdown(f"""<div class="metric-card">
                    <div class="metric-value">${fifty2_high:,.2f}</div>
                    <div class="metric-label">52W High</div></div>""", unsafe_allow_html=True)
                c5.markdown(f"""<div class="metric-card">
                    <div class="metric-value">${fifty2_low:,.2f}</div>
                    <div class="metric-label">52W Low</div></div>""", unsafe_allow_html=True)

                st.markdown("")

                # ── Candlestick chart ──────────────────────────────────────
                fig = go.Figure()

                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist["Open"],
                    high=hist["High"],
                    low=hist["Low"],
                    close=hist["Close"],
                    name=ticker,
                    increasing_line_color="#00C896",
                    decreasing_line_color="#FF4B4B",
                ))

                # Volume bars
                fig.add_trace(go.Bar(
                    x=hist.index,
                    y=hist["Volume"],
                    name="Volume",
                    marker_color="rgba(0,200,150,0.2)",
                    yaxis="y2",
                ))

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0D1117",
                    plot_bgcolor="#0D1117",
                    title=dict(text=f"{name} — Price Chart ({period})", font=dict(size=16)),
                    xaxis=dict(
                        rangeslider=dict(visible=False),
                        gridcolor="#21262D",
                    ),
                    yaxis=dict(title="Price (USD)", gridcolor="#21262D", side="right"),
                    yaxis2=dict(
                        title="Volume",
                        overlaying="y",
                        side="left",
                        showgrid=False,
                        range=[0, hist["Volume"].max() * 5],
                    ),
                    legend=dict(orientation="h", y=1.02),
                    height=520,
                    margin=dict(l=10, r=10, t=50, b=10),
                )
                st.plotly_chart(fig, use_container_width=True)

                # ── Moving averages chart ──────────────────────────────────
                if len(hist) >= 20:
                    hist["MA20"] = hist["Close"].rolling(20).mean()
                    hist["MA50"] = hist["Close"].rolling(50).mean()

                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close", line=dict(color="#0078FF", width=2)))
                    fig2.add_trace(go.Scatter(x=hist.index, y=hist["MA20"], name="MA 20", line=dict(color="#FFB300", width=1.5, dash="dot")))
                    if hist["MA50"].notna().sum() > 0:
                        fig2.add_trace(go.Scatter(x=hist.index, y=hist["MA50"], name="MA 50", line=dict(color="#FF4B4B", width=1.5, dash="dot")))

                    fig2.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="#0D1117",
                        plot_bgcolor="#0D1117",
                        title=dict(text="Moving Averages", font=dict(size=14)),
                        xaxis=dict(gridcolor="#21262D"),
                        yaxis=dict(gridcolor="#21262D", side="right"),
                        height=300,
                        margin=dict(l=10, r=10, t=40, b=10),
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                # ── Company info ───────────────────────────────────────────
                summary = info.get("longBusinessSummary")
                if summary:
                    with st.expander("About this company"):
                        st.write(summary[:800] + "..." if len(summary) > 800 else summary)

        except ImportError:
            st.error("yfinance not installed. Run: `pip install yfinance` in your venv.")
        except Exception as e:
            st.error(f"Could not load data for **{ticker}**: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — AI ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🤖 Smart Financial Analysis")
    st.markdown("Enter a stock ticker or finance question to get a comprehensive AI-generated report.")

    with st.form("ai_form"):
        query = st.text_input(
            "Ask anything about stocks or personal finance",
            value=st.session_state.get("last_query", ""),
            placeholder="e.g. Analyse AAPL stock for 2025 · How should I reduce food spending? · Is NVDA a buy?",
        )
        col1, col2 = st.columns([3, 1])
        with col1:
            run_btn = st.form_submit_button("🔍 Run Analysis", use_container_width=True, type="primary")
        with col2:
            clear_btn = st.form_submit_button("Clear", use_container_width=True)

    if clear_btn:
        st.session_state["last_result"] = None
        st.session_state["last_query"] = ""
        st.rerun()

    if run_btn:
        if not query.strip():
            st.warning("Please enter a ticker or question.")
        else:
            st.session_state["last_query"] = query.strip()
            with st.spinner("Analysing... this takes 1–3 minutes ⏳"):
                try:
                    result = run_crew(query.strip())
                    st.session_state["last_result"] = result
                    st.session_state["run_count"] += 1
                    save_run(user_topic=query.strip(), result=result, status="success")
                except Exception as e:
                    save_run(user_topic=query.strip(), result=str(e), status="failed")
                    st.error(f"Analysis error: {e}")

    if st.session_state["last_result"]:
        st.success("✅ Analysis complete")
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.markdown(st.session_state["last_result"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.download_button(
            label="📥 Download Report",
            data=st.session_state["last_result"],
            file_name=f"finance_report_{st.session_state['last_query'][:25].replace(' ', '_')}.md",
            mime="text/markdown",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MY FINANCES
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Spending Overview")

    transactions   = get_transactions()
    category_totals = get_spending_by_category()

    if not transactions:
        st.info("No transactions yet. Add your first one in the **Add Transaction** tab.")
    else:
        total_spent = sum(r[1] for r in transactions)
        num_tx      = len(transactions)
        top_cat     = category_totals[0][0] if category_totals else "N/A"

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Spent", f"£{total_spent:,.2f}")
        c2.metric("Transactions", num_tx)
        c3.metric("Top Category", top_cat)

        st.markdown("")

        col_chart, col_table = st.columns([1, 1])

        with col_chart:
            if category_totals:
                df_cat = pd.DataFrame(category_totals, columns=["Category", "Total (£)"])
                fig = px.pie(
                    df_cat, names="Category", values="Total (£)",
                    hole=0.45,
                    color_discrete_sequence=px.colors.sequential.Tealgrn,
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0D1117",
                    showlegend=True,
                    height=340,
                    margin=dict(l=0, r=0, t=20, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown("**Recent Transactions**")
            df_tx = pd.DataFrame(transactions, columns=["Date", "Amount (£)", "Category", "Description"])
            df_tx["Amount (£)"] = df_tx["Amount (£)"].map("£{:.2f}".format)
            st.dataframe(df_tx.head(20), use_container_width=True, height=320)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ADD TRANSACTION
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### ➕ Log a Transaction")

    with st.form("tx_form"):
        c1, c2 = st.columns(2)
        with c1:
            tx_date   = st.date_input("Date", value=date.today())
            tx_amount = st.number_input("Amount (£)", min_value=0.01, step=0.01, format="%.2f")
        with c2:
            tx_cat = st.selectbox("Category", [
                "Food & Dining", "Transport", "Housing", "Entertainment",
                "Healthcare", "Shopping", "Utilities", "Savings",
                "Investments", "Subscriptions", "Other",
            ])
            tx_desc = st.text_input("Description", placeholder="e.g. Weekly groceries")

        add_btn = st.form_submit_button("Save Transaction", use_container_width=True, type="primary")

    if add_btn:
        if not tx_desc.strip():
            st.warning("Please add a description.")
        else:
            save_transaction(str(tx_date), tx_amount, tx_cat, tx_desc.strip())
            st.success(f"Saved: {tx_cat} — £{tx_amount:.2f}")
            st.rerun()
