{{ config(
    materialized='table'
) }}

with track_metrics as (

    select
        track_id,

        count(*) as total_streams,

        count(distinct user_id) as unique_listeners,

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

    group by track_id

),

final as (

    select
        m.track_id,
        d.track_name,
        d.artists,
        d.album_name,
        d.track_genre,

        m.total_streams,
        m.unique_listeners,
        m.avg_stream_duration_seconds,
        m.completion_rate,
        m.skip_rate,

        dense_rank() over (
            order by m.total_streams desc
        ) as popularity_rank

    from track_metrics m

    left join {{ ref('dim_tracks') }} d
        on m.track_id = d.track_id

)

select *
from final