
  
    
        create or replace table `walmart`.`gold`.`fact_orders`
      
      
  using delta
      
      
      
      
      
      
      
      as
      SELECT 
    order_id,
    order_item_id,
    product_id,
    store_id,
    employee_id,
    customer_id,
    total_amount,
    quantity,
    unit_price,
    line_amount
FROM 
    `walmart`.`silver_b`.`obt_b`
  