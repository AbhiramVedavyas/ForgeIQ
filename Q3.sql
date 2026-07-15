WITH SupplierDelays AS (
    SELECT 
        s.supplier_name,
        s.country,
        AVG(DATEDIFF(po.delivered_date, po.order_date)) as avg_lead_time_days
    FROM purchase_orders po
    JOIN suppliers s ON po.supplier_id = s.supplier_id
    GROUP BY s.supplier_id, s.supplier_name, s.country
)
SELECT 
    supplier_name,
    country,
    ROUND(avg_lead_time_days, 1) as avg_lead_time_days,
    -- Rank suppliers in their respective country by efficiency (shortest lead time first)
    DENSE_RANK() OVER (
        PARTITION BY country 
        ORDER BY avg_lead_time_days ASC
    ) as supplier_rank_in_country
FROM SupplierDelays;
