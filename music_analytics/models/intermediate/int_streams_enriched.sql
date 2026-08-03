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

left join {{ ref('stg_music_metadata') }} m
    on s.track_id = m.track_id
