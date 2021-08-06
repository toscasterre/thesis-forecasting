# Notebook Walkthrough

A brief explanation of the content of this subdirectory of the repo.

```
.
├── custom_functions/
├── 00_retrieve_mila_data.ipynb
├── 01_retrieve_data.ipynb
├── 02_spatial_joins.ipynb
├── 03_univariate_tsa.ipynb
├── 04_arima_modelling.ipynb
└── README.md
```

* `custom_functions/` contains the custom functions written to improve readability and reduce boilerplate code,
* `00_retrieve_milan_data.ipynb`: retrieval of external data, such as the localised data of each station. There is also a script for that in `scripts/`.
* `01_retrieve_data.ipynb`: get the data for the analysis from the PostgreSQL server.
* `02_spatial_joins.ipynb`: combining the data obtained in notebooks `00` and `01` to aggregate the time series data at local neighbourhood level (NIL).
* `03_unvariate_tsa.ipynb`: visualisation of the unvariate time series at the city aggregation level.
* `04_arima_modelling.ipynb`: fitting of univariate time series models.
* `README.md`: this file.

