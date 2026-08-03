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

CLEAN_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "music_metadata_clean.parquet"
)


def clean_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw music metadata while preserving valid track-genre relationships."""

    cleaned_df = df.copy()

    cleaned_df = cleaned_df.drop(
        columns=["Unnamed: 0"],
        errors="ignore",
    )

    cleaned_df = cleaned_df.dropna(
        subset=[
            "track_id",
            "track_name",
            "artists",
            "album_name",
        ]
    )

    return cleaned_df


def main() -> None:
    """Clean raw metadata and save processed dataset."""

    print(f"Reading raw metadata from: {RAW_DATA_PATH}")

    df = pd.read_parquet(RAW_DATA_PATH)

    cleaned_df = clean_metadata(df)

    CLEAN_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_df.to_parquet(
        CLEAN_DATA_PATH,
        index=False,
    )

    print(f"Raw rows: {len(df):,}")
    print(f"Cleaned Rows: {len(cleaned_df):,}")
    print(f"Removed Rows: {len(df) - len(cleaned_df):,}")
    print(f"Clean Columns: {len(cleaned_df.columns)}")
    print(f"Saved cleaned metadata to: {CLEAN_DATA_PATH}")


if __name__ == "__main__":
    main()