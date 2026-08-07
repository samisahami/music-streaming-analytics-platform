{{ config(
    materialized='table'
) }}

with track_versions as (

    select
        track_id,
        track_name,
        artists,
        album_name,
        track_genre,
        explicit,
        count(*) as occurrence_count

    from {{ ref('int_streams_enriched') }}

    group by
        track_id,
        track_name,
        artists,
        album_name,
        track_genre,
        explicit

),

ranked_tracks as (

    select
        track_id,
        track_name,
        artists,
        album_name,
        track_genre,
        explicit,

        row_number() over (
            partition by track_id
            order by occurrence_count desc
        ) as row_num

    from track_versions

),

final as (

    select
        track_id,
        track_name,
        artists,
        album_name,
        track_genre,
        explicit

    from ranked_tracks
    where row_num = 1

)

select *
from final