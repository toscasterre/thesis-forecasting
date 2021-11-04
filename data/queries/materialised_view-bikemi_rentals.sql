CREATE MATERIALIZED VIEW IF NOT EXISTS bikemi_rentals AS (
    SELECT
	b.bici,
        b.tipo_bici,
        b.cliente_anonimizzato,
        DATE_TRUNC('second', b.data_prelievo) AS data_prelievo,
        b.numero_stazione_prelievo,
        b.nome_stazione_prelievo,
        DATE_TRUNC('second', b.data_restituzione) AS data_restituzione,
        b.numero_stazione_restituzione,
        b.nome_stazione_restituzione,
        b.durata_noleggio
    FROM bikemi_source_data b
    WHERE
        EXTRACT('year' FROM b.data_restituzione) < 2019 AND
        durata_noleggio < interval '1 minute'
);