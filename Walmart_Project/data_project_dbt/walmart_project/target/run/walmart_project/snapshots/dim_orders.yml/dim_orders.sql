
      
  
    
        create or replace table `walmart`.`gold`.`dim_orders`
      
      
  using delta
      
      
      
      
      
      
      
      as
      
    

    select *,
        md5(coalesce(cast(order_id as string ), '')
         || '|' || coalesce(cast(order_updated_timestamp as string ), '')
        ) as dbt_scd_id,
        order_updated_timestamp as dbt_updated_at,
        order_updated_timestamp as dbt_valid_from,
        
  
  coalesce(nullif(order_updated_timestamp, order_updated_timestamp), to_date('9999-12-31'))
  as dbt_valid_to
from (
        with __dbt__cte__eph_orders as (
SELECT 
    DISTINCT
    order_id,
    order_item_id,
    payment_method,
    order_status,
    order_timestamp,
    order_created_timestamp,
    order_updated_timestamp,
    order_is_active,
    order_processed_at,
    obt_b_processed_at,
    CURRENT_TIMESTAMP() AS order_gold_processed_at
FROM 
    `walmart`.`silver_b`.`obt_b`
) select * from __dbt__cte__eph_orders
    ) sbq



  
  