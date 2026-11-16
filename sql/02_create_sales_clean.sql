DROP TABLE IF EXISTS sales_clean;           -- remove the old copy so we can rebuild it fresh

CREATE TABLE sales_clean AS                 -- make a new table from the answer of the SELECT below
SELECT
    row_id,                                 -- these columns are copied as they are
    order_id,
    DATE(order_date) AS order_date,         -- DATE() cuts off the useless 00:00:00 time
    DATE(ship_date)  AS ship_date,
    ship_mode,
    customer_id,
    TRIM(customer_name) AS customer_name,   -- TRIM() removes extra spaces at the start or end
    segment,
    country,
    city,
    state,
    postal_code,
    region,
    product_id,
    category,
    sub_category,
    product_name,
    sales,
    quantity,
    discount,
    profit,
    order_year,
    order_month,
    shipping_days,
    ROUND(discount * 100, 0) AS discount_pct,  -- 0.3 becomes 30
    CASE                                       -- CASE works like if / else
        WHEN sales = 0 THEN NULL               -- never divide by zero
        ELSE ROUND(profit * 100.0 / sales, 2)  -- profit per 100 sold
    END AS profit_margin,
    CASE
        WHEN discount = 0   THEN 'No discount'
        WHEN discount <= 0.2 THEN 'Low (up to 20%)'
        ELSE 'High (over 20%)'
    END AS discount_band
FROM sales;                                 -- take everything from the old sales table