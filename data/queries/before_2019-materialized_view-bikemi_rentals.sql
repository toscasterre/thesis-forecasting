DROP MATERIALIZED VIEW IF EXISTS bikemi_rentals.bikemi_rentals_before_2019 CASCADE;

CREATE MATERIALIZED VIEW IF NOT EXISTS bikemi_rentals.bikemi_rentals_before_2019 AS
(
SELECT b.bici,
       b.tipo_bici,
       b.cliente_anonimizzato,
       date_trunc('second'::text, b.data_prelievo)     AS data_prelievo,
       b.numero_stazione_prelievo,
       b.nome_stazione_prelievo,
       date_trunc('second'::text, b.data_restituzione) AS data_restituzione,
       b.numero_stazione_restituzione,
       b.nome_stazione_restituzione,
       b.durata_noleggio
FROM bikemi_source_data b
WHERE EXTRACT(year FROM b.data_restituzione) < 2019::numeric
  AND b.durata_noleggio > '00:01:00'::interval
    );
