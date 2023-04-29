{{ 
    config(
        materialized='table',
        partition_by={
            "field": "start_date",
            "data_type": "timestamp",
            "granularity": "day",
        },
        cluster_by="StartStation_id",
    ) 
}}

with cycling as (
    select *
    from {{ ref('stg_cycling') }}
)

select * from cycling


-- {% if var('is_test_run', default=true) %}

--   limit 100

-- {% endif %}