"""
Montreal Housing Market Analysis
================================
A data analysis project exploring rental and housing price trends
across Montreal boroughs using synthetic data modeled on real market ranges.

Author: Yumo Xu
Portfolio: yumorepos.github.io
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# ── Config ──────────────────────────────────────────────────────
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
    "font.family": "sans-serif",
    "axes.titlesize": 14,
    "axes.labelsize": 12,
})

SEED = 42
np.random.seed(SEED)


# ── Data Generation ─────────────────────────────────────────────
# Synthetic data modeled on real Montreal rental/housing market ranges (2019-2025)
# Sources referenced: CMHC Rental Market Reports, Centris Quebec, StatCan

BOROUGHS = [
    "Plateau-Mont-Royal",  # trendy, high demand
    "Mile End",            # artsy, popular with young professionals
    "Griffintown",         # new development corridor
    "Verdun",              # up-and-coming, riverside
    "NDG",                 # Notre-Dame-de-Grâce, family-friendly
    "Rosemont",            # residential, growing demand
    "Villeray",            # north-central, affordable-ish
    "Hochelaga",           # east-end, gentrifying
    "Old Montreal",        # historic core, premium
    "Downtown",            # Ville-Marie, highest density
]

# Base monthly rent by unit type (CAD, 2019 baseline — pre-pandemic)
# Ranges reflect realistic 2024-2025 Montreal market after compounding increases
BASE_RENT = {
    "Studio": 1050,   # targets ~$1,400 by 2024-25
    "1BR":    1500,   # targets ~$2,000 by 2024-25
    "2BR":    1900,   # targets ~$2,500 by 2024-25
    "3BR":    2450,   # targets ~$3,200 by 2024-25
}

# Borough premium multiplier (1.0 = city average)
BOROUGH_MULT = {
    "Plateau-Mont-Royal": 1.18,
    "Mile End":           1.15,
    "Griffintown":        1.20,
    "Verdun":             0.94,
    "NDG":                1.00,
    "Rosemont":           1.05,
    "Villeray":           0.96,
    "Hochelaga":          0.87,
    "Old Montreal":       1.38,
    "Downtown":           1.32,
}

# Annual rent increase rates (compounding) — reflects pre-pandemic stability,
# pandemic shock, then sustained pressure
ANNUAL_INCREASES = {
    2019: 0.022,  # pre-pandemic baseline growth
    2020: 0.018,  # pandemic suppression
    2021: 0.025,  # early recovery
    2022: 0.055,  # surge: tight supply + inflation
    2023: 0.065,  # peak pressure
    2024: 0.042,  # slight easing
    2025: 0.032,  # normalizing
}


def generate_rental_data(n_per_combo: int = 35) -> pd.DataFrame:
    """Generate synthetic Montreal rental listings.

    Produces rows for every (year, borough, unit_type) combination with
    realistic rent values, a simulated listing date, and a vacancy-rate proxy.
    """
    rows = []
    for year in range(2019, 2026):
        # Cumulative rent multiplier relative to 2019 base
        cumulative = 1.0
        for y in range(2019, year + 1):
            cumulative *= (1 + ANNUAL_INCREASES.get(y, 0.03))

        for borough in BOROUGHS:
            for unit_type, base in BASE_RENT.items():
                for _ in range(n_per_combo):
                    # Price: base × borough premium × time growth × noise
                    price = base * BOROUGH_MULT[borough] * cumulative
                    noise = np.random.normal(1.0, 0.07)
                    rent = max(500, round(price * noise, 0))

                    # Random listing date within the year
                    start = datetime(year, 1, 1)
                    offset = np.random.randint(0, 365)
                    date = start + timedelta(days=offset)

                    # Vacancy proxy: lower in high-demand boroughs
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
    # Cast types for memory efficiency
    df["year"] = df["year"].astype("int16")
    df["monthly_rent"] = df["monthly_rent"].astype("float32")
    df["unit_type"] = df["unit_type"].astype("category")
    df["borough"] = df["borough"].astype("category")
    return df


def generate_sales_data(n_per_combo: int = 22) -> pd.DataFrame:
    """Generate synthetic Montreal home sales data.

    Simulates condo, duplex, single-family, and triplex transactions
    with price growth, borough premiums, and days-on-market signals.
    """
    # Median sale prices by property type (2019 baseline, CAD)
    BASE_PRICE = {
        "Condo":         310_000,
        "Duplex":        490_000,
        "Single-Family": 425_000,
        "Triplex":       640_000,
    }

    # Year-over-year price growth — Montreal experienced outsized gains 2020-22
    ANNUAL_PRICE_GROWTH = {
        2019:  0.04,
        2020:  0.06,
        2021:  0.15,  # pandemic frenzy
        2022:  0.09,
        2023: -0.03,  # rate-hike correction
        2024:  0.04,
        2025:  0.05,
    }

    rows = []
    for year in range(2019, 2026):
        cumulative = 1.0
        for y in range(2019, year + 1):
            cumulative *= (1 + ANNUAL_PRICE_GROWTH.get(y, 0.03))

        for borough in BOROUGHS:
            for prop_type, base in BASE_PRICE.items():
                for _ in range(n_per_combo):
                    price = base * BOROUGH_MULT[borough] * cumulative
                    noise = np.random.normal(1.0, 0.11)
                    sale_price = round(max(100_000, price * noise), -3)

                    start = datetime(year, 1, 1)
                    offset = np.random.randint(0, 365)
                    date = start + timedelta(days=offset)

                    # Days on market: shorter in expensive/hot boroughs
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


# ── Analysis Functions ──────────────────────────────────────────

def analyze_rental_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Compute yearly rental stats aggregated by borough and unit type."""
    stats = (
        df.groupby(["year", "borough", "unit_type"], observed=True)["monthly_rent"]
        .agg(["median", "mean", "std", "count"])
        .reset_index()
    )
    stats.columns = ["year", "borough", "unit_type", "median_rent", "mean_rent", "std_rent", "listings"]
    return stats


