"""
Validate raw music metadata.

Sprint 4:
Read the Bronze Parquet file and inspect core data-quality conditions.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "music_metadata"
    / "music_metadata.parquet"
)


def main() -> None:
    """Load and inspect the raw music metadata."""

    print(f"Reading raw metadata from: {RAW_DATA_PATH}")

    df = pd.read_parquet(RAW_DATA_PATH)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nMissing values by column:")
    print(df.isna().sum().sort_values(ascending=False))

    print("\nDuplicate track IDs:")
    print(df["track_id"].duplicated().sum())

    duplicate_rows = df[df["track_id"].duplicated(keep=False)]
    print("\nSample duplicate track IDs:")
    print(
        duplicate_rows[
            [
                "track_id",
                "track_name",
                "artists",
                "album_name",
                "track_genre",
            ]
        ]
        .sort_values("track_id")
        .head(20)
    )

    print("\nDuplicate rows across all columns:")
    print(df.duplicated().sum())

    print("\nUnique track IDs:")
    print(df["track_id"].nunique())


if __name__ == "__main__":
    main()