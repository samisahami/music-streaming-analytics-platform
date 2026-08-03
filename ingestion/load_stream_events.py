from pathlib import Path

import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

from ingestion.connect_snowflake import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STREAM_EVENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "stream_events"
    / "stream_events.parquet"
)


def load_stream_events() -> pd.DataFrame:
    if not STREAM_EVENTS_PATH.exists():
        raise FileNotFoundError(
            f"Stream events file not found: {STREAM_EVENTS_PATH}"
        )

    stream_events_df = pd.read_parquet(STREAM_EVENTS_PATH)

    print(f"Loaded {len(stream_events_df):,} stream events from Parquet.")

    return stream_events_df


def main() -> None:
    connection = None

    try:
        stream_events_df = load_stream_events()

        connection = get_connection()

        success, num_chunks, num_rows, _ = write_pandas(
            connection,
            stream_events_df,
            table_name="STREAM_EVENTS",
            schema="BRONZE",
            auto_create_table=True,
            overwrite=True,
        )

        print(f"Upload success: {success}")
        print(f"Chunks uploaded: {num_chunks}")
        print(f"Rows loaded: {num_rows:,}")

        if not success:
            raise RuntimeError("Snowflake upload failed.")

        if num_rows != len(stream_events_df):
            raise RuntimeError(
                f"Row count mismatch: expected {len(stream_events_df):,}, "
                f"loaded {num_rows:,}."
            )

        print("Stream events loaded into BRONZE.STREAM_EVENTS successfully.")

    finally:
        if connection is not None:
            connection.close()
            print("Snowflake connection closed.")


if __name__ == "__main__":
    main()

