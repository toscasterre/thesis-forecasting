SELECT
    d.data_partenza,
    d.noleggi_giornalieri,
    d.stazione_partenza,
    d.numero_stazione AS id_stazione,
    s.nil,
    s.id_nil
FROM daily_rentals_all d
JOIN bikemi_selected_stalls s ON s.numero_stazione = d.numero_stazione