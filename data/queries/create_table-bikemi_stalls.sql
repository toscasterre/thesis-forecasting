CREATE TABLE IF NOT EXISTS bikemi_stalls (
    numero_stazione SMALLINT
    , nome TEXT
    , municipio SMALLINT 
    , anno SMALLINT
    , geometry TEXT
);

COPY bikemi_stalls(numero_stazione, nome, municipio, anno, geometry)
    FROM '/Users/luca/tesi/data/milan/bikemi-stalls.csv'
    DELIMITER ',' CSV HEADER;