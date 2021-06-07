#!/usr/bin/env bash

source "$ZDOTDIR/.zsh-colors"

# dove sono: anywhere
# che cosa faccio
# 1. unzippo i file in input, dentro una cartella temporanea che ha il nome del file + tmp. la cartella si trova in ~/tesi/data/bikemi_csv

for ZIP in $@; do
    
    EXTRACTION_DIR="${ZIP/.zip/}" # ${ZIP/<pattern_to_replace>/<pattern_to_substitute>/}
    echo "${BOLD}${BLUE}> ${WHITE}Creating the extraction directory ${BLUE}${EXTRACTION_DIR}${RESET}"
    mkdir "$EXTRACTION_DIR" && cd "$EXTRACTION_DIR"

    # unzip the file
    echo -e "${BOLD}${BLUE}=> ${WHITE}Unzipping ${BLUE}${ZIP}${RESET}\n"
    unzip "../${ZIP}"
    
    echo ""
    # rename the files
    for FILE in *.xlsx; do
        # removes all sequences of whitespaces and replaces them with "_" 
        # see: http://plasmasturm.org/code/rename/
        echo "${BOLD}${CYAN}==> ${WHITE}Cleaning ${CYAN}${FILE} ${WHITE}filename${RESET}"
        rename --nows "$FILE"
    done

    echo ""
    # convert from xlsx to csv
    for FILE in *.xlsx; do
        # convert from xlsx to csv
        echo "${BOLD}${GREEN}==> ${WHITE}Converting ${GREEN}${FILE} ${WHITE}to ${GREEN}${FILE/.xlsx/_temp.csv}${RESET}"
        in2csv "$FILE" > "${FILE/.xlsx/_temp.csv}" && rm "$FILE"
    done
    
    echo ""
    # clean the headers of the csv
    for FILE in *.csv; do     
        echo "${BOLD}${GREEN}==> ${WHITE}Cleaning ${GREEN}${FILE} ${WHITE}headers${RESET}"
        clean_headers "${FILE}"

        echo "${BOLD}${GREEN}==> ${WHITE}Removing unnecessary columns from ${GREEN}${FILE}${RESET}"
        xsv select 1-3,5-7,10-12,15 "${FILE}" > "${FILE/_temp/}" && rm "${FILE}"
    done

    cd ..

done