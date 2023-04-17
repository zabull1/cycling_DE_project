{{ config(materialized="table") }}

with cycling as (
    select *,
        row_number() over (partition by cast(Rental_id as numeric), Start_Date) as rn
    from {{ source("staging", "cycling_table") }}
    where Rental_id is not null
)

select 
    cast(Rental_id as string) as Rental_id,
    cast(Bike_id as string) as Bike_id,
    cast(Start_Date as timestamp) as Start_Date,
    cast(StartStation_id as string) as StartStation_id,
    cast(StartStation_Name as string) as StartStation_Name,
    cast(End_Date as timestamp) as End_Date,
    cast(EndStation_id as string) as EndStation_id,
    cast(EndStation_Name as string) as EndStation_Name,
    cast(Duration as numeric) as Duration

from cycling

where rn = 1

{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}



