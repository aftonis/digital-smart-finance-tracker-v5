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
from src.tools.calculators import (
    calculate_simple_interest,
    calculate_compound_interest,
    calculate_future_value,
    calculate_present_value,
    calculate_future_value_annuity,
    calculate_present_value_annuity,
    COMPOUND_FREQUENCIES,
)
import numpy as np

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
    /* Make the main 5 tabs bigger and bolder */
    div[data-testid="stTabs"] > div > div > div > button {
        font-size: 1.05rem;
        font-weight: 700;
        padding: 14px 28px;
        min-height: 56px;
        border-radius: 10px 10px 0 0;
        margin-right: 4px;
    }
    div[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {
        background: linear-gradient(90deg, rgba(0,200,150,0.18), rgba(0,120,255,0.18));
        border-bottom: 3px solid #00C896;
        color: #FFFFFF;
    }
    /* Compact index-strip cards */
    .index-strip {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 10px 16px;
        text-align: center;
        height: 72px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .index-name {
        font-size: 0.72rem;
        color: #8B949E;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .index-price {
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 2px;
    }
    .index-change {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ── Init ───────────────────────────────────────────────────────────────────────
setup_knowledge_db()

for key, default in [
    ("last_result", None),
    ("run_count", 0),
    ("last_ticker", ""),          # empty → don't auto-load a chart on first visit
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
        "₿ Bitcoin": "BTC-USD",
        "🏦 S&P 500": "^GSPC",
    }
    for label, ticker in quick.items():
        if st.button(label, use_container_width=True, key=f"btn_{ticker}"):
            st.session_state["last_ticker"] = ticker

    st.markdown("##### 🔎 More tickers")
    more_options = [
        "GOOGL — Google", "AMZN — Amazon", "NVDA — NVIDIA", "TSLA — Tesla",
        "MSFT — Microsoft", "META — Meta", "NFLX — Netflix", "ETH-USD — Ethereum",
        "SOL-USD — Solana", "^DJI — Dow Jones", "^IXIC — Nasdaq", "GC=F — Gold",
        "Custom…",
    ]
    picked = st.selectbox("Pick or type a ticker", more_options, index=0, key="ticker_picker")
    if picked == "Custom…":
        custom = st.text_input("Enter any ticker", placeholder="e.g. COIN, QQQ, AVAX-USD", key="custom_ticker")
        if st.button("Load custom", use_container_width=True) and custom.strip():
            st.session_state["last_ticker"] = custom.strip().upper()
    else:
        if st.button(f"Load {picked.split(' — ')[0]}", use_container_width=True):
            st.session_state["last_ticker"] = picked.split(" — ")[0]

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    period = st.selectbox("Chart Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)
    st.markdown("---")
    st.caption("Smart Digital Finance Tracker v1.0")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">💰 Digital Smart Finance Tracker v5</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time markets · AI-powered analysis · Loan rates · Finance calculator</p>', unsafe_allow_html=True)

# ── Compact market-index strip (NASDAQ + majors) ──────────────────────────────
@st.cache_data(ttl=120)
def _fetch_index_snapshot(symbols: list) -> dict:
    """Fetch latest close + daily % change for a list of symbols (cached 2min)."""
    import yfinance as yf
    out = {}
    for sym in symbols:
        try:
            hist = yf.Ticker(sym).history(period="5d", interval="1d")
            if len(hist) >= 2:
                last = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                pct = (last - prev) / prev * 100 if prev else 0.0
                out[sym] = (last, pct)
        except Exception:
            pass
    return out

_indices = [
    ("^IXIC",   "NASDAQ"),
    ("^GSPC",   "S&P 500"),
    ("^DJI",    "DOW JONES"),
    ("BTC-USD", "BITCOIN"),
    ("ETH-USD", "ETHEREUM"),
    ("GC=F",    "GOLD"),
]
_snap = _fetch_index_snapshot([s for s, _ in _indices])

_strip_cols = st.columns(len(_indices))
for col, (sym, label) in zip(_strip_cols, _indices):
    data = _snap.get(sym)
    if data:
        price, pct = data
        arrow = "▲" if pct >= 0 else "▼"
        color = "#00C896" if pct >= 0 else "#FF4B4B"
        fmt = f"${price:,.0f}" if price >= 1000 else f"${price:,.2f}"
        col.markdown(
            f"""<div class="index-strip">
                <div class="index-name">{label}</div>
                <div class="index-price">{fmt}</div>
                <div class="index-change" style="color:{color}">{arrow} {pct:+.2f}%</div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        col.markdown(
            f"""<div class="index-strip">
                <div class="index-name">{label}</div>
                <div class="index-price" style="color:#8B949E">—</div>
                <div class="index-change" style="color:#8B949E">offline</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("")  # spacing

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Markets", "🤖 AI Analysis", "📊 My Finances", "➕ Add Transaction", "🧮 Calculator"]
)

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

    ticker = (ticker_input or "").strip().upper()
    if not ticker:
        st.info("👆 Pick a ticker from the sidebar, type one above, or click **Load Chart**. Indices at the top update every 2 minutes.")
    elif load_chart or ticker:
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
    # ── Loan Rates Calculator ──────────────────────────────────────────────────
    st.markdown("### 🏦 Major Loan Rates — Daily / Weekly / Monthly")
    st.caption("Edit any APR (%) or loan amount to recalculate instantly. Rates are indicative US/UK averages — update to match your actual loan offers.")

    default_loans = pd.DataFrame([
        {"Loan Type": "Mortgage (30-yr fixed)", "APR (%)": 6.85, "Amount": 250000.0},
        {"Loan Type": "Mortgage (15-yr fixed)", "APR (%)": 6.10, "Amount": 250000.0},
        {"Loan Type": "Auto Loan (new, 60-mo)", "APR (%)": 7.50, "Amount": 30000.0},
        {"Loan Type": "Auto Loan (used, 48-mo)", "APR (%)": 8.90, "Amount": 18000.0},
        {"Loan Type": "Personal Loan",           "APR (%)": 12.50, "Amount": 10000.0},
        {"Loan Type": "Credit Card (avg)",       "APR (%)": 22.75, "Amount": 5000.0},
        {"Loan Type": "Student Loan (federal)",  "APR (%)": 6.53,  "Amount": 35000.0},
        {"Loan Type": "HELOC",                   "APR (%)": 9.25,  "Amount": 50000.0},
        {"Loan Type": "Payday Loan",             "APR (%)": 391.0, "Amount": 500.0},
    ])

    edited_loans = st.data_editor(
        default_loans,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Loan Type": st.column_config.TextColumn("Loan Type", width="medium"),
            "APR (%)":   st.column_config.NumberColumn("APR (%)",  min_value=0.0, max_value=1000.0, step=0.05, format="%.2f"),
            "Amount":    st.column_config.NumberColumn("Principal ($)", min_value=0.0, step=100.0, format="$%.2f"),
        },
        key="loan_editor",
    )

    # Calculate daily / weekly / monthly interest costs + effective rates
    df_rates = edited_loans.copy()
    df_rates["Daily Rate (%)"]   = (df_rates["APR (%)"] / 365).round(4)
    df_rates["Weekly Rate (%)"]  = (df_rates["APR (%)"] / 52).round(4)
    df_rates["Monthly Rate (%)"] = (df_rates["APR (%)"] / 12).round(4)
    df_rates["Daily Interest ($)"]   = (df_rates["Amount"] * df_rates["APR (%)"] / 100 / 365).round(2)
    df_rates["Weekly Interest ($)"]  = (df_rates["Amount"] * df_rates["APR (%)"] / 100 / 52).round(2)
    df_rates["Monthly Interest ($)"] = (df_rates["Amount"] * df_rates["APR (%)"] / 100 / 12).round(2)
    df_rates["Yearly Interest ($)"]  = (df_rates["Amount"] * df_rates["APR (%)"] / 100).round(2)

    display_cols = [
        "Loan Type", "APR (%)", "Amount",
        "Daily Rate (%)", "Weekly Rate (%)", "Monthly Rate (%)",
        "Daily Interest ($)", "Weekly Interest ($)", "Monthly Interest ($)", "Yearly Interest ($)",
    ]
    st.markdown("#### 📋 Calculated Rates & Interest Cost")
    st.dataframe(
        df_rates[display_cols].style.format({
            "APR (%)":              "{:.2f}%",
            "Amount":               "${:,.2f}",
            "Daily Rate (%)":       "{:.4f}%",
            "Weekly Rate (%)":      "{:.4f}%",
            "Monthly Rate (%)":     "{:.4f}%",
            "Daily Interest ($)":   "${:,.2f}",
            "Weekly Interest ($)":  "${:,.2f}",
            "Monthly Interest ($)": "${:,.2f}",
            "Yearly Interest ($)":  "${:,.2f}",
        }),
        use_container_width=True,
        height=360,
    )

    # Comparison bar chart
    fig_loans = go.Figure()
    fig_loans.add_trace(go.Bar(
        x=df_rates["Loan Type"], y=df_rates["Monthly Interest ($)"],
        name="Monthly Interest", marker_color="#00C896",
    ))
    fig_loans.add_trace(go.Bar(
        x=df_rates["Loan Type"], y=df_rates["Weekly Interest ($)"],
        name="Weekly Interest", marker_color="#0078FF",
    ))
    fig_loans.add_trace(go.Bar(
        x=df_rates["Loan Type"], y=df_rates["Daily Interest ($)"],
        name="Daily Interest", marker_color="#FFB300",
    ))
    fig_loans.update_layout(
        template="plotly_dark", paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
        title="Interest Cost by Period — per Loan",
        barmode="group", height=380, margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(gridcolor="#21262D", tickangle=-25),
        yaxis=dict(gridcolor="#21262D", title="Interest ($)"),
    )
    st.plotly_chart(fig_loans, use_container_width=True)

    st.markdown("---")

    # ── Spending Overview (existing) ───────────────────────────────────────────
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

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — FINANCE CALCULATOR (from Digital_Smart_Finance_Calculator notebook)
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🧮 Digital Smart Finance Calculator")
    st.caption("Six core time-value-of-money calculators with growth visualisations. Ported from the Colab notebook.")

    calc_tabs = st.tabs([
        "Simple Interest", "Compound Interest", "Future Value",
        "Present Value", "FV Annuity", "PV Annuity",
    ])

    def _freq_selector(key: str) -> int:
        """Compound frequency dropdown → returns n per year."""
        label = st.selectbox(
            "Compounding frequency", list(COMPOUND_FREQUENCIES.keys()),
            index=3, key=f"freq_{key}",
        )
        return COMPOUND_FREQUENCIES[label]

    def _metric_card(label: str, value: str, color: str = "#00C896"):
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-value" style="color:{color}">{value}</div>
                <div class="metric-label">{label}</div></div>""",
            unsafe_allow_html=True,
        )

    def _growth_chart(years: np.ndarray, values: list, title: str, ylabel: str = "Value ($)"):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=values, mode="lines+markers",
            line=dict(color="#00C896", width=2.5),
            marker=dict(size=6, color="#0078FF"),
            fill="tozeroy", fillcolor="rgba(0,200,150,0.08)",
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
            title=dict(text=title, font=dict(size=14)),
            xaxis=dict(title="Years", gridcolor="#21262D"),
            yaxis=dict(title=ylabel, gridcolor="#21262D"),
            height=350, margin=dict(l=10, r=10, t=50, b=10),
        )
        return fig

    # ─── SIMPLE INTEREST ─────────────────────────────────────────────────
    with calc_tabs[0]:
        st.markdown("##### Formula: `I = P × r × t`")
        c1, c2, c3 = st.columns(3)
        si_principal = c1.number_input("Principal ($)", min_value=0.0, value=1000.0, step=100.0, key="si_p")
        si_rate      = c2.number_input("Annual rate (%)", min_value=0.0, value=5.0, step=0.25, key="si_r")
        si_time      = c3.number_input("Time (years)", min_value=0.0, value=3.0, step=0.5, key="si_t")

        si_interest = calculate_simple_interest(si_principal, si_rate / 100, si_time)
        total_si = si_principal + si_interest

        m1, m2, m3 = st.columns(3)
        with m1: _metric_card("Interest earned", f"${si_interest:,.2f}")
        with m2: _metric_card("Total amount", f"${total_si:,.2f}", "#0078FF")
        with m3: _metric_card("Growth %", f"{(si_interest/si_principal*100 if si_principal else 0):.2f}%", "#FFB300")

        if si_time > 0:
            years = np.linspace(0, si_time, 30)
            vals = [si_principal + calculate_simple_interest(si_principal, si_rate/100, t) for t in years]
            st.plotly_chart(_growth_chart(years, vals, "Simple Interest Growth"), use_container_width=True)

    # ─── COMPOUND INTEREST ───────────────────────────────────────────────
    with calc_tabs[1]:
        st.markdown("##### Formula: `A = P × (1 + r/n)^(n·t)`")
        c1, c2, c3 = st.columns(3)
        ci_principal = c1.number_input("Principal ($)", min_value=0.0, value=1000.0, step=100.0, key="ci_p")
        ci_rate      = c2.number_input("Annual rate (%)", min_value=0.0, value=5.0, step=0.25, key="ci_r")
        ci_time      = c3.number_input("Time (years)", min_value=0.0, value=3.0, step=0.5, key="ci_t")
        ci_n = _freq_selector("ci")

        total_ci = calculate_compound_interest(ci_principal, ci_rate/100, ci_time, ci_n)
        ci_interest = total_ci - ci_principal

        m1, m2, m3 = st.columns(3)
        with m1: _metric_card("Compound interest", f"${ci_interest:,.2f}")
        with m2: _metric_card("Total amount", f"${total_ci:,.2f}", "#0078FF")
        with m3: _metric_card("Growth %", f"{(ci_interest/ci_principal*100 if ci_principal else 0):.2f}%", "#FFB300")

        if ci_time > 0:
            years = np.linspace(0, ci_time, 30)
            vals_compound = [calculate_compound_interest(ci_principal, ci_rate/100, t, ci_n) for t in years]
            vals_simple   = [ci_principal + calculate_simple_interest(ci_principal, ci_rate/100, t) for t in years]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=vals_compound, name="Compound", line=dict(color="#00C896", width=2.5)))
            fig.add_trace(go.Scatter(x=years, y=vals_simple,   name="Simple",   line=dict(color="#FFB300", width=2, dash="dot")))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
                title="Compound vs Simple — same P, r, t",
                xaxis=dict(title="Years", gridcolor="#21262D"),
                yaxis=dict(title="Value ($)", gridcolor="#21262D"),
                height=350, margin=dict(l=10, r=10, t=50, b=10),
                legend=dict(orientation="h", y=1.08),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ─── FUTURE VALUE ────────────────────────────────────────────────────
    with calc_tabs[2]:
        st.markdown("##### Formula: `FV = PV × (1 + r/n)^(n·t)` — what today's money is worth later")
        c1, c2, c3 = st.columns(3)
        fv_pv    = c1.number_input("Present value ($)", min_value=0.0, value=1000.0, step=100.0, key="fv_pv")
        fv_rate  = c2.number_input("Annual rate (%)",   min_value=0.0, value=5.0, step=0.25, key="fv_r")
        fv_time  = c3.number_input("Time (years)",      min_value=0.0, value=10.0, step=1.0, key="fv_t")
        fv_n = _freq_selector("fv")

        fv_result = calculate_future_value(fv_pv, fv_rate/100, fv_time, fv_n)

        m1, m2 = st.columns(2)
        with m1: _metric_card("Future value", f"${fv_result:,.2f}")
        with m2: _metric_card("Total gain",   f"${fv_result - fv_pv:,.2f}", "#0078FF")

        if fv_time > 0:
            years = np.arange(1, int(fv_time)+2)
            vals = [calculate_future_value(fv_pv, fv_rate/100, t, fv_n) for t in years]
            st.plotly_chart(_growth_chart(years, vals, "Future Value over Time"), use_container_width=True)

    # ─── PRESENT VALUE ───────────────────────────────────────────────────
    with calc_tabs[3]:
        st.markdown("##### Formula: `PV = FV / (1 + r/n)^(n·t)` — what future money is worth today")
        c1, c2, c3 = st.columns(3)
        pv_fv    = c1.number_input("Future value ($)", min_value=0.0, value=10000.0, step=500.0, key="pv_fv")
        pv_rate  = c2.number_input("Annual rate (%)",  min_value=0.0, value=5.0, step=0.25, key="pv_r")
        pv_time  = c3.number_input("Years until",      min_value=0.0, value=10.0, step=1.0, key="pv_t")
        pv_n = _freq_selector("pv")

        pv_result = calculate_present_value(pv_fv, pv_rate/100, pv_time, pv_n)

        m1, m2 = st.columns(2)
        with m1: _metric_card("Present value", f"${pv_result:,.2f}")
        with m2: _metric_card("Discount",      f"${pv_fv - pv_result:,.2f}", "#FF4B4B")

        if pv_time > 0:
            years = np.arange(1, 31)
            vals = [calculate_present_value(pv_fv, pv_rate/100, t, pv_n) for t in years]
            st.plotly_chart(
                _growth_chart(years, vals, f"Present Value vs Time (FV=${pv_fv:,.0f} @ {pv_rate}%)",
                              ylabel="Present Value ($)"),
                use_container_width=True,
            )

    # ─── FV ANNUITY ──────────────────────────────────────────────────────
    with calc_tabs[4]:
        st.markdown("##### Formula: `FVA = P × [((1 + r/n)^(n·t) − 1) / (r/n)]` — regular deposits growing to a target")
        c1, c2, c3 = st.columns(3)
        fva_pmt   = c1.number_input("Payment per period ($)", min_value=0.0, value=100.0, step=25.0, key="fva_p")
        fva_rate  = c2.number_input("Annual rate (%)",        min_value=0.0, value=5.0, step=0.25, key="fva_r")
        fva_time  = c3.number_input("Time (years)",           min_value=0.0, value=10.0, step=1.0, key="fva_t")
        fva_n = _freq_selector("fva")

        fva_result = calculate_future_value_annuity(fva_pmt, fva_rate/100, fva_time, fva_n)
        total_paid = fva_pmt * fva_n * fva_time

        m1, m2, m3 = st.columns(3)
        with m1: _metric_card("Future value of annuity", f"${fva_result:,.2f}")
        with m2: _metric_card("Total contributions",     f"${total_paid:,.2f}", "#0078FF")
        with m3: _metric_card("Interest earned",         f"${fva_result - total_paid:,.2f}", "#FFB300")

        if fva_time > 0:
            years = np.arange(1, int(fva_time)+2)
            vals_fv  = [calculate_future_value_annuity(fva_pmt, fva_rate/100, t, fva_n) for t in years]
            vals_paid = [fva_pmt * fva_n * t for t in years]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=vals_fv,   name="FV of annuity", line=dict(color="#00C896", width=2.5), fill="tozeroy", fillcolor="rgba(0,200,150,0.08)"))
            fig.add_trace(go.Scatter(x=years, y=vals_paid, name="Total paid in", line=dict(color="#FFB300", width=2, dash="dot")))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
                title="Annuity growth vs Contributions",
                xaxis=dict(title="Years", gridcolor="#21262D"),
                yaxis=dict(title="Value ($)", gridcolor="#21262D"),
                height=350, margin=dict(l=10, r=10, t=50, b=10),
                legend=dict(orientation="h", y=1.08),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ─── PV ANNUITY ──────────────────────────────────────────────────────
    with calc_tabs[5]:
        st.markdown("##### Formula: `PVA = P × [(1 − (1 + r/n)^(−n·t)) / (r/n)]` — lump sum equivalent of future payments (loans!)")
        c1, c2, c3 = st.columns(3)
        pva_pmt   = c1.number_input("Payment per period ($)", min_value=0.0, value=200.0, step=25.0, key="pva_p")
        pva_rate  = c2.number_input("Annual rate (%)",        min_value=0.0, value=7.0, step=0.25, key="pva_r")
        pva_time  = c3.number_input("Time (years)",           min_value=0.0, value=5.0, step=1.0, key="pva_t")
        pva_n = _freq_selector("pva")

        pva_result = calculate_present_value_annuity(pva_pmt, pva_rate/100, pva_time, pva_n)
        total_received = pva_pmt * pva_n * pva_time

        m1, m2, m3 = st.columns(3)
        with m1: _metric_card("Present value of annuity", f"${pva_result:,.2f}")
        with m2: _metric_card("Total received",           f"${total_received:,.2f}", "#0078FF")
        with m3: _metric_card("Interest portion",         f"${total_received - pva_result:,.2f}", "#FFB300")

        if pva_time > 0:
            years = np.arange(1, int(pva_time)+2)
            vals = [calculate_present_value_annuity(pva_pmt, pva_rate/100, t, pva_n) for t in years]
            st.plotly_chart(_growth_chart(years, vals, "PV of Annuity vs Term"), use_container_width=True)
