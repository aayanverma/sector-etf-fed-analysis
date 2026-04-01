-- Query 1: Average monthly return per ETF per cycle type

SELECT 
    ticker,
    cycle_type,
    ROUND(AVG(monthly_return)::numeric, 2) AS avg_monthly_return
FROM etf_returns
GROUP BY ticker, cycle_type
ORDER BY cycle_type, avg_monthly_return DESC;

-- Query 2: Sector rankings within each cycle type

SELECT 
    ticker,
    cycle_type,
    ROUND(AVG(monthly_return)::numeric, 2) AS avg_monthly_return,
    RANK() OVER (PARTITION BY cycle_type ORDER BY AVG(monthly_return) DESC) AS rank
FROM etf_returns
GROUP BY ticker, cycle_type
ORDER BY cycle_type, rank;

-- Query 3: Best and worst performing sector per cycle

WITH ranked AS (
    SELECT 
        ticker,
        cycle_type,
        ROUND(AVG(monthly_return)::numeric, 2) AS avg_monthly_return,
        RANK() OVER (PARTITION BY cycle_type ORDER BY AVG(monthly_return) DESC) AS rank
    FROM etf_returns
    GROUP BY ticker, cycle_type
)
SELECT * FROM ranked
WHERE rank = 1 OR rank = 8
ORDER BY cycle_type, rank;

-- Query 4: Positive v.s. negative return months per sector

SELECT
    ticker,
    COUNT(CASE WHEN monthly_return > 0 THEN 1 END) AS positive_months,
    COUNT(CASE WHEN monthly_return < 0 THEN 1 END) AS negative_months,
    ROUND(100.0 * COUNT(CASE WHEN monthly_return > 0 THEN 1 END) / COUNT(*), 1) AS win_rate_pct
FROM etf_returns
GROUP BY ticker
ORDER BY win_rate_pct DESC;