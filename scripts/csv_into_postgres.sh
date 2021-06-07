#!/usr/bin/env bash

# csv_into_postgres.sh dir1 dir2...

source "$ZDOTDIR/.zsh-colors"

# see if the server is running (custom script)
pg_server_status

for DIR in $@; do

    cd $DIR

    echo "${BOLD}${BLUE}==>${WHITE} Checking if table ${BLUE}${DIR}${WHITE} exists${RESET}"
    psql -c "SET datestyle TO iso, dmy;

        CREATE TABLE IF NOT EXISTS ${DIR} (
            bici INT,
            tipo_bici VARCHAR(20),
            cliente_anonimizzato INT,
            data_prelievo TIMESTAMP,
            numero_stazione_prelievo INT,
            nome_stazione_prelievo TEXT,
            data_restituzione TIMESTAMP,
            numero_stazione_restituzione INT,
            nome_stazione_restituzione TEXT,
            distanza_totale REAL
        );" bikemi 

    for CSV in *.csv; do

        COLS="$( head -1 ${CSV} )"
        
        echo "${BOLD}${CYAN}==>${WHITE} Copying data from ${CYAN}${CSV}${RESET}"
        psql -c "SET datestyle TO iso, dmy; COPY ${DIR}(${COLS}) FROM '$(pwd)/${CSV}' DELIMITER ',' CSV HEADER;" bikemi

    done

    cd ..

done
