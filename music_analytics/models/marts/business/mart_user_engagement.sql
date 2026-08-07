{{ config(
    materialized='table'
) }}

with user_metrics as (

    select

        user_id,

        subscription_type,

        count(*) as total_streams,

        count(distinct track_id) as unique_tracks,

        round(avg(stream_duration_seconds), 2) as avg_stream_duration_seconds,

        round(avg(
            case
                when completed_flag then 1
                else 0
            end
        ), 4) as completion_rate,

        round(avg(
            case
                when skip_flag then 1
                else 0
            end
        ), 4) as skip_rate,

        min(stream_date) as first_stream_date,

        max(stream_date) as last_stream_date

    from {{ ref('fct_streams') }}

    group by
        user_id,
        subscription_type

),

device_usage as (

    select

        user_id,

        device_type,

        count(*) as streams,

        row_number() over (

            partition by user_id
            order by count(*) desc

        ) as rn

    from {{ ref('fct_streams') }}

    group by
        user_id,
        device_type

),

favorite_device as (

    select

        user_id,

        device_type as favorite_device

    from device_usage

    where rn = 1

),

final as (

    select

        u.*,

        d.favorite_device,

        datediff(
            day,
            first_stream_date,
            last_stream_date
        ) as active_days

    from user_metrics u

    left join favorite_device d
        on u.user_id = d.user_id

)

select *
from final