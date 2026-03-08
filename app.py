"""
Montreal Housing Market Dashboard
==================================
Interactive Streamlit dashboard exploring rental and housing price trends
across Montreal boroughs. Data is synthetic, modeled on real market ranges.

Author: Yumo Xu
Portfolio: yumorepos.github.io
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta

# ── Page config (must be first Streamlit call) ────────────────────
st.set_page_config(
    page_title="Montreal Housing Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants (mirrored from analysis.py) ────────────────────────
SEED = 42
np.random.seed(SEED)

BOROUGHS = [
    "Plateau-Mont-Royal",
    "Mile End",
    "Griffintown",
    "Verdun",
    "NDG",
    "Rosemont",
    "Villeray",
    "Hochelaga",
    "Old Montreal",
    "Downtown",
]

BASE_RENT = {
    "Studio": 1050,
    "1BR": 1500,
    "2BR": 1900,
    "3BR": 2450,
}

BOROUGH_MULT = {
    "Plateau-Mont-Royal": 1.18,
    "Mile End": 1.15,
    "Griffintown": 1.20,
    "Verdun": 0.94,
    "NDG": 1.00,
    "Rosemont": 1.05,
    "Villeray": 0.96,
    "Hochelaga": 0.87,
    "Old Montreal": 1.38,
    "Downtown": 1.32,
}

ANNUAL_INCREASES = {
    2019: 0.022,
    2020: 0.018,
    2021: 0.025,
    2022: 0.055,
    2023: 0.065,
    2024: 0.042,
    2025: 0.032,
}

BASE_PRICE = {
    "Condo": 310_000,
    "Duplex": 490_000,
    "Single-Family": 425_000,
    "Triplex": 640_000,
}

ANNUAL_PRICE_GROWTH = {
    2019: 0.04,
    2020: 0.06,
    2021: 0.15,
    2022: 0.09,
    2023: -0.03,
    2024: 0.04,
    2025: 0.05,
}

MEDIAN_INCOME = {
    2019: 50_000,
    2020: 51_500,
    2021: 53_000,
    2022: 56_000,
    2023: 58_500,
    2024: 61_000,
    2025: 63_500,
}

# ── Plotly dark theme palette ─────────────────────────────────────
ACCENT_COLORS = [
    "#7C83FD", "#96BAFF", "#59C3C3", "#F7B731",
    "#FC5C65", "#45AAB8", "#A55EEA", "#26DE81",
]
CARD_BG = "#1E2130"
PLOT_BG = "#161B2E"
PAPER_BG = "#0E1117"
GRID_COLOR = "#2A2F4A"
TEXT_COLOR = "#E8EAF6"


# ── Data generation (cached) ──────────────────────────────────────
@st.cache_data(show_spinner="Generating dataset…")
def generate_rental_data(n_per_combo: int = 35) -> pd.DataFrame:
    rows = []
    for year in range(2019, 2026):
        cumulative = 1.0
        for y in range(2019, year + 1):
            cumulative *= 1 + ANNUAL_INCREASES.get(y, 0.03)

        for borough in BOROUGHS:
            for unit_type, base in BASE_RENT.items():
                for _ in range(n_per_combo):
                    price = base * BOROUGH_MULT[borough] * cumulative
                    noise = np.random.normal(1.0, 0.07)
                    rent = max(500, round(price * noise, 0))

                    start = datetime(year, 1, 1)
                    offset = np.random.randint(0, 365)
                    date = start + timedelta(days=offset)

                    vacancy_rate = max(
                        0.005,
                        0.055 - BOROUGH_MULT[borough] * 0.022
                        + np.random.normal(0, 0.008),
                    )

                    rows.append({
                        "date": date,
                        "year": year,
                        "borough": borough,
                        "unit_type": unit_type,
                        "monthly_rent": rent,
                        "vacancy_rate": round(vacancy_rate, 4),
                    })

    df = pd.DataFrame(rows)
    df["year"] = df["year"].astype("int16")
    df["monthly_rent"] = df["monthly_rent"].astype("float32")
    df["unit_type"] = df["unit_type"].astype("category")
    df["borough"] = df["borough"].astype("category")
    return df


@st.cache_data(show_spinner=False)
def generate_sales_data(n_per_combo: int = 22) -> pd.DataFrame:
    rows = []
    for year in range(2019, 2026):
        cumulative = 1.0
        for y in range(2019, year + 1):
            cumulative *= 1 + ANNUAL_PRICE_GROWTH.get(y, 0.03)

        for borough in BOROUGHS:
            for prop_type, base in BASE_PRICE.items():
                for _ in range(n_per_combo):
                    price = base * BOROUGH_MULT[borough] * cumulative
                    noise = np.random.normal(1.0, 0.11)
                    sale_price = round(max(100_000, price * noise), -3)

                    start = datetime(year, 1, 1)
                    offset = np.random.randint(0, 365)
                    date = start + timedelta(days=offset)

                    dom = max(3, int(np.random.normal(42 / BOROUGH_MULT[borough], 14)))

                    rows.append({
                        "date": date,
                        "year": year,
                        "borough": borough,
                        "property_type": prop_type,
                        "sale_price": sale_price,
                        "days_on_market": dom,
                    })

    df = pd.DataFrame(rows)
    df["year"] = df["year"].astype("int16")
    df["sale_price"] = df["sale_price"].astype("float32")
    df["property_type"] = df["property_type"].astype("category")
    df["borough"] = df["borough"].astype("category")
    return df


# ── Plotly layout defaults ────────────────────────────────────────
def dark_layout(**kwargs) -> dict:
    base = dict(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT_COLOR, family="Inter, sans-serif"),
        xaxis=dict(gridcolor=GRID_COLOR, showline=False, zeroline=False),
        yaxis=dict(gridcolor=GRID_COLOR, showline=False, zeroline=False),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        hoverlabel=dict(bgcolor=CARD_BG, font_size=13),
    )
    base.update(kwargs)
    return base


# ── KPI card helper ───────────────────────────────────────────────
def kpi_card(label: str, value: str, delta: str | None = None, delta_positive: bool | None = None) -> None:
    arrow = ""
    delta_color = "#aaa"
    if delta is not None:
        if delta_positive is True:
            arrow, delta_color = "▲ ", "#26DE81"
        elif delta_positive is False:
            arrow, delta_color = "▼ ", "#FC5C65"
        else:
            arrow, delta_color = "", "#aaa"

    st.markdown(
        f"""
        <div style="
            background:{CARD_BG};
            border:1px solid {GRID_COLOR};
            border-radius:12px;
            padding:20px 24px;
            height:110px;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
        ">
            <p style="margin:0;font-size:12px;color:#8891B4;letter-spacing:.08em;text-transform:uppercase">{label}</p>
            <p style="margin:0;font-size:28px;font-weight:700;color:{TEXT_COLOR};line-height:1.1">{value}</p>
            {"" if delta is None else f'<p style="margin:0;font-size:12px;color:{delta_color}">{arrow}{delta}</p>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Load data ─────────────────────────────────────────────────────
rentals_raw = generate_rental_data()
sales_raw = generate_sales_data()

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:8px 0 20px">
            <span style="font-size:36px">🏙️</span>
            <h2 style="margin:4px 0 0;font-size:18px;color:#E8EAF6">Montreal Housing</h2>
            <p style="margin:0;font-size:11px;color:#8891B4">Market Dashboard · 2019–2025</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Filters")

    selected_boroughs = st.multiselect(
        "Borough",
        options=BOROUGHS,
        default=BOROUGHS,
        help="Filter by one or more Montreal boroughs",
    )

    year_range = st.slider(
        "Year Range",
        min_value=2019,
        max_value=2025,
        value=(2019, 2025),
        step=1,
    )

    selected_unit_types = st.multiselect(
        "Unit Type (Rentals)",
        options=list(BASE_RENT.keys()),
        default=list(BASE_RENT.keys()),
    )

    selected_prop_types = st.multiselect(
        "Property Type (Sales)",
        options=list(BASE_PRICE.keys()),
        default=list(BASE_PRICE.keys()),
    )

    st.divider()

    st.markdown(
        """
        <div style="font-size:11px;color:#8891B4;line-height:1.6">
            <strong style="color:#aaa">⚠️ Data Source Disclaimer</strong><br>
            All data is <em>synthetic</em> and generated programmatically.
            Values are modeled on publicly available ranges from
            <strong>CMHC Rental Market Reports</strong>,
            <strong>Centris Québec</strong>, and
            <strong>Statistics Canada</strong>.
            This dashboard is for portfolio/educational purposes only
            and does not constitute financial or real estate advice.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="margin-top:16px;font-size:11px;color:#8891B4">
            Built by <a href="https://yumorepos.github.io" style="color:#7C83FD" target="_blank">Yumo Xu</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Apply filters ─────────────────────────────────────────────────
if not selected_boroughs:
    selected_boroughs = BOROUGHS
if not selected_unit_types:
    selected_unit_types = list(BASE_RENT.keys())
if not selected_prop_types:
    selected_prop_types = list(BASE_PRICE.keys())

rentals = rentals_raw[
    rentals_raw["borough"].isin(selected_boroughs)
    & rentals_raw["year"].between(*year_range)
    & rentals_raw["unit_type"].isin(selected_unit_types)
].copy()

sales = sales_raw[
    sales_raw["borough"].isin(selected_boroughs)
    & sales_raw["year"].between(*year_range)
    & sales_raw["property_type"].isin(selected_prop_types)
].copy()

# ── KPI computation ───────────────────────────────────────────────
latest_year = year_range[1]
prev_year = max(year_range[0], latest_year - 1)

rent_latest = rentals[rentals["year"] == latest_year]["monthly_rent"].median()
rent_prev = rentals[rentals["year"] == prev_year]["monthly_rent"].median()
rent_yoy = (rent_latest / rent_prev - 1) * 100 if rent_prev > 0 else 0

price_latest = sales[sales["year"] == latest_year]["sale_price"].median()
price_prev = sales[sales["year"] == prev_year]["sale_price"].median()
price_yoy = (price_latest / price_prev - 1) * 100 if price_prev > 0 else 0

vacancy_latest = rentals[rentals["year"] == latest_year]["vacancy_rate"].mean()

# ── Header ────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="font-size:28px;font-weight:700;color:#E8EAF6;margin-bottom:4px">
        🏙️ Montreal Housing Market
    </h1>
    <p style="color:#8891B4;font-size:14px;margin-top:0">
        Rental & sales trends across Montreal boroughs · Synthetic data · 2019–2025
    </p>
    """,
    unsafe_allow_html=True,
)

# ── KPI Row ───────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card(
        f"Avg Monthly Rent ({latest_year})",
        f"${rent_latest:,.0f}",
        delta=f"{rent_yoy:+.1f}% YoY",
        delta_positive=rent_yoy >= 0,
    )
