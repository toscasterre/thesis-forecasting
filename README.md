# Deep Neural Networks for Time Series Forecasting: An Effort Worth Pursuing?

This is the repository for my graduate thesis on neural forecasting, i.e. the application of deep learning to time series forecasting.

* Capture correlation between series 

## Structure of the repo

```bash
.
├── README.md
├── .vscode
├── data
│   ├── arpa
│   ├── bikemi_csv
│   ├── bikemi_metadata
│   └── milan
├── environment.yml
├── jupyter/kernels/bikemi
├── notebooks
├── research_journal
├── scripts
├── tesi.code-workspace
└── thesis_body
```

* `README.md` is this file
* [`.vscode`](https://github.com/baggiponte/thesis-forecasting/tree/main/.vscode) settings and VS Code extensions.
* [`data`](https://github.com/baggiponte/thesis-forecasting/tree/main/data) contains:
  * [`arpa`](https://github.com/baggiponte/thesis-forecasting/tree/main/data/arpa) actually not needed
    * Could be exploited with time series for weather data from each measuring station.
  * [`bikemi_csv`](https://github.com/baggiponte/thesis-forecasting/tree/main/data/bikemi_csv): data for time series analysis.
  * [`bikemi_metadata`](https://github.com/baggiponte/thesis-forecasting/tree/main/data/bikemi_metadata): stalls locations.
  * [`milan`](https://github.com/baggiponte/thesis-forecasting/tree/main/data/milan): districts (Municipi) and neighborhoods (NIL) coordinates.
* [`environment.yml`](https://github.com/baggiponte/thesis-forecasting/tree/main/environment.yml) can be used to re-create the `conda` environment I am using via `conda create env --file environment.yml`
* [`jupyter/kernels/bikemi/`](https://github.com/baggiponte/thesis-forecasting/tree/main/jupyter/kernels/bikemi): take the `bikemi` folder and copy it to your `$JUPYTER_CONFIG_DIR` to get a kernel specification file. This creates the option to select the environment as a kernel for your Notebooks.
* [`notebooks`](https://github.com/baggiponte/thesis-forecasting/tree/main/environment.yml) contains the notebooks with the analysis.
* [`research_journal`](https://github.com/baggiponte/thesis-forecasting/tree/main/research_journal) has some of my considerations I wrote down. Actually, most of my errands are stored in a local knowledge tree with [logseq](https://github.com/logseq/logseq).
* [`scripts`](https://github.com/baggiponte/thesis-forecasting/tree/main/scripts) contains the custom shell scripts I have written to process the data.
* [`tesi.code-workspace`](https://github.com/baggiponte/thesis-forecasting/tree/main/tesi.code-workspace) the file to launch the project in Visual Studio Code

# Plan

## Technical Stuff:

- [ ] VM for traning and CV @marco @manzi
- [ ] Request data from beginning to 2020 (at least end of February) @manzi
- [ ] `{bookdown}` tutorial @marco

## 0 - Data

### 0.1 - Data Ingestion

- [x] Scripts to automate data import into the SQL database

### 0.2 - External Data

- [x] **Milan**
  - [x] Municipi 
  - [x] NIL
- [ ] Weather
  - Maybe too late

### 0.3 - Preprocessing

- [x] Clean multivariate data:
  - [x] `NaN` to `0`.
- [ ] Match stalls with Milan Data using `geopandas`
  - To obtain dummy/categoricals with NIL and Municipi to aggregate
- [x] Functions to get holidays and time series features

## 1 - Univariate Time Series

### 1.1 - Milan Aggregated Data

  - [ ] **Regression** with external data
    - Maybe only for multivariate to exploit correlations
    - Regularisation? @marco
  - [ ] **ARIMA**
    - [ ] Natural Level?
    - [ ] Transformations: log/box-cox?
    - [ ] First Diffences
    - [ ] Seasonal Differences
  - [ ] **SARIMA**
  - [ ] **Prophet**
  - [ ] **SARIMAX** only if time

### 1.2 - Aggregated Station Level 

* Analysing every single station may produce too much noise?
  * Come up with a baseline model to use to choose whether to use each time series, or the aggregation at NIL/Municipio.
  * **metrics**
  * **PCA** if time?

* Same as 1.1:

- [ ] **Regression** with external data
    - [ ] Regularisation to reduce dimensionality when using all TS
  - [ ] **ARIMA**
    - [ ] Natural Level?
    - [ ] Transformations: log/box-cox?
    - [ ] First Diffences
    - [ ] Seasonal Differences
  - [ ] **SARIMA**
  - [ ] **Prophet**
  - [ ] **SARIMAX** only if time

## 2 - Deep Learning

- [ ] Standardisation?