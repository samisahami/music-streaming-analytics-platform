{{ config(
    materialized='table'
) }}

with subscription_metrics as (

    select
        subscription_type,

        count(*) as total_streams,

        count(distinct user_id) as unique_users,

        count(distinct track_id) as unique_tracks,

        round(avg(stream_duration_seconds), 2) as avg_stream_duration_seconds,

        round(
            avg(
                case
                    when completed_flag then 1
                    else 0
                end
            ),
            4
        ) as completion_rate,

        round(
            avg(
                case
                    when skip_flag then 1
                    else 0
                end
            ),
            4
        ) as skip_rate

    from {{ ref('fct_streams') }}

    group by
        subscription_type

),

final as (

    select
        *,

        round(
            total_streams / sum(total_streams) over (),
            4
        ) as stream_share

    from subscription_metrics

)

select *
from final