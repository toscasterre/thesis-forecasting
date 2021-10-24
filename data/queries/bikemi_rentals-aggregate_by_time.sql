COPY (
SELECT 
    COUNT(bici),
    DATE_TRUNC('day', data_prelievo) AS giorno_partenza
FROM bikemi_rentals
GROUP BY DATE_TRUNC('day', data_prelievo)
ORDER BY giorno_partenza ASC
)
TO '/Users/luca/tesi/data/bikemi_csv/daily_rentals.csv' (format CSV);

COPY (
SELECT 
    COUNT(bici),
    DATE_TRUNC('hour', data_prelievo) AS ora_partenza
FROM bikemi_rentals
GROUP BY DATE_TRUNC('hour', data_prelievo)
ORDER BY ora_partenza ASC
)
TO '/Users/luca/tesi/data/bikemi_csv/hourly_rentals.csv' (format CSV);
