#!/usr/bin/env bash

# copies all csv in a relative or absolute path to a table (with the same name) in bikemi PostgreSQL database
# csv_into_postgres path/to/dir1 path/to/dir2
# will put all csv in path/to/dir1 and path/to/dir2 to the tables named dir1 and dir2 into bikemi

# TO DO
# use getopts to specify database
# use getopts to specify source and target directory

# for colored text output
source "./formatting_colors"

for DIR in "$@" ; do

    # temporarily cd into $DIR, both as relative or absolute path
    pushd "$DIR" || exit

    # to deal with relative paths deeper than 1
    # e.g. "path/to/dir" instead of "dir"
    # FYI, the opposite of `basename` is `dirname`
    TABLE_NAME="$(basename "$DIR")"

    echo -e "\n${BOLD}${BLUE}=>${WHITE} Checking if table ${BLUE}${TABLE_NAME}${WHITE} exists${RESET}"
    psql -c "SET datestyle TO iso, dmy;

        CREATE TABLE IF NOT EXISTS ${TABLE_NAME} (
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

        COLS="$( head -1 "$CSV" )"
        
        echo "${BOLD}${CYAN}==>${WHITE} Copying data from ${CYAN}${CSV} ${WHITE}to table ${BLUE}${TABLE_NAME} ${WHITE}in the PostgreSQL database${RESET}"
        psql -c "SET datestyle TO iso, dmy; COPY ${TABLE_DIR}(${COLS}) FROM '$(pwd)/${CSV}' DELIMITER ',' CSV HEADER;" bikemi
        # `$(pwd)/${CSV}` is used just because I am scared

    done

    # zip all files
    echo -e "\n${BOLD}${BLUE}=>${WHITE} Backing up ${BLUE}${DIR}${RESET}"
    zip -r "../${TABLE_NAME}_csv.zip" "${DIR}"
        
    # reverts back to original directory and deletes $DIR
    popd && rm -rf "$DIR"

done
