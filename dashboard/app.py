"""
IQ Basket — Streamlit + Plotly e-commerce analytics dashboard.
Connects directly to ecommerce_analytics.db (SQLite).
"""

import os
import sqlite3
import time

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE_DIR, "ecommerce_analytics.db")

APP_NAME = "IQ Basket"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛒",
    layout="wide",
)


# ------------------------------------------------------------
# Theme setup (Dark / Light) — stored in session_state so the
# choice survives reruns triggered by other widgets.
# ------------------------------------------------------------
if "iqb_theme" not in st.session_state:
    st.session_state["iqb_theme"] = "Dark"

THEMES = {
    "Dark": {
        "bg": "#0e0b1a",
        "bg_gradient": "radial-gradient(circle at 50% 0%, #1b1730 0%, #0e0b1a 60%)",
        "text": "#f5f4fb",
        "subtext": "rgba(245,244,251,0.65)",
        "card_bg": "linear-gradient(145deg, rgba(108,92,231,0.16), rgba(0,206,201,0.10))",
        "card_border": "rgba(255,255,255,0.10)",
        "sidebar_bg": "linear-gradient(180deg, #171327 0%, #0e0b1a 100%)",
        "sidebar_text": "#f5f4fb",
        "header_bg": "rgba(14,11,26,0.85)",
        "footer_bg": "rgba(14,11,26,0.92)",
        "border": "rgba(255,255,255,0.08)",
        "plotly_template": "plotly_dark",
    },
    "Light": {
        "bg": "#f6f5fb",
        "bg_gradient": "radial-gradient(circle at 50% 0%, #ffffff 0%, #f0eefc 60%)",
        "text": "#241f3d",
        "subtext": "rgba(36,31,61,0.65)",
        "card_bg": "linear-gradient(145deg, rgba(108,92,231,0.10), rgba(0,206,201,0.08))",
        "card_border": "rgba(36,31,61,0.10)",
        "sidebar_bg": "linear-gradient(180deg, #ffffff 0%, #f0eefc 100%)",
        "sidebar_text": "#241f3d",
        "header_bg": "rgba(246,245,251,0.85)",
        "footer_bg": "rgba(246,245,251,0.92)",
        "border": "rgba(36,31,61,0.08)",
        "plotly_template": "plotly_white",
    },
}

CHART_COLORWAY = ["#6C5CE7", "#00CEC9", "#55EFC4", "#FD79A8", "#FDCB6E", "#74B9FF"]

# Custom cursor: a small brand-purple dot (default) and a ring cursor
# on interactive/clickable elements.
CURSOR_DOT = (
    "data:image/svg+xml;base64,"
    "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVp"
    "Z2h0PSIyNCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iNiIgZmlsbD0iIzZDNUNFNyIg"
    "ZmlsbC1vcGFjaXR5PSIwLjkiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUi"
    "Lz48L3N2Zz4="
)
CURSOR_RING = (
    "data:image/svg+xml;base64,"
    "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyOCIgaGVp"
    "Z2h0PSIyOCI+PGNpcmNsZSBjeD0iMTQiIGN5PSIxNCIgcj0iOSIgZmlsbD0ibm9uZSIgc3Ry"
    "b2tlPSIjMDBDRUM5IiBzdHJva2Utd2lkdGg9IjIuNSIvPjxjaXJjbGUgY3g9IjE0IiBjeT0i"
    "MTQiIHI9IjIuNSIgZmlsbD0iIzZDNUNFNyIvPjwvc3ZnPg=="
)

