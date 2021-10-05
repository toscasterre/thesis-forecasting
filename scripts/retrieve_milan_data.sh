#! /usr/bin/env bash

get_data () {

    DD_DIR="$1"
    DOWNLOAD_FILE="$2"
    URL="$3"

    # if the download dir does not exist, create it
    [[ -d "$DD_DIR" ]] || mkdir -p "$DD_DIR"

    echo -e "\n${BOLD}${BLUE}==>${RESET} ${BOLD}Downloading ${CYAN}${DOWNLOAD_FILE}${RESET}${BOLD} to ${BLUE}${DOWNLOAD_DIR}/${DD_DIR}${RESET}"
    curl "$URL" -o "$DD_DIR/$DOWNLOAD_FILE"

}

source "./formatting_colors"

DOWNLOAD_DIR=${1:-"$HOME/tesi/data"}

pushd "$DOWNLOAD_DIR" 1>/dev/null || exit

get_data bikemi_metadata bikemi_stalls.csv "https://dati.comune.milano.it/dataset/cc065002-cd21-4dcb-b84f-bba2fd9e0c86/resource/4c31029c-22c9-49f7-b145-91374feac41c/download/bikemi_stazioni.csv"

get_data milan nil.geojson "https://dati.comune.milano.it/dataset/e8e765fc-d882-40b8-95d8-16ff3d39eb7c/resource/9c4e0776-56fc-4f3d-8a90-f4992a3be426/download/ds964_nil_wm.geojson"

get_data milan nil.csv "https://dati.comune.milano.it/dataset/e8e765fc-d882-40b8-95d8-16ff3d39eb7c/resource/3fce7202-0076-4a7b-ac2c-d2ab9b5dc658/download/ds964_nil_wm_4326.csv"

get_data milan municipi.geojson "https://dati.comune.milano.it/dataset/36ba21c2-8b48-43ce-bbe1-e236a8a49ff6/resource/99ecd085-0b04-4fb2-a66e-9795694d4fc4/download/ds379_municipi_label.geojson"

get_data milan municipi.csv "https://dati.comune.milano.it/dataset/36ba21c2-8b48-43ce-bbe1-e236a8a49ff6/resource/ebb1e5e3-fde1-46dd-8501-fa03ecb5d4bf/download/ds379_municipi_label_4326.csv"

get_data milan area_c.geojson "https://dati.comune.milano.it/it/dataset/d7d9179a-8228-427f-9c86-1e30154be4fe/resource/d788b26b-31b4-4e57-992d-276a1280c8c2/download/disciplina_aree.geojson"

get_data milan transports-metro_stops.geojson "https://dati.comune.milano.it/dataset/b7344a8f-0ef5-424b-a902-f7f06e32dd67/resource/dd6a770a-b321-44f0-b58c-9725d84409bb/download/tpl_metrofermate.geojson"

get_data milan transports-metro_stops.csv "https://dati.comune.milano.it/dataset/b7344a8f-0ef5-424b-a902-f7f06e32dd67/resource/0f4d4d05-b379-45a4-9a10-412a34708484/download/tpl_metrofermate.csv"

get_data milan transports-bus_stops.geojson "https://dati.comune.milano.it/dataset/ac494f5d-acd3-4fd3-8cfc-ed24f5c3d923/resource/7d21bd77-3ad1-4235-9a40-8a8cdfeb65a0/download/tpl_fermate.geojson"

get_data milan transports-bus_stops.csv "https://dati.comune.milano.it/dataset/ac494f5d-acd3-4fd3-8cfc-ed24f5c3d923/resource/2a52d51d-66fe-480b-a101-983aa2f6cbc3/download/tpl_fermate.csv"

popd 1>/dev/null || exit
