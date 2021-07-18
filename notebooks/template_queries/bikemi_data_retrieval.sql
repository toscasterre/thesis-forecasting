-- aggregate by departure, day

SELECT
    DATE_TRUNC('day', data_prelievo) AS data_agg,
    COUNT(bici)
FROM bikemi_2019
GROUP BY data_agg
ORDER BY data_agg DESC;

-- aggregate by destination, day

SELECT
    DATE_TRUNC('day', data_restituzione) AS data_agg,
    COUNT(bici)
FROM bikemi_2019
GROUP BY data_agg
ORDER BY data_agg DESC;

-- aggregate by departure, day

SELECT
    DATE_TRUNC('hour', data_prelievo) AS data_agg,
    COUNT(bici)
FROM bikemi_2019
GROUP BY data_agg
ORDER BY data_agg DESC;