#!/usr/bin/env bash

source $ZDOTDIR/.zsh-colors

# dove sono: anywhere
# che cosa faccio
# 1. unzippo i file in input, dentro una cartella temporanea che ha il nome del file + tmp. la cartella si trova in ~/tesi/data/bikemi_csv

for ZIP in $@; do
    
    TMP_DIR="${ZIP/.zip/}_tmp" # ${ZIP/<pattern_to_replace>/<pattern_to_substitute>/}
    echo "${BOLD}Creating the temporary dir ${TMP_DIR}${RESET}"
    mkdir "$TMP_DIR"
    cd "$TMP_DIR" # cd into the tmp dir to execute the script

    # unzip the file
    echo -e "${BOLD}${BLUE}=> ${WHITE}Unzipping ${BLUE}${ZIP}${RESET}"
    unzip "../${ZIP}"
    
    echo ""
    for FILE in *.xlsx; do
        # removes all sequences of whitespaces and replaces them with "_" 
        # see: http://plasmasturm.org/code/rename/
        echo "${BOLD}${CYAN}==> ${WHITE}Cleaning ${CYAN}${FILE} ${WHITE}filename${RESET}"
        rename --nows "$FILE"
    done

    for FILE in *.xlsx; do
        # convert from xlsx to csv
        echo -e "\n${BOLD}${GREEN}==> ${WHITE}Converting ${GREEN}${FILE} ${WHITE}to ${GREEN}${FILE/.xlsx/.csv}${RESET}"
        in2csv "$FILE" > "${FILE/.xlsx/.csv}"

        # remove the original file
        rm "$FILE"

        # clean the headers of the csv
        echo "${BOLD}${GREEN}==> ${WHITE}Cleaning ${GREEN}${FILE/.xlsx/.csv} ${WHITE}headers${RESET}"
        clean_headers "${FILE/.xlsx/.csv}"
    done

    cd ..

done

