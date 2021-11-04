DROP MATERIALIZED VIEW IF EXISTS daily_rentals;

CREATE MATERIALIZED VIEW IF NOT EXISTS daily_rentals AS (
    WITH cross_table AS (SELECT
        d.date AS data_partenza,
        s.nome AS stazione_partenza,
        s.numero_stazione
    FROM bikemi_stalls s
    CROSS JOIN (
       SELECT generate_series (timestamp '2015-06-01'
                             , timestamp '2018-06-01'
                             , interval  '1 day')::date
       ) d(date)
    ORDER BY nome, date ASC)

    SELECT
        c.data_partenza,
        c.stazione_partenza,    
        c.numero_stazione,
        COUNT(b.*)::smallint AS noleggi_giornalieri
    FROM cross_table c
    LEFT JOIN bikemi_rentals b
        ON b.numero_stazione_prelievo = c.numero_stazione
        AND DATE_TRUNC('day', b.data_prelievo)::date = c.data_partenza
    GROUP BY
        c.data_partenza,
        c.stazione_partenza,
        c.numero_stazione
    ORDER BY stazione_partenza, data_partenza ASC
);