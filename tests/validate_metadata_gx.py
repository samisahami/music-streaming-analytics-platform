from pathlib import Path

import great_expectations as gx
import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "music_metadata_clean.parquet"
)


# =========================================================
# LOAD DATA
# =========================================================

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Processed metadata file was not found: {DATA_PATH}"
    )

df = pd.read_parquet(DATA_PATH)

print(f"Loaded dataset: {DATA_PATH}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")


# =========================================================
# DUPLICATE-RATE VALIDATION
# =========================================================

# These columns represent the practical metadata row grain.
duplicate_columns = [
    "track_id",
    "track_genre",
    "artists",
    "album_name",
]

missing_duplicate_columns = [
    column
    for column in duplicate_columns
    if column not in df.columns
]

if missing_duplicate_columns:
    raise ValueError(
        "Cannot perform duplicate validation because these "
        f"columns are missing: {missing_duplicate_columns}"
    )

duplicate_mask = df.duplicated(
    subset=duplicate_columns,
    keep=False,
)

duplicate_row_count = int(duplicate_mask.sum())

duplicate_rate = df.duplicated(
    subset=duplicate_columns,
).mean()

MAX_DUPLICATE_RATE = 0.01

print("\nDuplicate validation")
print("--------------------")
print(f"Duplicate rows found: {duplicate_row_count:,}")
print(f"Duplicate rate: {duplicate_rate:.2%}")
print(f"Maximum allowed rate: {MAX_DUPLICATE_RATE:.2%}")

if duplicate_rate > MAX_DUPLICATE_RATE:
    duplicate_sample = (
        df.loc[duplicate_mask, duplicate_columns]
        .sort_values(duplicate_columns)
        .head(20)
    )

    print("\nSample duplicate metadata rows:")
    print(duplicate_sample.to_string(index=False))

    raise ValueError(
        "Duplicate metadata rate exceeded the allowed threshold. "
        f"Actual: {duplicate_rate:.2%}; "
        f"Allowed: {MAX_DUPLICATE_RATE:.2%}"
    )

print("PASS: Duplicate rate is within the allowed threshold.")


# =========================================================
# GREAT EXPECTATIONS CONTEXT
# =========================================================

context = gx.get_context(mode="file")


# =========================================================
# PANDAS DATA SOURCE AND ASSET
# =========================================================

data_source_name = "music_streaming_pandas"
data_asset_name = "music_metadata_clean"
batch_definition_name = "whole_dataframe"


try:
    data_source = context.data_sources.get(
        data_source_name
    )
except Exception:
    data_source = context.data_sources.add_pandas(
        name=data_source_name
    )


try:
    data_asset = data_source.get_asset(
        data_asset_name
    )
except Exception:
    data_asset = data_source.add_dataframe_asset(
        name=data_asset_name
    )


try:
    batch_definition = data_asset.get_batch_definition(
        batch_definition_name
    )
except Exception:
    batch_definition = (
        data_asset.add_batch_definition_whole_dataframe(
            name=batch_definition_name
        )
    )


batch = batch_definition.get_batch(
    batch_parameters={
        "dataframe": df
    }
)


# =========================================================
# GREAT EXPECTATIONS RULES
# =========================================================

expectations = [
    gx.expectations.ExpectTableRowCountToBeBetween(
        min_value=1
    ),

    gx.expectations.ExpectColumnToExist(
        column="track_id"
    ),

    gx.expectations.ExpectColumnToExist(
        column="track_name"
    ),

    gx.expectations.ExpectColumnToExist(
        column="artists"
    ),

    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="track_id"
    ),

    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="track_name"
    ),

    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="artists"
    ),
]


# =========================================================
# RUN GREAT EXPECTATIONS VALIDATIONS
# =========================================================

results = []

print("\nGreat Expectations validation")
print("-----------------------------")

for expectation in expectations:
    result = batch.validate(expectation)
    results.append(result)

    expectation_name = expectation.__class__.__name__
    status = "PASS" if result.success else "FAIL"

    print(f"{status}: {expectation_name}")


# =========================================================
# VALIDATION SUMMARY
# =========================================================

failed_results = [
    result
    for result in results
    if not result.success
]

passed_count = len(results) - len(failed_results)

print("\nValidation summary")
print("------------------")
print(f"GX expectations run: {len(results)}")
print(f"GX expectations passed: {passed_count}")
print(f"GX expectations failed: {len(failed_results)}")
print(
    "Duplicate-rate validation: "
    f"{duplicate_rate:.2%} "
    f"(maximum {MAX_DUPLICATE_RATE:.2%})"
)


if failed_results:
    raise ValueError(
        "GX validation failed for "
        f"{len(failed_results)} expectation(s)."
    )


print("\nAll metadata quality validations passed!")