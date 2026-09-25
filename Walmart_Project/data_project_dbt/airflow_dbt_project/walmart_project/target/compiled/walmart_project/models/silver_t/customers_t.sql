

SELECT 
    *,
    current_timestamp() AS processed_at
FROM 
    `walmart`.`bronze`.`customers`



    WHERE updated_timestamp > (SELECT COALESCE(MAX(updated_timestamp), '1900-01-01') FROM `walmart`.`silver_t`.`customers_t`)
