WITH SensorHistory AS (
    SELECT 
        machine_id,
        timestamp,
        temperature_c,
        -- Get the temperature of the PREVIOUS reading for this specific machine
        LAG(temperature_c, 1) OVER (
            PARTITION BY machine_id 
            ORDER BY timestamp
        ) as prev_temperature_c
    FROM machine_sensors
)
SELECT 
    sh.machine_id,
    m.machine_name,
    sh.timestamp,
    sh.temperature_c as current_temp,
    sh.prev_temperature_c as previous_temp,
    ROUND((sh.temperature_c - sh.prev_temperature_c), 2) as temp_spike
FROM SensorHistory sh
JOIN machines m ON sh.machine_id = m.machine_id
WHERE sh.prev_temperature_c IS NOT NULL 
  AND (sh.temperature_c - sh.prev_temperature_c) >= 10.0
ORDER BY temp_spike DESC
LIMIT 10;