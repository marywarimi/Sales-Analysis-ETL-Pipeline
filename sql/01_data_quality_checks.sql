-- Each line asks one question. bad_rows should be 0 for every check.
SELECT 'missing order_id' AS check_name, COUNT(*) AS bad_rows
FROM sales
WHERE order_id IS NULL                      -- order_id has no value

UNION ALL                                   -- UNION ALL glues the answers into one list

SELECT 'duplicate row_id', COUNT(*) - COUNT(DISTINCT row_id)
FROM sales                                  -- total rows minus unique rows = how many repeats

UNION ALL

SELECT 'sales zero or less', COUNT(*)
FROM sales
WHERE sales <= 0                            -- a sale should be more than 0

UNION ALL

SELECT 'quantity zero or less', COUNT(*)
FROM sales
WHERE quantity <= 0                         -- you cannot sell 0 items

UNION ALL

SELECT 'discount outside 0 to 1', COUNT(*)
FROM sales
WHERE discount < 0 OR discount > 1          -- discount must be between 0% and 100%

UNION ALL

SELECT 'shipped before ordered', COUNT(*)
FROM sales
WHERE ship_date < order_date                -- same safety check as in your notebook

UNION ALL

SELECT 'postal code not 5 characters', COUNT(*)
FROM sales
WHERE LENGTH(postal_code) <> 5;             -- your zfill should make all of them 5