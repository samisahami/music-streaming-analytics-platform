from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRACK_META_DATA = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "music_metadata_clean.parquet"
)

STREAM_EVENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "stream_events"
    / "stream_events.parquet"
)

STREAM_EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)

NUM_USERS = 10_000

NUM_STREAM_EVENTS = 1_000_000

RANDOM_SEED = 42

random.seed(RANDOM_SEED)

np.random.seed(RANDOM_SEED)

tracks_df = pd.read_parquet(TRACK_META_DATA)

print(f"Loaded {len(tracks_df):,} tracks.")

track_ids = (
    tracks_df["track_id"]
    .dropna()
    .drop_duplicates()
    .to_numpy()
)

print(f"Available unique track IDs: {len(track_ids):,}")

user_ids = np.arange(1, NUM_USERS + 1)

print(f"Created {len(user_ids):,} synthetic users.")        

event_ids = np.arange(1, NUM_STREAM_EVENTS + 1)

stream_user_ids = np.random.choice(
    user_ids,
    size=NUM_STREAM_EVENTS,
    replace=True,
)

stream_track_ids = np.random.choice(
    track_ids,
    size=NUM_STREAM_EVENTS,
    replace=True,
)

print(f"Generated {len(event_ids):,} user-track stream combinations.")


START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31, 23, 59, 59)

total_seconds = int((END_DATE - START_DATE).total_seconds())

random_seconds = np.random.randint(
    0,
    total_seconds + 1,
    size=NUM_STREAM_EVENTS,
)

stream_timestamps = pd.to_datetime(START_DATE) + pd.to_timedelta(
    random_seconds,
    unit="s",
)

print(f"Generated {len(stream_timestamps):,} stream timestamps.")


stream_duration_seconds = np.random.randint(
    10,
    601,
    size=NUM_STREAM_EVENTS,
)

print(
    f"Generated {len(stream_duration_seconds):,} stream duration"
)

device_types = np.array([
    "Mobile",
    "Desktop",
    "Tablet",
    "Smart Speaker",
])

stream_devices = np.random.choice(
    device_types,
    size=NUM_STREAM_EVENTS,
    p=[0.60, 0.25, 0.10, 0.05],
)

print(f"Generated {len(stream_devices):,} device types.")


subscription_types = np.array([
    "Free",
    "Premium",
])

stream_subscriptions = np.random.choice(
    subscription_types,
    size=NUM_STREAM_EVENTS,
    p=[0.30, 0.70],
)

print(
    f"Generated {len(stream_subscriptions):,} subscription types."
)

shuffle_flags = np.random.choice(
    [True, False],
    size=NUM_STREAM_EVENTS,
    p=[0.45, 0.55],
)

print(f"Generated {len(shuffle_flags):,} shuffle flags.")

skip_flags = np.random.choice(
    [True, False],
    size=NUM_STREAM_EVENTS,
    p=[0.20, 0.80],
)

print(f"Generated {len(skip_flags):,} skip flags.")

completed_flags = np.where(
    skip_flags,
    False,
    np.random.choice(
        [True, False],
        size=NUM_STREAM_EVENTS,
        p=[0.95, 0.05],
    ),
)

print(f"Generated {len(completed_flags):,} completion flags.")

stream_events_df = pd.DataFrame({
    "event_id": event_ids,
    "user_id": stream_user_ids,
    "track_id": stream_track_ids,
    "stream_timestamp": stream_timestamps,
    "stream_duration_seconds": stream_duration_seconds,
    "device_type": stream_devices,
    "subscription_type": stream_subscriptions,
    "shuffle_flag": shuffle_flags,
    "skip_flag": skip_flags,
    "completed_flag": completed_flags,
})

print(f"Created stream events DataFrame with {len(stream_events_df):,} rows.")
print(stream_events_df.head())

stream_events_df.to_parquet(
    STREAM_EVENTS_PATH,
    index=False,
)

print(f"Saved stream events to {STREAM_EVENTS_PATH}")


