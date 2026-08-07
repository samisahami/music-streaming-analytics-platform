{{ config(
    materialized='table'
) }}

with source_streams as (

    select
        event_id,
        user_id,
        track_id,
        stream_timestamp,
        device_type,
        subscription_type,
        stream_duration_seconds,
        skip_flag,
        completed_flag

    from {{ ref('int_streams_enriched') }}

),

final as (

    select
        event_id,
        user_id,
        track_id,
        stream_timestamp,
        cast(stream_timestamp as date) as stream_date,
        device_type,
        subscription_type,
        stream_duration_seconds,
        skip_flag,
        completed_flag

    from source_streams

)

select *
from final

