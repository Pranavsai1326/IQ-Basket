-- ============================================================
-- IQ Basket — SQL Business Analysis (SQLite)
-- ============================================================
-- NOTE: The Customer Shopping Trends dataset has NO purchase-date
-- column in its real Kaggle schema. Monthly revenue trend is
-- therefore only computed for the Online Retail dataset.
-- ============================================================


-- ------------------------------------------------------------
-- QUERY 1: Revenue by Product Category
-- Business question: What is total revenue and average purchase
-- amount for each product category? (Customer Behavior dataset)
-- ------------------------------------------------------------
SELECT
    product_category,
    SUM(purchase_amount) AS total_revenue,
    AVG(purchase_amount) AS average_purchase_amount
FROM customer_behavior
GROUP BY product_category
ORDER BY total_revenue DESC;


-- ------------------------------------------------------------
-- QUERY 2: Most Popular Payment Method by Age Group
-- Business question: Which payment method is most popular within
-- each age group? Uses CASE + RANK() window function.
-- ------------------------------------------------------------
WITH payment_summary AS (
    SELECT
        CASE
            WHEN age < 30 THEN 'Under 30'
            WHEN age BETWEEN 30 AND 50 THEN '30-50'
            ELSE 'Over 50'
        END AS age_group,
        payment_method,
        COUNT(*) AS purchase_count
    FROM customer_behavior
    GROUP BY age_group, payment_method
),
ranked AS (
    SELECT
        age_group,
        payment_method,
        purchase_count,
        RANK() OVER (
            PARTITION BY age_group
            ORDER BY purchase_count DESC
        ) AS payment_rank
    FROM payment_summary
)
SELECT
    age_group,
    payment_method,
    purchase_count
FROM ranked
WHERE payment_rank = 1
ORDER BY age_group;


-- ------------------------------------------------------------
-- QUERY 3: Monthly Revenue Trend (Online Retail)
-- Business question: How does revenue trend month over month?
-- ------------------------------------------------------------
SELECT
    strftime('%Y-%m', invoice_date) AS month,
    SUM(revenue) AS monthly_revenue
FROM online_retail
GROUP BY month
ORDER BY month;


-- ------------------------------------------------------------
-- QUERY 4: Location Spending Rank
-- Business question: Which locations generate the most spending?
-- Uses DENSE_RANK() window function.
-- ------------------------------------------------------------
SELECT
    location,
    SUM(purchase_amount) AS total_spending,
    DENSE_RANK() OVER (
        ORDER BY SUM(purchase_amount) DESC
    ) AS spending_rank
FROM customer_behavior
GROUP BY location
ORDER BY spending_rank;


-- ------------------------------------------------------------
-- QUERY 5: Purchase Frequency Analysis
-- Business question: How often do customers purchase, and how
-- much revenue does each frequency segment generate?
-- ------------------------------------------------------------
SELECT
    frequency_of_purchases,
    COUNT(*) AS purchase_count,
    SUM(purchase_amount) AS total_revenue,
    AVG(purchase_amount) AS average_purchase
FROM customer_behavior
GROUP BY frequency_of_purchases
ORDER BY purchase_count DESC;


-- ------------------------------------------------------------
-- QUERY 6: Revenue by Gender
-- ------------------------------------------------------------
SELECT
    gender,
    COUNT(*) AS purchases,
    SUM(purchase_amount) AS total_revenue,
    AVG(purchase_amount) AS average_purchase
FROM customer_behavior
GROUP BY gender
ORDER BY total_revenue DESC;


-- ------------------------------------------------------------
-- QUERY 7: Revenue by Location
-- ------------------------------------------------------------
SELECT
    location,
    COUNT(*) AS purchases,
    SUM(purchase_amount) AS total_revenue
FROM customer_behavior
GROUP BY location
ORDER BY total_revenue DESC;


-- ------------------------------------------------------------
-- QUERY 8: Top Countries by Revenue (Online Retail, excluding UK)
-- Business question: Which international markets drive the most
-- revenue outside the dataset's dominant UK market?
-- ------------------------------------------------------------
SELECT
    country,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS invoice_count
FROM online_retail
WHERE country != 'United Kingdom'
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;
