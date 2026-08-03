select
    count(*) as total_streams,
    count(distinct user_id) as unique_users,
    avg(stream_duration_seconds) as avg_stream_duration_seconds,

    avg(
        case
            when skip_flag then 1
            else 0
        end
    ) as skip_rate,

    avg(
        case
            when completed_flag then 1
            else 0
        end
    ) as completion_rate,

    avg(
        case
            when subscription_type = 'Premium' then 1
            else 0
        end
    ) as premium_stream_rate,

    avg(
        case
            when subscription_type = 'Free' then 1
            else 0
        end
    ) as free_stream_rate

from {{ ref('int_streams_enriched') }}