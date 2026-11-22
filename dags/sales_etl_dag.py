# ---------- PART 1: TOOLS AND SETTINGS ----------

import sys                                   # sys lets us tell Python where to find extra code files
from datetime import datetime                # datetime is used for the start date
from pathlib import Path                     # Path builds file locations safely

import pandas as pd                          # pandas is our table tool

from airflow.sdk import dag, task            # dag = the to-do list, task = one step in it

PROJECT_FOLDER = Path(__file__).resolve().parent.parent   # the main project folder (one level above dags)
SRC_FOLDER = PROJECT_FOLDER / "src"                       # the folder where etl.py lives
STAGING_FOLDER = Path("/tmp/sales_etl")                   # a temporary folder where tasks leave tables for the next task

EXTRACTED_FILE = STAGING_FOLDER / "01_extracted.pkl"      # the table after extract
TRANSFORMED_FILE = STAGING_FOLDER / "02_transformed.pkl"  # the table after transform

sys.path.insert(0, str(SRC_FOLDER))          # let Python find src/etl.py so we can use your functions


# ---------- PART 2: THE DAG (the to-do list) ----------

@dag(
    dag_id="sales_etl_pipeline",             # the name you will see on the Airflow page
    schedule="@daily",                       # run once every day
    start_date=datetime(2026, 11, 1),        # the date the schedule starts counting from
    catchup=False,                           # do NOT run all the missed days, only the latest
    tags=["sales", "etl"],                   # little labels to help find it
)
def sales_etl_pipeline():

    # ---------- TASK 1: EXTRACT ----------
    @task
    def extract_data():
        import etl                                            # your etl.py file
        STAGING_FOLDER.mkdir(parents=True, exist_ok=True)     # make the temporary folder if it is missing
        df = etl.extract()                                    # your extract() reads the raw CSV
        df.to_pickle(EXTRACTED_FILE)                          # freeze the table into a file for the next task

    # ---------- TASK 2: TRANSFORM ----------
    @task
    def transform_data():
        import etl
        df = pd.read_pickle(EXTRACTED_FILE)                   # unfreeze the table from task 1
        df = etl.transform(df)                                # your transform(df) cleans it
        df.to_pickle(TRANSFORMED_FILE)                        # freeze the cleaned table

    # ---------- TASK 3: LOAD ----------
    @task
    def load_data():
        import etl
        df = pd.read_pickle(TRANSFORMED_FILE)                 # unfreeze the cleaned table
        etl.load(df)                                          # your load(df) saves the CSV and the sales table

    # ---------- TASK 4: CLEAN WITH SQL ----------
    @task
    def clean_data():
        import etl
        etl.clean_with_sql()                                  # your clean_with_sql() runs the checks and builds sales_clean

    # ---------- THE ARROWS (the order) ----------
    extract_data() >> transform_data() >> load_data() >> clean_data()


# ---------- PART 3: SWITCH THE DAG ON ----------

sales_etl_pipeline()                         # calling the function is what registers the DAG with Airflow