# ---------- PART 1: TOOLS AND SETTINGS ----------

from pathlib import Path   # Path helps us build file locations safely on Windows
import sqlite3             # sqlite3 lets Python talk to the database
import pandas as pd        # pandas is our table tool, like in your notebooks

# This finds the main project folder, no matter where you run the script from.
# __file__ is this script. .parent is the folder it sits in (src). .parent again goes up to the project folder.
PROJECT_FOLDER = Path(__file__).resolve().parent.parent

# These are the three file locations. We write them once here and reuse them below.
RAW_CSV = PROJECT_FOLDER / "data" / "raw" / "superstore.csv"
CLEAN_CSV = PROJECT_FOLDER / "data" / "processed" / "superstore_clean.csv"
DATABASE = PROJECT_FOLDER / "data" / "superstore.db"


# ---------- PART 2: EXTRACT (read the raw file) ----------

def extract():                                          # a recipe called extract
    df = pd.read_csv(RAW_CSV, encoding="latin-1")       # read the CSV into df (latin-1 so the odd characters don't break it)
    print("Extracted:", df.shape[0], "rows and", df.shape[1], "columns")  # show how big the table is
    return df                                           # hand the table back to whoever called extract


# ---------- PART 3: TRANSFORM (clean the table) ----------

def transform(df):                                      # a recipe called transform; it receives df
    print("Duplicate rows:", df.duplicated().sum())     # count the repeated rows (you found 0)
    df = df.drop_duplicates()                           # remove repeats; with 0 repeats nothing changes

    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")  # text -> real date
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")    # same for Ship Date

    df["Postal Code"] = df["Postal Code"].astype(str).str.zfill(5)  # make it text, then pad with zeros to 5 digits

    print("Ship before order:", (df["Ship Date"] < df["Order Date"]).sum())  # safety check; should be 0

    df["Order Year"] = df["Order Date"].dt.year         # new column: the year (2014, 2015...)
    df["Order Month"] = df["Order Date"].dt.month       # new column: the month as a number (1 to 12)
    df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days  # new column: days between order and ship

    print("Transformed:", df.shape[0], "rows and", df.shape[1], "columns")  # should say 24 columns
    return df                                           # hand the clean table back


# ---------- PART 4: LOAD (save the clean table) ----------

def load(df):                                           # a recipe called load
    # lowercase the names, then swap spaces and dashes for underscores (same line as your notebook)
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")

    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True) # make data/processed if it is missing
    df.to_csv(CLEAN_CSV, index=False)                   # save the clean CSV (index=False = no extra number column)

    conn = sqlite3.connect(DATABASE)                    # open (or create) the database file
    df.to_sql("sales", conn, if_exists="replace", index=False)  # write the table "sales"; replace it if it exists

    check = pd.read_sql(                                # a quick SQL check, like in your notebook
        "SELECT order_year, ROUND(SUM(sales), 2) AS total_sales "
        "FROM sales GROUP BY order_year ORDER BY order_year",
        conn,
    )
    print(check)                                        # show the yearly sales
    conn.close()                                        # close the database door when we are done


# ---------- PART 5: MAIN (run all steps in order) ----------

def main():                                             # the boss recipe
    df = extract()                                      # step 1: read
    df = transform(df)                                  # step 2: clean
    load(df)                                            # step 3: save (always last, because it lowercases the names)
    print("ETL finished!")                              # tell us it worked


# ---------- PART 6: THE START BUTTON ----------

if __name__ == "__main__":                              # true only when you run this file directly
    main()                                              # press start