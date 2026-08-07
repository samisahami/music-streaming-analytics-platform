{{ config(
    materialized='table'
) }}

with ranked_users as (

    select
        user_id,
        subscription_type,
        stream_timestamp,

        row_number() over (
            partition by user_id
            order by stream_timestamp desc
        ) as row_num

    from {{ ref('int_streams_enriched') }}

),

final as (

    select
        user_id,
        subscription_type
    from ranked_users
    where row_num = 1

)

select *
from final