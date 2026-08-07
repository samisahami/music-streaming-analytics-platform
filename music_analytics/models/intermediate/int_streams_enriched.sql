with metadata_ranked as (

    select
        track_id,
        track_name,
        artists,
        album_name,
        track_genre,
        explicit,

        row_number() over (
            partition by track_id
            order by
                track_name,
                artists,
                album_name,
                track_genre
        ) as row_num

    from {{ ref('stg_music_metadata') }}

),

metadata_deduped as (

    select
        track_id,
        track_name,
        artists,
        album_name,
        track_genre,
        explicit

    from metadata_ranked
    where row_num = 1

),

final as (

    select
        s.event_id,
        s.user_id,
        s.track_id,

        m.track_name,
        m.artists,
        m.album_name,
        m.track_genre,

        s.stream_timestamp,
        s.device_type,
        s.subscription_type,
        s.stream_duration_seconds,
        s.skip_flag,
        s.completed_flag,

        m.explicit

    from {{ ref('stg_streaming_events') }} s

    left join metadata_deduped m
        on s.track_id = m.track_id

)

select *
from final