-- back compat for old kwarg name
  
  
  
  
  
  
      
          
          
      
  

    merge
    into
        `walmart`.`silver_t`.`products_t` as DBT_INTERNAL_DEST
    using
        `products_t__dbt_tmp` as DBT_INTERNAL_SOURCE
    on
        
              DBT_INTERNAL_SOURCE.product_id <=> DBT_INTERNAL_DEST.product_id
          
    when matched
        then update set
            *
    when not matched
        then insert
            *
