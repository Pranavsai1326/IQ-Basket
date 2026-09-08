# IQ Basket

An end-to-end local data analytics project: two real Kaggle e-commerce
datasets, cleaned with Pandas, loaded into SQLite, analyzed with SQL,
and visualized in an interactive Streamlit + Plotly dashboard with a
branded animated preloader and UI transitions.

## Business Questions

- What is total revenue and average purchase amount per product category?
- Which payment method is most popular within each age group?
- How does revenue trend month over month?
- Which locations/countries generate the most spending?
- How does purchase frequency relate to revenue?
- How does revenue differ by gender?

## Architecture

```text
Kaggle → KaggleHub → Raw CSV → Pandas Cleaning → Clean CSV
       → SQLite (ecommerce_analytics.db) → SQL Analytics
       → Streamlit + Plotly Dashboard
```

## Datasets

| Dataset | Kaggle ID | Rows (raw) | Notes |
|---|---|---|---|
| Customer Shopping Trends | `iamsouravbanerjee/customer-shopping-trends-dataset` | 3,900 | No purchase-date column in the real schema |
| Online Retail | `vijayuv/onlineretail` | 541,909 | UK-based transactional invoice data, 2010-2011 |

## Technology Stack

Python, Pandas, NumPy, KaggleHub, SQLite, SQL, Plotly, Streamlit.

## Folder Structure

```text
iq-basket/
├── data/
│   ├── raw/            # raw CSVs pulled via KaggleHub (gitignored)
│   └── cleaned/        # cleaned CSVs (gitignored)
├── scripts/
│   ├── 01_load_and_inspect.py
│   ├── 02_clean_data.py
│   └── 03_load_database.py
├── sql/
│   └── analysis_queries.sql
├── dashboard/
│   └── app.py
├── ecommerce_analytics.db
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

```bash
pip install -r requirements.txt
```

## Run the ETL Pipeline

```bash
python scripts/01_load_and_inspect.py
python scripts/02_clean_data.py
python scripts/03_load_database.py
```

## Run SQL Analysis

Open `sql/analysis_queries.sql` in any SQLite client (e.g. `sqlite3
ecommerce_analytics.db`) and run the queries, or use the dashboard,
which runs equivalent aggregations directly against the same tables.

## Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

Then open the URL Streamlit prints (typically `http://localhost:8501`).

## Key Analytics Performed

- Revenue and average purchase amount by product category
- Most popular payment method per age group (`CASE` + `RANK()`)
- Monthly revenue trend (Online Retail; Customer Shopping Trends has no date field)
- Location spending rank (`DENSE_RANK()`)
- Purchase frequency segmentation
- Revenue by gender and by location
- Top international countries by revenue (Online Retail, excluding UK)

## Dashboard Features

- **KPI cards**: Total Revenue, Active Customers, Average Order Value
- **Charts**: category bar chart, payment-method donut chart, monthly
  revenue line chart (Online Retail view), purchase-frequency and
  top-locations charts
- **Filters**: Location and Gender (Customer Behavior view)
- **Dataset switcher**: Customer Behavior (primary) vs. Online Retail
- **Animated UI**: branded "IQ Basket" preloader on first load, gradient
  title, fade-in/slide-up transitions, and hover-lift effects on KPI
  cards and charts

## Important Data Note

The Customer Shopping Trends dataset does not include a purchase-date
column in its actual Kaggle schema (verified by inspection). The
monthly revenue trend chart is therefore shown only for the Online
Retail dataset, which does have transaction dates.

## Future Improvements

- Add a date field to the Customer Shopping Trends analysis if a
  future dataset version provides one
- Add cohort/retention analysis for Online Retail
- Add CSV export of filtered dashboard results
