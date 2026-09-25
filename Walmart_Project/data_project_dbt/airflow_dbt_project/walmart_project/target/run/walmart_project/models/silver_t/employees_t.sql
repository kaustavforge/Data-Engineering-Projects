-- back compat for old kwarg name
  
  
  
  
  
  
      
          
          
      
  

    merge
    into
        `walmart`.`silver_t`.`employees_t` as DBT_INTERNAL_DEST
    using
        `employees_t__dbt_tmp` as DBT_INTERNAL_SOURCE
    on
        
              DBT_INTERNAL_SOURCE.employee_id <=> DBT_INTERNAL_DEST.employee_id
          
    when matched
        then update set
            *
    when not matched
        then insert
            *
