{{ config(materialized='table') }}

with cycling as (
    select *
    from {{ ref('stg_cycling') }}
)

select * from cycling



-- dbt build --select dbt_mtg_latest_data.sql --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}