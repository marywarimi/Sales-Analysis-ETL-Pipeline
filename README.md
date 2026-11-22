# Sales Analysis ETL Pipeline

A  data pipeline that takes the Sample Superstore sales data, cleans it with Python, stores it in a SQL database, and finds out where the business makes and loses money. Apache Airflow runs the pipeline automatically, and a Power BI dashboard shows the results.

**ETL** means **E**xtract (read the data), **T**ransform (clean it), **L**oad (save it). I run all three steps with one command.

## What this project does

1. **Extract:** reads the raw CSV (9,994 rows, one row per product line in an order).
2. **Transform:** fixes dates and postal codes, and adds three new columns (Order Year, Order Month, Shipping Days).
3. **Load:** saves a clean CSV and a SQLite database with a `sales` table.
4. **SQL checks:** runs 7 data quality checks. Every check passes with 0 bad rows.
5. **SQL cleaning:** builds a `sales_clean` table with three extra columns: `discount_pct`, `profit_margin` and `discount_band`.

An **Apache Airflow** DAG runs these steps in order, once a day. A **Power BI** dashboard shows the findings.

## Tools used

Python, pandas, SQLite (sqlite3), SQL, Jupyter notebooks, Apache Airflow 3.4 (running in WSL2 Ubuntu), Power BI Desktop, Git and GitHub.

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

## Power BI dashboard

I built the dashboard from `data/processed/superstore_clean.csv`.

![Superstore sales dashboard](powerbi/dashboard.jpeg)

It has 4 charts and a region filter:

- **Sales by year:** sales grew from 2014 to 2017, with a small dip in 2015.
- **Profit by region:** the West makes the most profit and the Central region the least.
- **Profit by sub-category:** the red bars show the products that lose money (Tables, Bookcases and Supplies).
- **Profit by discount level:** profit falls below zero at every discount level of 30% and above.
- **Region slicer:** click a region to filter the charts.

The file is `powerbi/superstore_dashboard.pbix` and it opens in Power BI Desktop.

## Automation with Apache Airflow

Apache Airflow runs the pipeline for me, in order, without typing any commands. The DAG is in `dags/sales_etl_dag.py` and is called `sales_etl_pipeline`.

It has 4 tasks, one after the other:

1. `extract_data`: runs `extract()` from `src/etl.py`
2. `transform_data`: runs `transform(df)`
3. `load_data`: runs `load(df)`
4. `clean_data`: runs `clean_with_sql()` (7 quality checks, then the `sales_clean` table)

Airflow tasks run separately, so each task saves its table to a temporary file (`/tmp/sales_etl`) for the next task to read. The DAG calls the functions already in `src/etl.py`, so `python src/etl.py` still works on its own. The DAG runs once a day (`@daily`) and does not run the missed days (`catchup=False`).

All 4 tasks finish successfully, in about 27 seconds for the whole run.

### How to run it with Airflow

Airflow does not run on plain Windows, so I use **WSL2** (Linux inside Windows) with Ubuntu. Inside Ubuntu:

```bash
# 1. Tools and a virtual environment
sudo apt update
sudo apt install -y python3-venv python3-pip
python3 -m venv ~/airflow-venv
source ~/airflow-venv/bin/activate

# 2. Install Airflow and pandas with the official constraints file
AIRFLOW_VERSION=3.4.0
PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
pip install pandas --constraint "${CONSTRAINT_URL}"

# 3. Point Airflow at this project's dags folder (change YOUR_NAME)
sed -i 's|^dags_folder = .*|dags_folder = /mnt/c/Users/YOUR_NAME/Desktop/Sales-Analysis-ETL-Pipeline/dags|' ~/airflow/airflow.cfg

# 4. Start Airflow
airflow standalone
```

Then:

1. Open `http://localhost:8080` in a browser.
2. Log in with the username `admin` and the password saved in `~/airflow/simple_auth_manager_passwords.json.generated`.
3. Find `sales_etl_pipeline`, switch it on, and click **Trigger**.

This is a local setup, so the daily schedule only runs while Airflow is running on my computer.

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
├── dags/
│   └── sales_etl_dag.py   # Airflow DAG
├── powerbi/
│   ├── superstore_dashboard.pbix
│   └── dashboard.jpeg
└── tests/            # coming
```

## How to run it (without Airflow)

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
- [x] Power BI dashboard
- [x] Apache Airflow DAG to run the pipeline automatically
- [ ] Add tests with pytest

## Author

Mary. GitHub: [marywarimi](https://github.com/marywarimi)