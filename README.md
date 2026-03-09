# 🏠 Montreal Housing Dashboard

> **🔴 Live:** [montreal-housing-dashboard-rdjsnh9h6wxxlkczmbfbcq.streamlit.app](https://montreal-housing-dashboard-rdjsnh9h6wxxlkczmbfbcq.streamlit.app)


An interactive data dashboard exploring **rental prices**, **home sale trends**, **affordability**, and **vacancy rates** across Montreal's diverse boroughs — built with Streamlit and Plotly.

> **Data disclaimer:** All data is synthetic and generated programmatically, modeled on publicly available ranges from CMHC Rental Market Reports, Centris Québec, and Statistics Canada. This project is for portfolio and educational purposes only.

---

## Screenshots

> *Run the app locally (`streamlit run app.py`) to see the full interactive dashboard.*

| KPI Cards & Rental Trends | Borough Heatmap |
|:---:|:---:|
| *Avg rent · Median sale price · Vacancy rate · Affordability ratio* | *Median 2BR rent by borough × year* |

| Borough Comparison | Vacancy Rates |
|:---:|:---:|
| *Horizontal bar — ranked by median rent* | *RdYlGn colour scale* |

---

## Features

- **4 KPI cards** — Avg rent, median sale price, vacancy rate, rent-to-income ratio with YoY delta
- **Rental trend chart** — City-wide median rent by unit type (Studio → 3BR), 2019–2025
- **YoY change chart** — Grouped bar showing annual rent growth rates
- **Borough heatmap** — Median 2BR rent across all boroughs and years
- **Borough comparison** — Ranked horizontal bar for the selected year
- **Vacancy rates** — Colour-coded vacancy estimates by borough
- **Affordability gauge** — Rent-to-income ratio vs. 30% CMHC threshold
- **Sale price by property type** — Condo, Duplex, Single-Family, Triplex
- **Days on market** — City average + borough highlights over time
- **Sidebar filters** — Borough, year range, unit type, property type

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Streamlit](https://streamlit.io) ≥ 1.32 |
| Charts | [Plotly](https://plotly.com/python/) ≥ 5.20 |
| Data | [Pandas](https://pandas.pydata.org) ≥ 2.0 · [NumPy](https://numpy.org) ≥ 1.24 |
| Styling | Custom dark theme via `.streamlit/config.toml` + inline CSS |
| Container | Docker (Python 3.11-slim) |
| Language | Python 3.11+ |

---

## Quick Start

### Local (Python)

```bash
# 1. Clone
git clone https://github.com/yumorepos/montreal-housing-dashboard.git
cd montreal-housing-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### Docker

```bash
# Build
docker build -t montreal-housing .

# Run
docker run -p 8501:8501 montreal-housing
```

Open `http://localhost:8501`.

---

## Project Structure

```
montreal-housing-dashboard/
├── app.py                  # Main Streamlit dashboard
├── analysis.py             # Original analysis script (matplotlib/seaborn)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── .streamlit/
│   └── config.toml         # Dark theme + server config
└── README.md
```

---

## Data Model

The synthetic dataset covers **2019–2025** across **10 Montreal boroughs**:

| Boroughs | Unit Types | Property Types |
|---|---|---|
| Plateau-Mont-Royal, Mile End, Griffintown, Verdun, NDG, Rosemont, Villeray, Hochelaga, Old Montreal, Downtown | Studio, 1BR, 2BR, 3BR | Condo, Duplex, Single-Family, Triplex |

Annual rent increases are modeled on historical market dynamics: pre-pandemic baseline (2.2%), pandemic suppression (1.8%), early recovery (2.5%), surge years (5.5–6.5%), and gradual normalization. Borough premium multipliers range from 0.87× (Hochelaga) to 1.38× (Old Montreal).

---

## Author

**Yumo Xu** · [yumorepos.github.io](https://yumorepos.github.io)
