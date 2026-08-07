{{ config(
    materialized='table'
) }}

with dates as (

    select distinct
        stream_date

    from {{ ref('fct_streams') }}

),

final as (

    select

        stream_date as full_date,

        to_number(to_char(stream_date, 'YYYYMMDD')) as date_key,

        extract(year from stream_date) as year,

        extract(quarter from stream_date) as quarter,

        extract(month from stream_date) as month,

        monthname(stream_date) as month_name,

        weekofyear(stream_date) as week_of_year,

        day(stream_date) as day_of_month,

        dayname(stream_date) as day_name,

        case
            when dayofweek(stream_date) in (0, 6)
            then true
            else false
        end as is_weekend

    from dates

)

select *
from final