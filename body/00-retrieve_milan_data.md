---
jupytext:
  formats: notebooks///ipynb,body///md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.0
kernelspec:
  display_name: Deep Learning Forecasting
  language: python
  name: bikemi_win
---

# BikeMi Metadata and External Data

+++

Most of the data can be retrieved from [here](https://bikemi.com/dati-aperti/tempo-reale), via the official APIs. Every request must follow this template:

```bash
curl -H "Client-Identifier: IDENTIFIER" https://gbfs.urbansharing.com/bikemi.com/gbfs.json
```

Where `IDENTIFIER` must look like `mycompany-role`, as suggested. In our case, it would be `unimi-student`.

The files downloaded in this way are in `.json` format. However, the geographical information about bike stalls can also easily be retrived via [Comune di Milano's official Open Data Portal](https://dati.comune.milano.it/dataset/ds65_infogeo_aree_sosta_bike_sharing_localizzazione_/resource/4c31029c-22c9-49f7-b145-91374feac41c).

```{code-cell} ipython3
%%bash
mkdir -p ../data/bikemi_metadata && \
    curl "https://dati.comune.milano.it/dataset/cc065002-cd21-4dcb-b84f-bba2fd9e0c86/resource/4c31029c-22c9-49f7-b145-91374feac41c/download/bikemi_stazioni.csv" -o ../data/bikemi_metadata/bikemi_stalls.csv
```

## Neighbourhoods [NIL]

+++

Milan has 88 neighbourhoods (NIL, i.e. *nuclei di identità locale*), split across 9 Municipi (with some [overlappings](https://www.pgt.comune.milano.it/sites/default/files/allegati/NIL_Intro.pdf)). NIL data [was updated in April 2020](https://dati.comune.milano.it/dataset/e8e765fc-d882-40b8-95d8-16ff3d39eb7c) and the boundaries should be in place until 2030.

Data is available both as [`.geojson`](https://dati.comune.milano.it/dataset/ds964-nil-vigenti-pgt-2030/resource/9c4e0776-56fc-4f3d-8a90-f4992a3be426) and [`.csv`](https://dati.comune.milano.it/dataset/ds964-nil-vigenti-pgt-2030/resource/3fce7202-0076-4a7b-ac2c-d2ab9b5dc658).

```{code-cell} ipython3
%%bash
[ ! -d "../data/milan" ] && mkdir -p ../data/milan

echo "Retrieving NILs (.geojson)"
curl "https://dati.comune.milano.it/dataset/e8e765fc-d882-40b8-95d8-16ff3d39eb7c/resource/9c4e0776-56fc-4f3d-8a90-f4992a3be426/download/ds964_nil_wm.geojson" \
    -o ../data/milan/milan_nil.geojson

echo -e "\nRetrieving NILs (.csv)"
curl "https://dati.comune.milano.it/dataset/e8e765fc-d882-40b8-95d8-16ff3d39eb7c/resource/3fce7202-0076-4a7b-ac2c-d2ab9b5dc658/download/ds964_nil_wm_4326.csv" \
    -o ../data/milan/milan_nil.csv
```

*Municipi* data is also available in both formats, [here](https://dati.comune.milano.it/dataset/ds379-infogeo-municipi-superficie).

+++

## Municipi

```{code-cell} ipython3
%%bash
[ ! -d "../data/milan" ] && mkdir -p ../data/milan

echo "Retrieving Municipi (.geojson)"
curl "https://dati.comune.milano.it/dataset/36ba21c2-8b48-43ce-bbe1-e236a8a49ff6/resource/99ecd085-0b04-4fb2-a66e-9795694d4fc4/download/ds379_municipi_label.geojson" \
    -o ../data/milan/milan_municipi.geojson

echo -e "\nRetrieving Municipi (.csv)"
curl "https://dati.comune.milano.it/dataset/36ba21c2-8b48-43ce-bbe1-e236a8a49ff6/resource/ebb1e5e3-fde1-46dd-8501-fa03ecb5d4bf/download/ds379_municipi_label_4326.csv" \
    -o ../data/milan/milan_municipi.csv
```