{{ config(materialized='table') }}

with cycling as (
    select *
    from {{ ref('stg_cycling') }}
)

select 

StartStation_Name,
count(Rental_id) as count

from cycling
group by StartStation_Name
order by count DESC