WITH MachineMetrics AS (
    SELECT 
        m.machine_name,
        m.machine_type,
        f.location,
        SUM(pj.runtime_hours) as total_runtime_hrs,
        SUM(pj.quantity_produced) as total_produced,
        SUM(pj.quantity_defective) as total_defective,
        SUM(pj.quantity_produced - pj.quantity_defective) as good_units
    FROM production_jobs pj
    JOIN machines m ON pj.machine_id = m.machine_id
    JOIN production_lines pl ON m.line_id = pl.line_id
    JOIN factories f ON pl.factory_id = f.factory_id
    GROUP BY m.machine_id, m.machine_name, m.machine_type, f.location
)
SELECT 
    machine_name,
    machine_type,
    location,
    total_produced,
    -- Quality Rate
    ROUND((good_units / total_produced) * 100, 2) AS quality_rate_pct,
    -- OEE Approximation (combining output rates vs runtime efficiency)
    ROUND((good_units / (total_runtime_hrs * 100)) * 100, 2) AS oee_score_pct
FROM MachineMetrics
ORDER BY oee_score_pct DESC;