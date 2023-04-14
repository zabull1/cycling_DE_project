{{config(materalized= 'view')}}

select * from {{source('staging', 'cycling_table')}}

limit 100