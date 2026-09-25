-- back compat for old kwarg name
  
  
  
  
  
  
      
          
          
      
  

    merge
    into
        `walmart`.`silver_t`.`stores_t` as DBT_INTERNAL_DEST
    using
        `stores_t__dbt_tmp` as DBT_INTERNAL_SOURCE
    on
        
              DBT_INTERNAL_SOURCE.store_id <=> DBT_INTERNAL_DEST.store_id
          
    when matched
        then update set
            *
    when not matched
        then insert
            *
