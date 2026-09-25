

SELECT 
    *,
    current_timestamp() AS processed_at
FROM 
    `walmart`.`bronze`.`products`



    WHERE updated_timestamp > (SELECT COALESCE(MAX(updated_timestamp), '1900-01-01') FROM `walmart`.`silver_t`.`products_t`)
