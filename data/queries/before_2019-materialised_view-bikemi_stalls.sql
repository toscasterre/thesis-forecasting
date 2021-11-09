CREATE MATERIALIZED VIEW IF NOT EXISTS bikemi_stalls_before_2019 AS (
    SELECT *
    FROM bikemi_stations
    WHERE anno < 2019
);