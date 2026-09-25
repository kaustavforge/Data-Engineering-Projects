
      
  
    
        create or replace table `walmart`.`gold`.`dim_stores`
      
      
  using delta
      
      
      
      
      
      
      
      as
      
    

    select *,
        md5(coalesce(cast(store_id as string ), '')
         || '|' || coalesce(cast(store_updated_timestamp as string ), '')
        ) as dbt_scd_id,
        store_updated_timestamp as dbt_updated_at,
        store_updated_timestamp as dbt_valid_from,
        
  
  coalesce(nullif(store_updated_timestamp, store_updated_timestamp), to_date('9999-12-31'))
  as dbt_valid_to
from (
        with __dbt__cte__eph_stores as (
SELECT 
    DISTINCT
    store_id,
    store_name,
    store_city,
    store_province,
    store_country,
    store_created_timestamp,
    store_updated_timestamp,
    store_is_active,
    store_processed_at,
    CURRENT_TIMESTAMP() AS store_gold_processed_at
FROM 
    `walmart`.`silver_b`.`obt_b`
) select * from __dbt__cte__eph_stores
    ) sbq



  
  