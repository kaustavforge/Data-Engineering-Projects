
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  

SELECT 1 
FROM 
    `walmart`.`silver_b`.`obt_b` AS obt
WHERE 
    obt.order_id IS NULL
OR
    obt.product_id IS NULL
OR
    obt.employee_id IS NULL
OR
    obt.store_id IS NULL
OR
    obt.order_item_id IS NULL
OR
    obt.customer_id IS NULL
  
  
      
    ) dbt_internal_test