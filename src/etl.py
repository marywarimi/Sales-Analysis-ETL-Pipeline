# ---------- PART 1: TOOLS AND SETTINGS ----------

from pathlib import Path   # Path helps us build file locations safely on Windows
import sqlite3             # sqlite3 lets Python talk to the database
import pandas as pd        # pandas is our table tool

PROJECT_FOLDER = Path(__file__).resolve().parent.parent  # the main project folder

RAW_CSV = PROJECT_FOLDER / "data" / "raw" / "superstore.csv"                  # raw data file
CLEAN_CSV = PROJECT_FOLDER / "data" / "processed" / "superstore_clean.csv"    # clean CSV file
DATABASE = PROJECT_FOLDER / "data" / "superstore.db"                          # database file
SQL_FOLDER = PROJECT_FOLDER / "sql"                                           # NEW: where the .sql files live


# ---------- PART 2: EXTRACT (read the raw file) ----------

def extract():
    df = pd.read_csv(RAW_CSV, encoding="latin-1")       # read the CSV into df
    print("Extracted:", df.shape[0], "rows and", df.shape[1], "columns")
    return df


# ---------- PART 3: TRANSFORM (clean the table) ----------

def transform(df):
    print("Duplicate rows:", df.duplicated().sum())     # count repeated rows
    df = df.drop_duplicates()                           # remove repeats

    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")  # text -> real date
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

    df["Postal Code"] = df["Postal Code"].astype(str).str.zfill(5)          # 5-digit text

    print("Ship before order:", (df["Ship Date"] < df["Order Date"]).sum())

    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

    print("Transformed:", df.shape[0], "rows and", df.shape[1], "columns")
    return df


# ---------- PART 4: LOAD (save the clean table) ----------

def load(df):
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")

    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_CSV, index=False)

    conn = sqlite3.connect(DATABASE)
    df.to_sql("sales", conn, if_exists="replace", index=False)

    check = pd.read_sql(
        "SELECT order_year, ROUND(SUM(sales), 2) AS total_sales "
        "FROM sales GROUP BY order_year ORDER BY order_year",
        conn,
    )
    print(check)
    conn.close()


# ---------- PART 5 (NEW): CLEAN WITH SQL FILES ----------

def clean_with_sql():                                   # NEW recipe
    conn = sqlite3.connect(DATABASE)                    # open the database again

    checks_sql = (SQL_FOLDER / "01_data_quality_checks.sql").read_text(encoding="utf-8")  # read file 1 as text
    print("Data quality checks (every bad_rows should be 0):")
    print(pd.read_sql(checks_sql, conn))                # run the 7 questions and show the answers

    create_sql = (SQL_FOLDER / "02_create_sales_clean.sql").read_text(encoding="utf-8")   # read file 2 as text
    conn.executescript(create_sql)                      # run it; executescript is for files with many statements

    count = pd.read_sql("SELECT COUNT(*) AS rows_in_sales_clean FROM sales_clean", conn)  # count the new table
    print(count)
    conn.close()                                        # close the database door


# ---------- PART 6: MAIN (run all steps in order) ----------

def main():
    df = extract()                                      # step 1: read
    df = transform(df)                                  # step 2: clean with pandas
    load(df)                                            # step 3: save (builds the sales table)
    clean_with_sql()                                    # NEW step 4: checks, then build sales_clean
    print("ETL finished!")


# ---------- PART 7: THE START BUTTON ----------

if __name__ == "__main__":
    main()