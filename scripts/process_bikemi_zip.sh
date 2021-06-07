#!/usr/bin/env bash

source "$ZDOTDIR/.zsh-colors"

# dove sono: anywhere
# che cosa faccio
# 1. unzippo i file in input, dentro una cartella temporanea che ha il nome del file + tmp. la cartella si trova in ~/tesi/data/bikemi_csv

for ZIP in $@; do
    
    # name and create the extraction directory, starting from the filename
    EXTRACTION_DIR="${ZIP/.zip/}" # ${ZIP/<pattern_to_replace>/<pattern_to_substitute>/}
    echo "${BOLD}${BLUE}=> ${WHITE}Create the extraction directory ${BLUE}${EXTRACTION_DIR}${RESET}"
    mkdir "$EXTRACTION_DIR" && cd "$EXTRACTION_DIR"

    # unzip the file
    echo -e "${BOLD}${BLUE}=> ${WHITE}Unzip ${BLUE}${ZIP}${RESET}\n"
    unzip "../${ZIP}"
    echo ""

    for FILE in * ; do
        # removes all sequences of whitespaces and replaces them with "_" 
        # see: http://plasmasturm.org/code/rename/
        echo "${BOLD}${CYAN}==> ${WHITE}Rename ${CYAN}${FILE}${RESET}"
        rename --nows "$FILE"
    done
    echo ""

    # if files matches .xlsx, then convert to _temp.csv
    for XLSX in *.xlsx ; do
        echo "${BOLD}${GREEN}==> ${WHITE}Convert ${GREEN}${XLSX} ${WHITE}to ${GREEN}${XLSX/.xlsx/_temp.csv}${RESET}"
        in2csv "$XLSX" > "${XLSX/.xlsx/_temp.csv}" && rm "$XLSX"
    done
    echo ""

    # clean the headers of the csv and select columns
    for TEMP_CSV in *_temp.csv ; do     
        echo "${BOLD}${GREEN}==> ${WHITE}Clean ${GREEN}${TEMP_CSV} ${WHITE}headers${RESET}"
        clean_headers "${TEMP_CSV}"

        echo "${BOLD}${GREEN}==> ${WHITE}Select columns columns from ${GREEN}${TEMP_CSV}${RESET}"
        xsv select "1-3,5-7,10-12,15" "${TEMP_CSV}" > "${TEMP_CSV/_temp/}" && rm "${TEMP_CSV}"
    done
    
    cd ..

    # see if the server is running (custom script, just a fancy conditional)
    pg_server_status

    csv_into_postgres ${EXTRACTION_DIR}

done