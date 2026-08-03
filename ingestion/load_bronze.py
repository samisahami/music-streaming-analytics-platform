import os 

import pandas as pd
import snowflake.connector

from dotenv import load_dotenv

from pathlib import Path

from snowflake.connector.pandas_tools import write_pandas

from ingestion.clean_metadata import CLEAN_DATA_PATH
from ingestion.save_metadata import PROJECT_ROOT

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEAN_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "music_metadata_clean.parquet"
)

def get_connection():

    return snowflake.connector.connect(

        user=os.getenv("SNOWFLAKE_USER"),

        password=os.getenv("SNOWFLAKE_PASSWORD"),

        account=os.getenv("SNOWFLAKE_ACCOUNT"),

        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),

        database=os.getenv("SNOWFLAKE_DATABASE"),

        schema=os.getenv("SNOWFLAKE_SCHEMA"),

    )

def load_clean_metadata():
    print(f"Reading cleaned metadata from {CLEAN_DATA_PATH}")

    df = pd.read_parquet(CLEAN_DATA_PATH)

    print(f"Rows:{len(df):,}")
    print(f"Columns:{len(df.columns)}")

    return df

def load_to_bronze() -> None:
    """Load cleaned music metadata into the Snowflake Bronze layer."""

    df = load_clean_metadata()
    conn = get_connection()

    print(f"Preparing to upload {len(df):,} rows...")

    try:
        success, num_chunks, num_rows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name="BRONZE_MUSIC_METADATA",
            auto_create_table=True,
            overwrite=True,
        )

        print(f"Upload success: {success}")
        print(f"Chunks uploaded: {num_chunks}")
        print(f"Rows loaded: {num_rows:,}")

        if not success or num_rows != len(df):
            raise RuntimeError(
                f"Upload validation failed: expected {len(df):,} rows, "
                f"but Snowflake reported {num_rows:,}."
            )

    finally:
        conn.close()


if __name__ == "__main__":
    load_to_bronze()