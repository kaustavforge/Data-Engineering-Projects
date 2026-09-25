-- back compat for old kwarg name
  
  
  
  
  
  
      
          
          
      
  

    merge
    into
        `walmart`.`silver_t`.`order_items_t` as DBT_INTERNAL_DEST
    using
        `order_items_t__dbt_tmp` as DBT_INTERNAL_SOURCE
    on
        
              DBT_INTERNAL_SOURCE.order_item_id <=> DBT_INTERNAL_DEST.order_item_id
          
    when matched
        then update set
            *
    when not matched
        then insert
            *
