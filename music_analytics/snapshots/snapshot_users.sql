{% snapshot snapshot_users %}

{{
    config(
        target_schema='SNAPSHOTS',
        unique_key='user_id',
        strategy='check',
        check_cols=['subscription_type']
    )
}}

select
    user_id,
    subscription_type
from {{ ref('dim_users') }}

{% endsnapshot %}