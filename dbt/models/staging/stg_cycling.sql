{{ config(materialized="table") }}

with cycling as (
    select *,
        row_number() over (partition by cast(Rental_id as numeric), Start_Date) as rn
    from {{ source("staging", "external_cycling_data_partitioned_clustered") }}
    where Rental_id is not null
)

select 
    cast(Rental_id as string) as rental_id,
    cast(Bike_id as string) as bike_id,
    cast(Start_Date as timestamp) as Start_Date,
    cast(StartStation_id as string) as startstation_id,
    cast(StartStation_Name as string) as startstation_name,
    cast(End_Date as timestamp) as end_date,
    cast(EndStation_id as string) as endstation_id,
    cast(EndStation_Name as string) as endstation_name,
    cast(Duration as numeric) as duration

from cycling

where rn = 1

-- {% if var('is_test_run', default=true) %}

--   limit 100

-- {% endif %}