def compute_yoy(df: pd.DataFrame) -> pd.DataFrame:
    """Compute year-over-year rent change by unit type."""
    city_wide = (
        df.groupby(["year", "unit_type"], observed=True)["monthly_rent"]
        .median()
        .reset_index()
    )
    city_wide["yoy_pct"] = city_wide.groupby("unit_type", observed=True)["monthly_rent"].pct_change() * 100
    return city_wide


def compute_affordability(rental_df: pd.DataFrame) -> pd.DataFrame:
    """Compute rent-to-income ratio vs. Montreal median household income.

    The 30% threshold (rent/income) is the standard CMHC affordability benchmark.
    """
    # Montreal median household income (CAD, approximated from StatCan data)
    MEDIAN_INCOME = {
        2019: 50_000,
        2020: 51_500,
        2021: 53_000,
        2022: 56_000,
        2023: 58_500,
        2024: 61_000,
        2025: 63_500,
    }

    yearly = rental_df.groupby("year")["monthly_rent"].median().reset_index()
    yearly.columns = ["year", "median_rent"]
    yearly["annual_rent"] = yearly["median_rent"] * 12
    yearly["median_income"] = yearly["year"].map(MEDIAN_INCOME)
    yearly["rent_to_income"] = (yearly["annual_rent"] / yearly["median_income"] * 100).round(1)
    return yearly


# ── Visualization Functions ─────────────────────────────────────

