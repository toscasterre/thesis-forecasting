#!/usr/bin/env bash

# csv_into_postgres.sh dir1 dir2...

source "$ZDOTDIR/colors.zsh"

for DIR in $@; do

    cd $DIR

    echo -e "\n${BOLD}${BLUE}=>${WHITE} Checking if table ${BLUE}${DIR}${WHITE} exists${RESET}"
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
    echo ""

    for CSV in *.csv; do

        COLS="$( head -1 ${CSV} )"
        
        echo "${BOLD}${CYAN}==>${WHITE} Copying data from ${CYAN}${CSV} ${WHITE}to ${BLUE}${DIR} ${WHITE}PostgreSQL database${RESET}"
        psql -c "SET datestyle TO iso, dmy; COPY ${DIR}(${COLS}) FROM '$(pwd)/${CSV}' DELIMITER ',' CSV HEADER;" bikemi

    done

    cd ..

    # zip all files and remove them
    echo -e "\n${BOLD}${BLUE}=>${WHITE} Backing up ${BLUE}${DIR}${RESET}"
    zip -r "${DIR}_csv.zip" ${DIR} && rm -rf ${DIR}

done
