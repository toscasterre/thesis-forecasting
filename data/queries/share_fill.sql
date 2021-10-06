WITH outf AS (
	SELECT COUNT(*) AS outflow,
	DATE_TRUNC('minute', data_prelievo) AS departure_time,
	nome_stazione_prelievo,
	numero_stazione_prelievo
	FROM bikemi_rentals
	GROUP BY DATE_TRUNC('minute', data_prelievo),
	nome_stazione_prelievo,
	numero_stazione_prelievo
	ORDER BY departure_time, nome_stazione_prelievo),

inf AS (
	SELECT COUNT(*) AS inflow,
	DATE_TRUNC('minute', data_restituzione) AS arrival_time,
	nome_stazione_restituzione,
	numero_stazione_restituzione
	FROM bikemi_rentals
	GROUP BY DATE_TRUNC('minute', data_restituzione),
	nome_stazione_restituzione,
	numero_stazione_restituzione
	ORDER BY arrival_time, nome_stazione_restituzione
)
	
SELECT *
FROM outf o
FULL OUTER JOIN inf i
	ON o.departure_time = i.arrival_time;
