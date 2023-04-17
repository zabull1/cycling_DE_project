{{ config(materialized='table') }}

with cycling as (
    select *
    from {{ ref('stg_cycling') }}
)

select * from cycling




{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}