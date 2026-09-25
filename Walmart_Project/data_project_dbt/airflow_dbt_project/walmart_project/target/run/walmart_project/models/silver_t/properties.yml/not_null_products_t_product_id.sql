
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select product_id
from `walmart`.`silver_t`.`products_t`
where product_id is null



  
  
      
    ) dbt_internal_test