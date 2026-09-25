
      
  
    
        create or replace table `walmart`.`gold`.`dim_employees`
      
      
  using delta
      
      
      
      
      
      
      
      as
      
    

    select *,
        md5(coalesce(cast(employee_id as string ), '')
         || '|' || coalesce(cast(employee_updated_timestamp as string ), '')
        ) as dbt_scd_id,
        employee_updated_timestamp as dbt_updated_at,
        employee_updated_timestamp as dbt_valid_from,
        
  
  coalesce(nullif(employee_updated_timestamp, employee_updated_timestamp), to_date('9999-12-31'))
  as dbt_valid_to
from (
        with __dbt__cte__eph_employees as (
SELECT 
    DISTINCT
    employee_id,
    employee_first_name,
    employee_last_name,
    employee_email,
    job_title,
    salary,
    store_id,
    employee_created_timestamp,
    employee_updated_timestamp,
    employee_is_active,
    employee_processed_at,
    CURRENT_TIMESTAMP() AS employee_gold_processed_at
FROM 
    `walmart`.`silver_b`.`obt_b`
) select * from __dbt__cte__eph_employees
    ) sbq



  
  