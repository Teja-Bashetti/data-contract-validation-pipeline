
-- 1. View all published customer records
SELECT *
FROM customers;


-- 2. Count total published customers
SELECT COUNT(*) AS total_customers
FROM customers;


-- 3. Count customers by city
SELECT
    city,
    COUNT(*) AS customer_count
FROM customers
GROUP BY city
ORDER BY customer_count DESC;


-- 4. Find customers above 30 years old
SELECT
    customer_id,
    customer_name,
    age,
    city
FROM customers
WHERE age > 30
ORDER BY age DESC;


-- 5. Check for duplicate customer IDs
SELECT
    customer_id,
    COUNT(*) AS duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;


-- 6. View pipeline processing metadata
SELECT
    customer_id,
    customer_name,
    run_id,
    source_file,
    processed_at
FROM customers
ORDER BY processed_at DESC;


-- 7. Count records by pipeline run
SELECT
    run_id,
    COUNT(*) AS records_published
FROM customers
GROUP BY run_id;