theme = THEMES[st.session_state["iqb_theme"]]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

    :root {{
        --iqb-bg: {theme["bg"]};
        --iqb-text: {theme["text"]};
        --iqb-subtext: {theme["subtext"]};
        --iqb-card-bg: {theme["card_bg"]};
        --iqb-card-border: {theme["card_border"]};
        --iqb-sidebar-bg: {theme["sidebar_bg"]};
        --iqb-header-bg: {theme["header_bg"]};
        --iqb-footer-bg: {theme["footer_bg"]};
        --iqb-border: {theme["border"]};
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        cursor: url('{CURSOR_DOT}') 12 12, auto !important;
    }}

    a, button, [role="button"], [role="radio"], [role="checkbox"],
    .stSelectbox, .stSlider, input, select, summary,
    [data-baseweb="select"], [data-testid="stSidebar"] * {{
        cursor: url('{CURSOR_RING}') 14 14, pointer !important;
    }}

    /* App + sidebar background follow the active theme */
    .stApp {{
        background: {theme["bg_gradient"]};
        color: var(--iqb-text);
    }}
    [data-testid="stAppViewContainer"] {{
        background: transparent;
    }}

    /* Keep Streamlit's native header (it holds the sidebar open/close
       toggle, essential on mobile) but make it transparent and hide
       just the Deploy/menu buttons — not needed for this local app.
       It renders above our custom header so the toggle stays clickable. */
    header[data-testid="stHeader"] {{
        background: transparent;
        box-shadow: none;
        z-index: 1000000;
    }}
    [data-testid="stAppDeployButton"],
    [data-testid="stMainMenu"] {{
        display: none;
    }}
    footer {{
        visibility: hidden;
    }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(18px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to   {{ opacity: 1; }}
    }}
    @keyframes shimmer {{
        0%   {{ background-position: -400px 0; }}
        100% {{ background-position: 400px 0; }}
    }}

    /* NOTE: intentionally opacity-only (no transform) — a transformed
       ancestor becomes the containing block for position:fixed
       descendants, which would break the fixed header/footer below. */
    .main .block-container {{
        animation: fadeIn 0.6s ease-out both;
        padding-top: 5.5rem;
        padding-bottom: 4.5rem;
        max-width: 1200px;
    }}

    /* ---- Sticky header ---- */
    .iqb-header {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: var(--iqb-header-bg);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--iqb-border);
        padding: 0.85rem 2.5rem;
        display: flex;
        align-items: baseline;
        gap: 0.9rem;
        flex-wrap: wrap;
    }}
    .iqb-title {{
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        font-size: 1.6rem;
        background: linear-gradient(90deg, #6C5CE7, #00CEC9 60%, #55EFC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }}
    .iqb-subtitle {{
        color: var(--iqb-subtext);
        font-size: 0.88rem;
        margin: 0;
    }}

    /* ---- Sticky footer ---- */
    .iqb-footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: var(--iqb-footer-bg);
        backdrop-filter: blur(10px);
        border-top: 1px solid var(--iqb-border);
        padding: 0.5rem 2.5rem;
        color: var(--iqb-subtext);
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.4rem;
    }}

    /* Section titles inside the page */
    .iqb-section {{
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.25rem;
        color: var(--iqb-text);
        margin-top: 0.4rem;
        margin-bottom: 0.6rem;
        border-left: 4px solid #6C5CE7;
        padding-left: 0.6rem;
        animation: fadeInUp 0.7s ease-out both;
    }}

    /* KPI metric cards */
    [data-testid="stMetric"] {{
        background: var(--iqb-card-bg);
        border: 1px solid var(--iqb-card-border);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 4px 18px rgba(0,0,0,0.18);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        animation: fadeInUp 0.7s ease-out both;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-6px) scale(1.015);
        box-shadow: 0 10px 28px rgba(108,92,231,0.35);
        border-color: rgba(108,92,231,0.55);
    }}
    [data-testid="stMetricLabel"] p {{ color: var(--iqb-subtext) !important; }}
    [data-testid="stMetricValue"] {{ color: var(--iqb-text) !important; }}

    div[data-testid="column"]:nth-of-type(1) [data-testid="stMetric"] {{ animation-delay: 0.05s; }}
    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {{ animation-delay: 0.15s; }}
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {{ animation-delay: 0.25s; }}

    /* Chart containers */
    [data-testid="stPlotlyChart"] {{
        border-radius: 16px;
        padding: 0.4rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeInUp 0.8s ease-out both;
    }}
    [data-testid="stPlotlyChart"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }}

    /* Sidebar — matches the app theme instead of Streamlit's default.
       padding-top clears the fixed header so the sidebar's own content
       doesn't render underneath it. */
    section[data-testid="stSidebar"] {{
        background: var(--iqb-sidebar-bg);
        border-right: 1px solid var(--iqb-border);
    }}
    section[data-testid="stSidebar"] > div {{
        padding-top: 4.2rem;
    }}
    section[data-testid="stSidebar"] * {{
        color: var(--iqb-text) !important;
        transition: color 0.2s ease, opacity 0.2s ease;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: var(--iqb-border);
    }}

    [data-testid="stSelectbox"] .react-aria-ComboBox > div,
    [data-testid="stTextInput"] > div > div {{
        background: var(--iqb-card-bg) !important;
        border-color: var(--iqb-card-border) !important;
        transition: box-shadow 0.25s ease, border-color 0.25s ease;
    }}
    [data-testid="stSelectbox"] .react-aria-ComboBox > div:hover {{
        box-shadow: 0 0 0 2px rgba(108,92,231,0.35);
    }}
    [data-testid="stSelectbox"] input {{
        color: var(--iqb-text) !important;
        background: transparent !important;
    }}
    [data-testid="stSelectbox"] button {{
        background: transparent !important;
    }}
    /* dropdown option list (rendered in a react-aria popover) */
    [role="listbox"], [role="option"] {{
        background: var(--iqb-sidebar-bg) !important;
        color: var(--iqb-text) !important;
    }}

    [data-testid="stAlert"] {{
        animation: fadeIn 0.8s ease-out both;
        border-radius: 12px;
    }}

    /* ---- Preloader ---- */
    .iqb-preloader {{
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: {theme["bg_gradient"]};
        animation: fadeIn 0.3s ease-in;
    }}
    .iqb-preloader-logo {{
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        background: linear-gradient(90deg, #6C5CE7, #00CEC9 60%, #55EFC4);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 1.6s linear infinite;
        letter-spacing: 1px;
    }}
    .iqb-preloader-tag {{
        color: var(--iqb-subtext);
        font-family: 'Inter', sans-serif;
        margin-top: 0.4rem;
        font-size: 0.95rem;
    }}
    .iqb-spinner {{
        margin-top: 1.6rem;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        border: 3px solid rgba(108,92,231,0.15);
        border-top-color: #6C5CE7;
        animation: iqb-spin 0.9s linear infinite;
    }}
    @keyframes iqb-spin {{ to {{ transform: rotate(360deg); }} }}

    /* ---- Mobile responsiveness ---- */
    @media (max-width: 640px) {{
        .iqb-header {{
            padding: 0.6rem 1rem;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.15rem;
        }}
        .iqb-title {{ font-size: 1.15rem; }}
        .iqb-subtitle {{ font-size: 0.75rem; }}
        .main .block-container {{
            padding-top: 5rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-bottom: 5.5rem;
        }}
        .iqb-footer {{
            flex-direction: column;
            text-align: center;
            padding: 0.5rem 1rem;
            font-size: 0.72rem;
        }}
        [data-testid="stMetric"] {{
            padding: 0.8rem 0.9rem;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.3rem !important;
        }}
        .iqb-section {{ font-size: 1.05rem; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# One-time animated preloader (shown once per browser session)
# ------------------------------------------------------------
if "iqb_loaded" not in st.session_state:
    preloader = st.empty()
    preloader.markdown(
        f"""
        <div class="iqb-preloader">
            <div class="iqb-preloader-logo">🛒 {APP_NAME}</div>
            <div class="iqb-preloader-tag">Loading your e-commerce insights…</div>
            <div class="iqb-spinner"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(1.1)
    preloader.empty()
    st.session_state["iqb_loaded"] = True


def get_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data
def load_table(table_name):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def check_database():
    if not os.path.exists(DB_PATH):
        st.error(
            "Database file not found. Please run the ETL scripts first:\n\n"
            "python scripts/01_load_and_inspect.py\n"
            "python scripts/02_clean_data.py\n"
            "python scripts/03_load_database.py"
        )
        st.stop()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    required = {"customer_behavior", "online_retail"}
    missing = required - set(tables)
    if missing:
        st.error(f"Missing required table(s) in database: {', '.join(missing)}")
        st.stop()


def section_header(text):
    st.markdown(f'<div class="iqb-section">{text}</div>', unsafe_allow_html=True)


def style_fig(fig):
    fig.update_layout(
        template=theme["plotly_template"],
        colorway=CHART_COLORWAY,
        transition={"duration": 500, "easing": "cubic-in-out"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, l=10, r=10, b=10),
        font=dict(family="Inter, sans-serif", color=theme["text"]),
    )
    # Single-series bar/line traces don't inherit layout.colorway automatically,
    # so recolor them explicitly to match the IQ Basket palette.
    for trace in fig.data:
        if trace.type == "bar" and len(fig.data) == 1:
            trace.marker.color = CHART_COLORWAY[0]
        elif trace.type == "scatter" and len(fig.data) == 1:
            trace.line.color = CHART_COLORWAY[0]
            trace.marker.color = CHART_COLORWAY[0]
    return fig


check_database()

try:
    customer_df = load_table("customer_behavior")
    retail_df = load_table("online_retail")
    retail_df["invoice_date"] = pd.to_datetime(retail_df["invoice_date"], errors="coerce")
except Exception:
    st.error("Failed to load data from the database. Please check the ETL pipeline ran successfully.")
    st.stop()

if customer_df.empty or retail_df.empty:
    st.error("One or more tables are empty. Please re-run the ETL pipeline.")
    st.stop()

REQUIRED_CUSTOMER_COLS = {
    "customer_id", "age", "gender", "location", "product_category",
    "purchase_amount", "payment_method", "frequency_of_purchases",
}
REQUIRED_RETAIL_COLS = {
    "invoice_no", "quantity", "invoice_date", "unit_price",
    "customer_id", "country", "revenue",
}
missing_customer_cols = REQUIRED_CUSTOMER_COLS - set(customer_df.columns)
missing_retail_cols = REQUIRED_RETAIL_COLS - set(retail_df.columns)
if missing_customer_cols or missing_retail_cols:
    st.error(
        f"Required columns missing. customer_behavior: {missing_customer_cols or 'OK'}, "
        f"online_retail: {missing_retail_cols or 'OK'}"
    )
    st.stop()


# ------------------------------------------------------------
# Sidebar — appearance, filters, dataset switcher
# (branding lives in the fixed top header instead, to avoid duplication)
# ------------------------------------------------------------
st.sidebar.header("Appearance")
theme_choice = st.sidebar.radio("Theme", ["Dark", "Light"], horizontal=True, key="iqb_theme")

st.sidebar.markdown("---")
st.sidebar.header("Filters")

locations = ["All"] + sorted(customer_df["location"].dropna().unique().tolist())
selected_location = st.sidebar.selectbox("Location", locations)

genders = ["All"] + sorted(customer_df["gender"].dropna().unique().tolist())
selected_gender = st.sidebar.selectbox("Gender", genders)

categories = ["All"] + sorted(customer_df["product_category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Product Category", categories)

payment_methods = ["All"] + sorted(customer_df["payment_method"].dropna().unique().tolist())
selected_payment = st.sidebar.selectbox("Payment Method", payment_methods)

age_min, age_max = int(customer_df["age"].min()), int(customer_df["age"].max())
selected_age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

st.sidebar.markdown("---")
st.sidebar.header("Analysis Dataset")
dataset_choice = st.sidebar.radio("Choose dataset", ["Customer Behavior", "Online Retail"])

filtered_df = customer_df.copy()
if selected_location != "All":
    filtered_df = filtered_df[filtered_df["location"] == selected_location]
if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["gender"] == selected_gender]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["product_category"] == selected_category]
if selected_payment != "All":
    filtered_df = filtered_df[filtered_df["payment_method"] == selected_payment]
filtered_df = filtered_df[
    (filtered_df["age"] >= selected_age_range[0]) & (filtered_df["age"] <= selected_age_range[1])
]


# ------------------------------------------------------------
# Sticky header + footer (rendered as fixed-position bars; the
# block-container padding above reserves space for both)
# ------------------------------------------------------------
st.markdown(
    f"""
    <div class="iqb-header">
        <span class="iqb-title">🛒 {APP_NAME}</span>
        <span class="iqb-subtitle">Interactive analysis of customer behavior, payment preferences, sales and e-commerce trends.</span>
    </div>
    <div class="iqb-footer">
        <span>© {APP_NAME} — Local Analytics Portfolio Project</span>
        <span>Built with Python · Pandas · SQLite · Streamlit · Plotly</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Customer Behavior view
# ------------------------------------------------------------
if dataset_choice == "Customer Behavior":
    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    total_revenue = filtered_df["purchase_amount"].sum()
    active_customers = filtered_df["customer_id"].nunique()
    average_order_value = filtered_df["purchase_amount"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Active Customers", f"{active_customers:,}")
    col3.metric("Average Order Value", f"${average_order_value:,.2f}")

    section_header("Sales by Product Category")
    category_revenue = (
        filtered_df.groupby("product_category")["purchase_amount"]
        .sum()
        .reset_index()
        .sort_values("purchase_amount", ascending=False)
    )
    fig_category = px.bar(
        category_revenue,
        x="product_category",
        y="purchase_amount",
        labels={"product_category": "Product Category", "purchase_amount": "Total Revenue ($)"},
    )
    st.plotly_chart(style_fig(fig_category), use_container_width=True)

    section_header("Payment Method Distribution")
    payment_counts = filtered_df["payment_method"].value_counts().reset_index()
    payment_counts.columns = ["payment_method", "count"]
    fig_payment = px.pie(
        payment_counts,
        names="payment_method",
        values="count",
        hole=0.5,
    )
    fig_payment.update_traces(textinfo="percent+label")
    st.plotly_chart(style_fig(fig_payment), use_container_width=True)

    st.info(
        "Note: the Customer Shopping Trends dataset has no purchase-date column, "
        "so a monthly revenue trend is not available here. See the Online Retail "
        "dataset for a monthly trend chart."
    )

    section_header("Additional Insights")
    left, right = st.columns(2)

    with left:
        st.markdown("**Purchase Frequency**")
        freq_summary = (
            filtered_df.groupby("frequency_of_purchases")["purchase_amount"]
            .agg(purchase_count="count", total_revenue="sum")
            .reset_index()
            .sort_values("purchase_count", ascending=False)
        )
        fig_freq = px.bar(
            freq_summary,
            x="frequency_of_purchases",
            y="purchase_count",
            labels={"frequency_of_purchases": "Frequency", "purchase_count": "Purchase Count"},
        )
        st.plotly_chart(style_fig(fig_freq), use_container_width=True)

    with right:
        st.markdown("**Top Locations by Revenue**")
        location_revenue = (
            filtered_df.groupby("location")["purchase_amount"]
            .sum()
            .reset_index()
            .sort_values("purchase_amount", ascending=False)
            .head(10)
        )
        fig_location = px.bar(
            location_revenue,
            x="purchase_amount",
            y="location",
            orientation="h",
            labels={"purchase_amount": "Total Revenue ($)", "location": "Location"},
        )
        fig_location.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(style_fig(fig_location), use_container_width=True)


# ------------------------------------------------------------
# Online Retail view
# ------------------------------------------------------------
else:
    total_revenue = retail_df["revenue"].sum()
    active_customers = retail_df["customer_id"].dropna().nunique()
    invoice_totals = retail_df.groupby("invoice_no")["revenue"].sum()
    average_order_value = invoice_totals.mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Active Customers", f"{active_customers:,}")
    col3.metric("Average Order Value", f"${average_order_value:,.2f}")

    section_header("Monthly Revenue Trend")
    retail_df["month"] = retail_df["invoice_date"].dt.to_period("M").astype(str)
    monthly_revenue = (
        retail_df.groupby("month")["revenue"].sum().reset_index().sort_values("month")
    )
    fig_monthly = px.line(
        monthly_revenue,
        x="month",
        y="revenue",
        markers=True,
        labels={"month": "Month", "revenue": "Revenue ($)"},
    )
    fig_monthly.update_traces(line=dict(width=3))
    st.plotly_chart(style_fig(fig_monthly), use_container_width=True)

    section_header("Top Countries by Revenue (excluding United Kingdom)")
    country_revenue = (
        retail_df[retail_df["country"] != "United Kingdom"]
        .groupby("country")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    fig_country = px.bar(
        country_revenue,
        x="revenue",
        y="country",
        orientation="h",
        labels={"revenue": "Total Revenue ($)", "country": "Country"},
    )
    fig_country.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(style_fig(fig_country), use_container_width=True)
