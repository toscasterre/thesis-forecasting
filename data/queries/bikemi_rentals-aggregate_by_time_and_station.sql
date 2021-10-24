COPY (
	SELECT
		COUNT(b.bici),
		b.nome_stazione_prelievo,
		b.numero_stazione_prelievo,
		-- cast as date and not datetime
		DATE_TRUNC('day', b.data_prelievo)::date AS giorno_prelievo
	FROM bikemi_rentals b
	WHERE EXTRACT('year' FROM b.data_prelievo) < 2019
	GROUP BY 
		b.nome_stazione_prelievo,
		b.numero_stazione_prelievo,
		DATE_TRUNC('day', b.data_prelievo)
	ORDER BY giorno_prelievo ASC
) TO '/Users/luca/tesi/data/bikemi-rentals_csv/bikemi-stations-daily_rentals.csv' DELIMITER ',' CSV HEADER;

COPY (
	SELECT
		COUNT(b.bici),
		b.nome_stazione_prelievo,
		b.numero_stazione_prelievo,
		DATE_TRUNC('hour', b.data_prelievo) AS ora_prelievo
	FROM bikemi_rentals b
	WHERE EXTRACT('year' FROM b.data_prelievo) < 2019
	GROUP BY 
		b.nome_stazione_prelievo,
		b.numero_stazione_prelievo,
		DATE_TRUNC('hour', b.data_prelievo)
	ORDER BY ora_prelievo ASC
) TO '/Users/luca/tesi/data/bikemi-rentals_csv/bikemi-stations-hourly_rentals.csv' DELIMITER ',' CSV HEADER;