with k2:
    kpi_card(
        f"Median Sale Price ({latest_year})",
        f"${price_latest/1_000:.0f}K" if not np.isnan(price_latest) else "N/A",
        delta=f"{price_yoy:+.1f}% YoY",
        delta_positive=price_yoy >= 0,
    )
with k3:
    kpi_card(
        f"Avg Vacancy Rate ({latest_year})",
        f"{vacancy_latest*100:.2f}%",
        delta="Est. from synthetic data",
        delta_positive=None,
    )
with k4:
    afford_ratio = (rent_latest * 12) / MEDIAN_INCOME.get(latest_year, 61_000) * 100
    above_threshold = afford_ratio > 30
    kpi_card(
        "Rent-to-Income Ratio",
        f"{afford_ratio:.1f}%",
        delta="⚠️ Above 30% CMHC threshold" if above_threshold else "✓ Below 30% threshold",
        delta_positive=not above_threshold,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# CHART ROW 1: Rental Trends + Heatmap
# ═══════════════════════════════════════════════════════════════════
col_left, col_right = st.columns([3, 2], gap="medium")

with col_left:
    st.markdown("#### Median Monthly Rent by Unit Type")

    city_wide = (
        rentals.groupby(["year", "unit_type"], observed=True)["monthly_rent"]
        .median()
        .reset_index()
    )

    fig_trend = px.line(
        city_wide,
        x="year",
        y="monthly_rent",
        color="unit_type",
        markers=True,
        color_discrete_sequence=ACCENT_COLORS,
        labels={"monthly_rent": "Median Rent (CAD/mo)", "year": "Year", "unit_type": "Unit Type"},
    )
    fig_trend.update_traces(line_width=2.5, marker_size=7)
    fig_trend.update_layout(
        **dark_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",",
            xaxis_tickvals=list(range(year_range[0], year_range[1] + 1)),
            legend_title_text="Unit Type",
            height=340,
        )
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.markdown("#### YoY Rent Change by Unit Type")

    city_yoy = (
        rentals_raw.groupby(["year", "unit_type"], observed=True)["monthly_rent"]
        .median()
        .reset_index()
    )
    city_yoy["yoy_pct"] = (
        city_yoy.groupby("unit_type", observed=True)["monthly_rent"]
        .pct_change() * 100
    )
    city_yoy = city_yoy[
        city_yoy["year"].between(*year_range)
        & city_yoy["unit_type"].isin(selected_unit_types)
    ].dropna(subset=["yoy_pct"])

    fig_yoy = px.bar(
        city_yoy,
        x="year",
        y="yoy_pct",
        color="unit_type",
        barmode="group",
        color_discrete_sequence=ACCENT_COLORS,
        labels={"yoy_pct": "YoY Change (%)", "year": "Year", "unit_type": "Unit Type"},
    )
    fig_yoy.add_hline(
        y=0,
        line_dash="dot",
        line_color="#aaa",
        line_width=1,
        annotation_text="0%",
        annotation_font_color="#aaa",
    )
    fig_yoy.update_layout(
        **dark_layout(
            yaxis_ticksuffix="%",
            legend_title_text="Unit Type",
            height=340,
            bargap=0.2,
        )
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# CHART ROW 2: Borough Heatmap
# ═══════════════════════════════════════════════════════════════════
st.markdown("#### Median 2BR Rent by Borough & Year (Heat Map)")

two_br = rentals_raw[
    (rentals_raw["unit_type"] == "2BR")
    & rentals_raw["borough"].isin(selected_boroughs)
    & rentals_raw["year"].between(*year_range)
]
pivot = (
    two_br.pivot_table(index="borough", columns="year", values="monthly_rent", aggfunc="median")
    .sort_values(by=two_br["year"].max(), ascending=False)
)

fig_heat = go.Figure(
    go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale="Viridis",
        colorbar=dict(
            title="CAD/mo",
            tickprefix="$",
            tickformat=",",
            title_font_color=TEXT_COLOR,
            tickfont_color=TEXT_COLOR,
        ),
        hovertemplate="<b>%{y}</b><br>%{x}: $%{z:,.0f}/mo<extra></extra>",
        text=[[f"${v:,.0f}" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont_size=11,
    )
)
fig_heat.update_layout(
    **dark_layout(
        height=380,
        xaxis_title="Year",
        yaxis_title="",
        xaxis=dict(gridcolor=GRID_COLOR, side="bottom"),
        yaxis=dict(gridcolor=GRID_COLOR, autorange="reversed"),
    )
)
st.plotly_chart(fig_heat, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# CHART ROW 3: Borough Comparison + Vacancy Rates
# ═══════════════════════════════════════════════════════════════════
col3, col4 = st.columns(2, gap="medium")

with col3:
    st.markdown(f"#### Borough Rent Comparison ({latest_year})")

    borough_latest = (
        rentals[rentals["year"] == latest_year]
        .groupby("borough", observed=True)["monthly_rent"]
        .median()
        .sort_values(ascending=True)
        .reset_index()
    )

    colors_bar = [
        ACCENT_COLORS[0] if b in ["Old Montreal", "Downtown", "Griffintown"]
        else ACCENT_COLORS[3]
        for b in borough_latest["borough"]
    ]

    fig_bor = go.Figure(
        go.Bar(
            x=borough_latest["monthly_rent"],
            y=borough_latest["borough"],
            orientation="h",
            marker_color=colors_bar,
            hovertemplate="<b>%{y}</b><br>Median rent: $%{x:,.0f}/mo<extra></extra>",
            text=[f"${v:,.0f}" for v in borough_latest["monthly_rent"]],
            textposition="outside",
            textfont=dict(color=TEXT_COLOR, size=11),
        )
    )
    fig_bor.update_layout(
        **dark_layout(
            height=380,
            xaxis_tickprefix="$",
            xaxis_tickformat=",",
            xaxis_title="Median Monthly Rent (CAD)",
            yaxis_title="",
            bargap=0.25,
        )
    )
    st.plotly_chart(fig_bor, use_container_width=True)

with col4:
    st.markdown("#### Estimated Vacancy Rates by Borough")

    vacancy_by_borough = (
        rentals[rentals["year"] == latest_year]
        .groupby("borough", observed=True)["vacancy_rate"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    vacancy_by_borough["pct"] = vacancy_by_borough["vacancy_rate"] * 100

    fig_vac = go.Figure(
        go.Bar(
            x=vacancy_by_borough["pct"],
            y=vacancy_by_borough["borough"],
            orientation="h",
            marker=dict(
                color=vacancy_by_borough["pct"],
                colorscale="RdYlGn",
                showscale=True,
                colorbar=dict(
                    title="Vacancy %",
                    title_font_color=TEXT_COLOR,
                    tickfont_color=TEXT_COLOR,
                    ticksuffix="%",
                ),
            ),
            hovertemplate="<b>%{y}</b><br>Vacancy: %{x:.2f}%<extra></extra>",
            text=[f"{v:.2f}%" for v in vacancy_by_borough["pct"]],
            textposition="outside",
            textfont=dict(color=TEXT_COLOR, size=11),
        )
    )
    fig_vac.update_layout(
        **dark_layout(
            height=380,
            xaxis_ticksuffix="%",
            xaxis_title="Estimated Vacancy Rate",
            yaxis_title="",
            bargap=0.25,
        )
    )
    st.plotly_chart(fig_vac, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# CHART ROW 4: Affordability + Sales Price by Property Type
# ═══════════════════════════════════════════════════════════════════
col5, col6 = st.columns(2, gap="medium")

with col5:
    st.markdown("#### Rent-to-Income Ratio (Affordability)")

    afford_rows = []
    for yr in range(year_range[0], year_range[1] + 1):
        med = rentals_raw[rentals_raw["year"] == yr]["monthly_rent"].median()
        income = MEDIAN_INCOME.get(yr, 61_000)
        ratio = med * 12 / income * 100
        afford_rows.append({"year": yr, "ratio": round(ratio, 1)})
    afford_df = pd.DataFrame(afford_rows)

    bar_colors = [
        "#26DE81" if r < 30 else "#F7B731" if r < 35 else "#FC5C65"
        for r in afford_df["ratio"]
    ]

    fig_afford = go.Figure(
        go.Bar(
            x=afford_df["year"],
            y=afford_df["ratio"],
            marker_color=bar_colors,
            hovertemplate="<b>%{x}</b><br>Rent-to-income: %{y:.1f}%<extra></extra>",
            text=[f"{r:.1f}%" for r in afford_df["ratio"]],
            textposition="outside",
            textfont=dict(color=TEXT_COLOR, size=11),
        )
    )
    fig_afford.add_hline(
        y=30,
        line_dash="dash",
        line_color="#FC5C65",
        line_width=1.5,
        annotation_text="30% CMHC threshold",
        annotation_font_color="#FC5C65",
        annotation_position="top right",
    )
    fig_afford.update_layout(
        **dark_layout(
            height=340,
            yaxis_ticksuffix="%",
            xaxis_tickvals=list(range(year_range[0], year_range[1] + 1)),
            xaxis_title="Year",
            yaxis_title="Rent as % of Median Income",
            bargap=0.3,
        )
    )
    st.plotly_chart(fig_afford, use_container_width=True)

with col6:
    st.markdown(f"#### Median Sale Price by Property Type ({latest_year})")

    sales_summary = (
        sales[sales["year"] == latest_year]
        .groupby("property_type", observed=True)["sale_price"]
        .median()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_sales = px.bar(
        sales_summary,
        x="property_type",
        y="sale_price",
        color="property_type",
        color_discrete_sequence=ACCENT_COLORS,
        labels={"sale_price": "Median Sale Price (CAD)", "property_type": "Property Type"},
        text=[f"${v/1_000:.0f}K" for v in sales_summary["sale_price"]],
    )
    fig_sales.update_traces(textposition="outside", textfont_color=TEXT_COLOR)
    fig_sales.update_layout(
        **dark_layout(
            height=340,
            yaxis_tickprefix="$",
            yaxis_tickformat=",",
            showlegend=False,
            xaxis_title="",
            bargap=0.3,
        )
    )
    st.plotly_chart(fig_sales, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# CHART ROW 5: Days on Market over time
# ═══════════════════════════════════════════════════════════════════
st.markdown("#### Average Days on Market — City-Wide vs. Selected Boroughs")

top_boroughs_dom = ["Old Montreal", "Downtown", "Plateau-Mont-Royal", "Hochelaga"]
highlight = [b for b in top_boroughs_dom if b in selected_boroughs]

dom_city = (
    sales_raw[sales_raw["year"].between(*year_range)]
    .groupby("year")["days_on_market"]
    .mean()
    .reset_index()
)

fig_dom = go.Figure()
fig_dom.add_trace(
    go.Scatter(
        x=dom_city["year"],
        y=dom_city["days_on_market"],
        mode="lines+markers",
        name="City Average",
        line=dict(color="#E8EAF6", width=3),
        marker=dict(size=8, symbol="square"),
        fill="tozeroy",
        fillcolor="rgba(124,131,253,0.08)",
        hovertemplate="<b>City Average</b><br>%{x}: %{y:.1f} days<extra></extra>",
    )
)

for i, borough in enumerate(highlight):
    dom_b = (
        sales_raw[
            (sales_raw["borough"] == borough)
            & sales_raw["year"].between(*year_range)
        ]
        .groupby("year")["days_on_market"]
        .mean()
        .reset_index()
    )
    fig_dom.add_trace(
        go.Scatter(
            x=dom_b["year"],
            y=dom_b["days_on_market"],
            mode="lines+markers",
            name=borough,
            line=dict(color=ACCENT_COLORS[i % len(ACCENT_COLORS)], width=2, dash="dot"),
            marker=dict(size=6),
            hovertemplate=f"<b>{borough}</b><br>%{{x}}: %{{y:.1f}} days<extra></extra>",
        )
    )

fig_dom.update_layout(
    **dark_layout(
        height=320,
        xaxis_tickvals=list(range(year_range[0], year_range[1] + 1)),
        xaxis_title="Year",
        yaxis_title="Avg Days on Market",
        legend_title_text="Borough",
    )
)
st.plotly_chart(fig_dom, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    """
    <div style="text-align:center;font-size:12px;color:#8891B4;padding:8px 0">
        Montreal Housing Market Dashboard · Synthetic data only · Built with
        <a href="https://streamlit.io" style="color:#7C83FD" target="_blank">Streamlit</a> &
        <a href="https://plotly.com" style="color:#7C83FD" target="_blank">Plotly</a> ·
        <a href="https://yumorepos.github.io" style="color:#7C83FD" target="_blank">Yumo Xu</a>
    </div>
    """,
    unsafe_allow_html=True,
)
