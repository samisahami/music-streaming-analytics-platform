{{ config(materialized='table') }}

with artist_metrics as (
    select 
        d.artists as artist_name,
        count(*) as total_streams,
        count(distinct f.user_id) as unique_listeners,
        count(distinct f.track_id) as unique_tracks,
        round(avg(f.stream_duration_seconds), 2) as avg_stream_duration,

        round(
            avg(
                case 
                    when f.completed_flag then 1
                    else 0
                end
            ),
            4
        ) as completion_rate,
        round(
            avg(
                case
                    when f.skip_flag then 1
                    else 0
                end 
            ),
            4
        ) as skip_rate
    from {{ (ref('fct_streams')) }} f

    left join {{ ref('dim_tracks') }} d
        on f.track_id = d.track_id
    group by d.artists

),
final as (
    select
    *,
    dense_rank() over(
        order by total_streams desc
    ) as artist_rank
from artist_metrics
)

select *
from final