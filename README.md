# Deep Neural Networks for Time Series Forecasting: An Effort Worth Pursuing?

This is the repository for my graduate thesis on neural forecasting, i.e. the application of deep learning to time series forecasting.

* Capture correlation between series 

## Structure of the repo

```bash
.
├── README.md
├── environment.yml
├── data
├── notebooks
├── research_journal
└── scripts
```

* `README.md` is this file
* `environment.yml` can be used to re-create the `conda` environment I am using via `conda create env --file environment.yml`
* `data` contains the data that can be published (?).
* `notebooks` contains the notebooks with the analysis.
* `research_journal` has some of my considerations I wrote down. Actually, most of my errands are stored in a local knowledge tree with [logseq](https://github.com/logseq/logseq).
* `scripts` contains the custom shell scripts I have written to process the data.


# To Do List

## Part 0: Data Ingestion

- [x] Scripts to automate data import into the SQL database
- [x] Clean multivariate data:
  - [x] `NaN` to `0`.

## Part 1: Univariate Time Series

Two analyses, then compare the results

* Aggregate data for Milan
* Aggregate data for each station

- [ ] Time Series Decomposition?
- [ ] ARIMA model
  - [ ] Choose the metrics
  - [ ] Transformations: log? box-cox?
  - [ ] First Differences
  - [ ] Seasonal Differences
- [ ] SARIMA
- [ ] Prophet
- [ ] SARIMAX if weather data

## Part 2: Multivariate Time Series with Deep Neural Networks