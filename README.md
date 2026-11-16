# Sales Analysis ETL Pipeline

A small data pipeline that takes the Sample Superstore sales data, cleans it with Python, stores it in a SQL database, and finds out where the business makes and loses money.

**ETL** means **E**xtract (read the data), **T**ransform (clean it), **L**oad (save it). I run all three steps with one command.

## What this project does

1. **Extract:** reads the raw CSV (9,994 rows, one row per product line in an order).
2. **Transform:** fixes dates and postal codes, and adds three new columns (Order Year, Order Month, Shipping Days).
3. **Load:** saves a clean CSV and a SQLite database with a `sales` table.
4. **SQL checks:** runs 7 data quality checks. Every check passes with 0 bad rows.
5. **SQL cleaning:** builds a `sales_clean` table with three extra columns: `discount_pct`, `profit_margin` and `discount_band`.

## Tools used

Python 3.13, pandas, SQLite (sqlite3), SQL, Jupyter notebooks, Git and GitHub.

## Data

Sample Superstore dataset from Kaggle. It has 21 original columns, 4 regions, 17 sub-categories and orders from 2014 to 2017.

## Key findings

**Yearly sales** grew over time, with a small dip in 2015.

| Year | Sales |
|------|-------|
| 2014 | about 484K |
| 2015 | about 471K |
| 2016 | about 609K |
| 2017 | about 733K |

**Regions:** the West makes the most profit. The Central region keeps the least, about 8 profit for every 100 sold.

| Region | Sales | Profit |
|--------|-------|--------|
| West | 725K | 108K |
| East | 679K | 92K |
| Central | 501K | 40K |
| South | 392K | 47K |

**Products:**
- Tables lost about 17.7K (average discount 26%).
- Bookcases lost about 3.5K and Supplies lost about 1.2K.
- Machines sold 189K but made only about 3.4K profit (average discount 31%).
- Copiers made the most profit, about 55.6K.

**Discounts:**
- Items sold with 0% to 20% discount made about 421K profit in total.
- Every discount level from 30% up lost money: about 1,393 items lost about 135K in total.
- Tables with no discount made about 13.3K profit, but Tables sold at 30% off or more lost about 31K.

**In short:** in this data, deep discounts are where the money is lost, and the worst hit are Tables and Machines.

## Project structure

```text
Sales-Analysis-ETL-Pipeline/
├── data/
│   ├── raw/          # original superstore.csv
│   └── processed/    # superstore_clean.csv
├── notebooks/
│   ├── 01_extract_and_explore.ipynb
│   └── 02_sql_analysis.ipynb
├── src/
│   └── etl.py        # runs the whole pipeline
├── sql/
│   ├── 01_data_quality_checks.sql
│   └── 02_create_sales_clean.sql
├── dags/             # Airflow DAG (coming)
├── powerbi/          # dashboard (coming)
└── tests/
```

## How to run it

1. Download or clone the project.
2. Make and turn on a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install pandas jupyter
```

3. Run the pipeline:

```powershell
python src/etl.py
```

This rebuilds the database `data/superstore.db` (it stays on my computer and is not uploaded to GitHub) and the clean CSV.

## What's next

- [x] Notebook 01: extract, transform, load
- [x] Notebook 02: SQL analysis
- [x] ETL script in `src/etl.py`
- [x] SQL quality checks and `sales_clean` table
- [ ] Power BI dashboard
- [ ] Apache Airflow DAG to run the pipeline automatically

## Author

Mary. GitHub: [marywarimi](https://github.com/marywarimi)