def plot_rent_trends(stats: pd.DataFrame) -> None:
    """Line chart: city-wide median rent by unit type, 2019–2025."""
    city_wide = stats.groupby(["year", "unit_type"], observed=True)["median_rent"].median().reset_index()

    fig, ax = plt.subplots()
    palette = sns.color_palette("tab10", n_colors=len(BASE_RENT))
    for (unit_type, color) in zip(BASE_RENT.keys(), palette):
        subset = city_wide[city_wide["unit_type"] == unit_type]
        ax.plot(subset["year"], subset["median_rent"], marker="o", linewidth=2.2,
                label=unit_type, color=color)

    ax.set_title("Montreal Median Monthly Rent by Unit Type (2019–2025)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Monthly Rent (CAD)")
    ax.legend(title="Unit Type", framealpha=0.9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_xticks(range(2019, 2026))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/01_rent_trends.png")
    plt.close()
    print("  ✓ Saved 01_rent_trends.png")


def plot_borough_comparison(stats: pd.DataFrame) -> None:
    """Heatmap: median 2BR rent by borough and year."""
    two_br = stats[stats["unit_type"] == "2BR"]
    pivot = two_br.pivot_table(index="borough", columns="year", values="median_rent", aggfunc="median")
    pivot = pivot.sort_values(by=pivot.columns[-1], ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(
        pivot, annot=True, fmt=",.0f", cmap="YlOrRd",
        linewidths=0.5, linecolor="white", ax=ax,
        cbar_kws={"label": "Median Rent (CAD/mo)"},
    )
    ax.set_title("Median 2BR Monthly Rent by Borough — Montreal (2019–2025)")
    ax.set_xlabel("Year")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/02_borough_heatmap.png")
    plt.close()
    print("  ✓ Saved 02_borough_heatmap.png")


def plot_affordability(afford_df: pd.DataFrame) -> None:
    """Bar chart: rent-to-income ratio over time with 30% threshold line."""
    fig, ax = plt.subplots()
    colors = [
        "#2ecc71" if r < 30 else "#f39c12" if r < 35 else "#e74c3c"
        for r in afford_df["rent_to_income"]
    ]
    bars = ax.bar(
        afford_df["year"], afford_df["rent_to_income"],
        color=colors, edgecolor="white", linewidth=0.8, width=0.6,
    )

    ax.axhline(y=30, color="#c0392b", linestyle="--", linewidth=1.5,
               label="30% affordability threshold (CMHC)")
    ax.set_title("Montreal Rent-to-Income Ratio (2019–2025)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Rent as % of Median Household Income")
    ax.legend(framealpha=0.9)
    ax.set_xticks(afford_df["year"])

    for bar, val in zip(bars, afford_df["rent_to_income"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f"{val}%", ha="center", va="bottom", fontsize=10, fontweight="bold",
        )

    ax.set_ylim(0, max(afford_df["rent_to_income"]) + 6)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/03_affordability.png")
    plt.close()
    print("  ✓ Saved 03_affordability.png")


def plot_sales_distribution(sales_df: pd.DataFrame) -> None:
    """Violin plot: sale price distribution by property type (2025)."""
    recent = sales_df[sales_df["year"] == 2025].copy()

    # Sort by median sale price for a cleaner chart
    order = (
        recent.groupby("property_type", observed=True)["sale_price"]
        .median()
        .sort_values()
        .index.tolist()
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(
        data=recent, x="property_type", y="sale_price",
        order=order, palette="Set2", inner="box", ax=ax,
    )
    ax.set_title("Montreal Sale Price Distribution by Property Type (2025)")
    ax.set_xlabel("Property Type")
    ax.set_ylabel("Sale Price (CAD)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/04_sales_distribution.png")
    plt.close()
    print("  ✓ Saved 04_sales_distribution.png")


def plot_days_on_market(sales_df: pd.DataFrame) -> None:
    """Line chart: average days on market per year with borough breakout."""
    dom_annual = sales_df.groupby("year")["days_on_market"].mean().reset_index()

    # Also compute for top-4 boroughs to show variance
    top_boroughs = ["Old Montreal", "Downtown", "Plateau-Mont-Royal", "Hochelaga"]
    dom_borough = (
        sales_df[sales_df["borough"].isin(top_boroughs)]
        .groupby(["year", "borough"], observed=True)["days_on_market"]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots()
    ax.plot(
        dom_annual["year"], dom_annual["days_on_market"],
        marker="s", linewidth=2.8, color="#2c3e50", markersize=8, label="City average",
    )
    ax.fill_between(dom_annual["year"], dom_annual["days_on_market"], alpha=0.12, color="#2c3e50")

    palette = sns.color_palette("pastel", n_colors=len(top_boroughs))
    for borough, color in zip(top_boroughs, palette):
        subset = dom_borough[dom_borough["borough"] == borough]
        ax.plot(subset["year"], subset["days_on_market"], linestyle="--",
                linewidth=1.4, color=color, label=borough, alpha=0.85)

    ax.set_title("Average Days on Market — Montreal (2019–2025)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Days on Market")
    ax.legend(title="Borough", framealpha=0.9, fontsize=9)
    ax.set_xticks(range(2019, 2026))
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/05_days_on_market.png")
    plt.close()
    print("  ✓ Saved 05_days_on_market.png")


# ── Main ────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Montreal Housing Market Analysis")
    print("=" * 60)

    # ── Generate data ──
    print("\n📊 Generating synthetic dataset...")
    rentals = generate_rental_data()
    sales = generate_sales_data()
    print(f"  Rental listings: {len(rentals):,}")
    print(f"  Sales records:   {len(sales):,}")

    # Save raw datasets for downstream use
    rentals.to_csv(f"{OUTPUT_DIR}/rentals.csv", index=False)
    sales.to_csv(f"{OUTPUT_DIR}/sales.csv", index=False)
    print(f"  ✓ Raw data saved to {OUTPUT_DIR}/")

    # ── Rental analysis ──
    print("\n📈 Rental market analysis...")
    rental_stats = analyze_rental_trends(rentals)

    city_median = rentals.groupby("year")["monthly_rent"].median()
    yoy_change = city_median.pct_change() * 100

    print(f"\n  City-wide median rent by year:")
    for yr, med in city_median.items():
        chg = yoy_change[yr]
        chg_str = f"  ({chg:+.1f}% YoY)" if not pd.isna(chg) else ""
        print(f"    {yr}: ${med:,.0f}/mo{chg_str}")

    five_yr_increase = (city_median.iloc[-1] / city_median.iloc[0] - 1) * 100
    print(f"\n  6-year rent increase (2019→2025): {five_yr_increase:.1f}%")
    print(f"  2025 YoY change: {yoy_change.iloc[-1]:+.1f}%")

    # Borough spread
    borough_2025 = (
        rentals[rentals["year"] == 2025]
        .groupby("borough", observed=True)["monthly_rent"]
        .median()
        .sort_values(ascending=False)
    )
    print(f"\n  Most expensive borough:  {borough_2025.index[0]} (${borough_2025.iloc[0]:,.0f}/mo)")
    print(f"  Least expensive borough: {borough_2025.index[-1]} (${borough_2025.iloc[-1]:,.0f}/mo)")
    print(f"  Spread: ${borough_2025.iloc[0] - borough_2025.iloc[-1]:,.0f}/mo")

    # 2025 median rents by unit type
    print("\n  2025 median rent by unit type:")
    for ut, grp in rentals[rentals["year"] == 2025].groupby("unit_type", observed=True):
        print(f"    {ut:7s}: ${grp['monthly_rent'].median():,.0f}/mo")

    # ── Affordability ──
    print("\n💰 Affordability metrics...")
    affordability = compute_affordability(rentals)
    latest = affordability.iloc[-1]
    print(f"  2025 rent-to-income ratio: {latest['rent_to_income']}%")
    if latest["rent_to_income"] > 30:
        print("  ⚠️  Above 30% CMHC threshold — housing stress for median-income households")

    # ── Sales market ──
    print("\n🏠 Sales market summary (2025)...")
    sales_2025 = sales[sales["year"] == 2025]
    for prop_type in ["Condo", "Duplex", "Single-Family", "Triplex"]:
        med = sales_2025[sales_2025["property_type"] == prop_type]["sale_price"].median()
        print(f"  {prop_type:15s} median: ${med:>12,.0f}")

    avg_dom = sales_2025["days_on_market"].mean()
    total_growth = (
        sales.groupby("year")["sale_price"].median().iloc[-1]
        / sales.groupby("year")["sale_price"].median().iloc[0] - 1
    ) * 100
    print(f"\n  Average days on market (2025): {avg_dom:.0f} days")
    print(f"  Median sale price growth (2019→2025): {total_growth:.1f}%")

    # Vacancy proxy summary
    mean_vacancy = rentals.groupby("borough", observed=True)["vacancy_rate"].mean().sort_values()
    print(f"\n  Lowest vacancy (est.): {mean_vacancy.index[0]} ({mean_vacancy.iloc[0]*100:.1f}%)")
    print(f"  Highest vacancy (est.): {mean_vacancy.index[-1]} ({mean_vacancy.iloc[-1]*100:.1f}%)")

    # ── Visualizations ──
    print("\n🎨 Generating visualizations...")
    plot_rent_trends(rental_stats)
    plot_borough_comparison(rental_stats)
    plot_affordability(affordability)
    plot_sales_distribution(sales)
    plot_days_on_market(sales)

    print("\n" + "=" * 60)
    print("  Analysis complete! See output/ for charts and data.")
    print("=" * 60)


if __name__ == "__main__":
    main()
