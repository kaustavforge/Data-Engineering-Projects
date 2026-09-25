
      
  
    
        create or replace table `walmart`.`gold`.`dim_products`
      
      
  using delta
      
      
      
      
      
      
      
      as
      
    

    select *,
        md5(coalesce(cast(product_id as string ), '')
         || '|' || coalesce(cast(product_updated_timestamp as string ), '')
        ) as dbt_scd_id,
        product_updated_timestamp as dbt_updated_at,
        product_updated_timestamp as dbt_valid_from,
        
  
  coalesce(nullif(product_updated_timestamp, product_updated_timestamp), to_date('9999-12-31'))
  as dbt_valid_to
from (
        with __dbt__cte__eph_products as (
SELECT 
    DISTINCT
    product_id,
    product_name,
    category,
    brand,
    price,
    product_created_timestamp,
    product_updated_timestamp,
    product_is_active,
    product_processed_at,
    CURRENT_TIMESTAMP() AS product_gold_processed_at
FROM 
    `walmart`.`silver_b`.`obt_b`
) select * from __dbt__cte__eph_products
    ) sbq



  
  