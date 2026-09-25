-- back compat for old kwarg name
  
  
  
  
  
  
      
          
          
      
  

    merge
    into
        `walmart`.`silver_t`.`customers_t` as DBT_INTERNAL_DEST
    using
        `customers_t__dbt_tmp` as DBT_INTERNAL_SOURCE
    on
        
              DBT_INTERNAL_SOURCE.customer_id <=> DBT_INTERNAL_DEST.customer_id
          
    when matched
        then update set
            *
    when not matched
        then insert
            *
