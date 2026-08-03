"""
Save music metadata as a parquet file.

sprint 3:
Download metadata and persist it to the raw data layer.
"""


from pathlib import Path

import pandas as pd
from datasets import load_dataset

from ingestion.download_metadata import load_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "music_metadata"
    / "music_metadata.parquet"
)

def main() -> None:

    """Download and save music metadata."""

    config = load_config()

    dataset_name = config["datasets"]["music_metadata"]["dataset"]

    print(f"Loading dataset: {dataset_name}")

    dataset = load_dataset(

        dataset_name,

        split="train",

    )

    df = dataset.to_pandas()

    print(f"Rows: {len(df):,}")

    print(f"Columns: {len(df.columns)}")

    print(df.head())

    RAW_DATA_PATH.parent.mkdir(

        parents=True,

        exist_ok=True,

    )

    df.to_parquet(

        RAW_DATA_PATH,

        index=False,

    )

    print(f"Saved raw metadata to: {RAW_DATA_PATH}")

if __name__ == "__main__":

    main()