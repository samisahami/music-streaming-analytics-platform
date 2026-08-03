select 
"event_id" as event_id,
"user_id" as user_id,
"track_id" as track_id,
to_timestamp_ntz("stream_timestamp", 6) as stream_timestamp,
"stream_duration_seconds" as stream_duration_seconds,
"device_type" as device_type,
"subscription_type" as subscription_type,
"shuffle_flag" as shuffle_flag, 
"skip_flag" as skip_flag,
"completed_flag" as completed_flag
from {{ source('bronze', 'stream_events') }}