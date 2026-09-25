
      
  
    
        create or replace table `walmart`.`gold`.`dim_customers`
      
      
  using delta
      
      
      
      
      
      
      
      as
      
    

    select *,
        md5(coalesce(cast(customer_id as string ), '')
         || '|' || coalesce(cast(customer_updated_timestamp as string ), '')
        ) as dbt_scd_id,
        customer_updated_timestamp as dbt_updated_at,
        customer_updated_timestamp as dbt_valid_from,
        
  
  coalesce(nullif(customer_updated_timestamp, customer_updated_timestamp), to_date('9999-12-31'))
  as dbt_valid_to
from (
        with __dbt__cte__eph_customers as (
SELECT 
    DISTINCT
    customer_id,
    customer_first_name,
    customer_last_name,
    customer_email,
    customer_phone,
    customer_city,
    customer_province,
    customer_country,
    customer_created_timestamp,
    customer_updated_timestamp,
    customer_is_active,
    customer_processed_at,
    CURRENT_TIMESTAMP() AS customer_gold_processed_at
FROM 
    `walmart`.`silver_b`.`obt_b`
) select * from __dbt__cte__eph_customers
    ) sbq



  
  