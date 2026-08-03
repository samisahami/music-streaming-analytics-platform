select

    "track_id" as track_id,

    "track_name" as track_name,

    "artists" as artists,

    "album_name" as album_name,

    "track_genre" as track_genre,

    "duration_ms" as duration_ms,

    "explicit" as explicit

from {{ source('bronze', 'bronze_music_metadata') }}