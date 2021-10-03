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
  name: bikemi
---

+++ {"incorrectly_encoded_metadata": "tags=[] jp-MarkdownHeadingCollapsed=true"}

# Import Libraries and Load Data

```{code-cell} ipython3
:init_cell: true

# suppress future warnings
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

# Data visualisations
import matplotlib.pyplot as plt

# Base libraries
import numpy as np
import pandas as pd

# More data viz
import plotly.express as px
import seaborn as sns

# to use pandas dtypes in matplotlib plots
from pandas.plotting import register_matplotlib_converters

# rich
from rich.console import Console

# define rich console for formatted output
console = Console()

# have pandas types plotted with matplotlib
register_matplotlib_converters()

# set plotly as backend for plots wih pandas
pd.options.plotting.backend = "plotly"

# create a dict to update plotly layout
plotly_styles = dict(
    font_family="DejaVuSansMono Nerd Font",
    template="none",
    title={
        "x": 0.05,
        # basically, what part of the title to put at position "x"
        "xanchor": "left",
    },
)


# set settings for seaborn
sns.set_style(style="darkgrid", rc={"axes.facecolor": ".9", "grid.color": ".8"})
sns.set_palette(palette="deep")
sns_c = sns.color_palette(palette="deep")  # will be useful later

# visualise plots inline
%matplotlib inline

# customise matplotlib and sns plot dimensions
plt.rcParams["figure.figsize"] = [12, 6]
plt.rcParams["figure.dpi"] = 100
```

We use `squeeze=True` to indicate that our data has only one column and we want to retrieve a `pandas.Series` (see [here](https://machinelearningmastery.com/load-explore-time-series-data-python/))

```{code-cell} ipython3
daily_rentals = pd.read_csv(
    "../data/bikemi_csv/daily_outflow.csv", index_col=[0], parse_dates=[0], squeeze=True
).asfreq(
    freq="D"
)  # set frequency

print(f"Our data is a {type(daily_rentals)}")

daily_rentals
```

We also need to make sure our index has a frequency - which we did with `.asfreq("D")` above:

```{code-cell} ipython3
daily_rentals.index
```

+++ {"incorrectly_encoded_metadata": "jp-MarkdownHeadingCollapsed=true", "tags": []}

# Naïve forecaster

+++

We need to fit a naïve forecaster to have a benchmark for our other methods:

```{code-cell} ipython3
# to define forecasting horizon
from sktime.forecasting.base import ForecastingHorizon

# to perform train-test split
from sktime.forecasting.model_selection import temporal_train_test_split

# to establish the naive forecaster benchmark
from sktime.forecasting.naive import NaiveForecaster
```

+++ {"citation-manager": {"citations": {"11q8p": []}}, "incorrectly_encoded_metadata": "citation-manager={\"citations\": {\"11q8p\": [{\"id\": \"7765261/FETNQC8M\", \"source\": \"zotero\"}]}} tags=[] citation-manager={\"citations\": {\"11q8p\": []}} citation-manager={\"citations\": {\"11q8p\": []}}"}

We also need to choose the forecasting metrics. Since we will be forecasting several models on the same data, we can use both scale-dependent errors (mean absolute error, root mean squared error) and percentage errors (mean absolute percentage error). We can also employ a scaled error, such as the mean absolute scaled error (MASE, proposed by <cite id="11q8p">[NO_PRINTED_FORM]</cite>).

`mean_absolute_error`, `mean_squared_error`, `mean_absolute_percentage_error` and `mean_absolute_scaled_error` also have an argument for adding weights to the forecast.

```{code-cell} ipython3
from sktime.performance_metrics.forecasting import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_absolute_scaled_error,
    mean_squared_error,
)


def model_diagnostics(
    y_pred: pd.Series,
    y_true: pd.Series = y_test,
    y_train: pd.Series = y_train,
    mase: bool = True,
) -> pd.DataFrame:

    metrics = ["MAE", "RMSE", "MAPE"]

    scores = [
        mean_absolute_error(y_true, y_pred),
        mean_squared_error(y_true, y_pred, square_root=True),
        mean_absolute_percentage_error(y_true, y_pred, symmetric=False),
    ]

    if mase:
        metrics.append("MASE")
        scores.append(mean_absolute_scaled_error(y_true, y_pred, y_train=y_train))

    return pd.DataFrame({"metrics": metrics, "scores": scores})
```

We will be using a Seasonal Naive Forecaster (link Hyndman) where the predicted value is the one of the last seasonal value (i.e., 7 days before):

```{code-cell} ipython3
# perform train-test splitting
y_train, y_test = temporal_train_test_split(daily_rentals, test_size=0.1)

# uses all of the test set as forecasting horizon
fh = ForecastingHorizon(y_test.index, is_relative=False)

# naive forecaster model definition
naive_forecaster = NaiveForecaster(
    strategy="last",
    # weekly seasonal periodicity
    sp=7,
)

# naive forecaster model fitting
naive_forecaster.fit(y_train)

# naive forecaster predictions
naive_pred = naive_forecaster.predict(fh)

# naive forecaster error
naive_diagnostics = model_diagnostics(naive_pred, mase=False)

naive_diagnostics
```

Our model has 64% MAPE - whereas one might have expected something more. Let's plot it to see the differences:

```{code-cell} ipython3
from sktime.utils.plotting import plot_series

plot_series(daily_rentals, naive_pred, labels=["observed", "naive forecaster"])

plt.show()
```

# ARIMA Model

+++

The autocorrelation plot suggested us to use:

* an autoregressive component $p$ of 1
* an integration $d$ of order 1
* a moving average component $q$ of 1
* an autorgressive seasonal component $P$ of 2 with periodicity $m$ of 7
* an seasonal integration $D$ of order 1
* a moving average seasonal component $P$ of 3 with periodicity $M$ of 7

An interesting feature of the ARIMA class is that it provides arguments to perform cross validation directly within the model specification step:

```md
`out_of_sample_size` int, optional (default=0)
The number of examples from the tail of the time series to hold out and use as validation examples. The model will not be fit on these samples, but the observations will be added into the model’s endog and exog arrays so that future forecast values originate from the end of the endogenous vector. See update. For instance:

y = [0, 1, 2, 3, 4, 5, 6]
out_of_sample_size = 2
> Fit on: [0, 1, 2, 3, 4]
> Score on: [5, 6]
> Append [5, 6] to end of self.arima_res_.data.endog values

`scoring` str or callable, optional (default=’mse’)
If performing validation (i.e., if out_of_sample_size > 0), the metric to use for scoring the out-of-sample data:

* If a string, must be a valid metric name importable from sklearn.metrics.
* If a callable, must adhere to the function signature [...]
```

By default, the ARIMA model is fit with a trend and a constant.

```{code-cell} ipython3
from sktime.forecasting.arima import ARIMA

# model specification
arima = ARIMA(order=(3, 1, 3), seasonal_order=(3, 1, 3, 7), maxiter=500)

# model fitting
arima_fit = arima.fit(y_train)

# predictions
arima_pred = arima_fit.predict(fh)

# plot the model
plot_series(daily_rentals, arima_pred, labels=["observed", "arima"])

plt.show()
```

```{code-cell} ipython3
# arima model error
arima_diagnostics = model_diagnostics(arima_pred)
arima_diagnostics
```

The performance is just marginally better, compared to our naive forecaster. This can be due to multiple reason, the first one being the increase in volatility of the series in the winter months. This might hint that using external regressors might improve on the model, but as of this stage we cannot be sure. Ideally, we might want to find a way to tell the model to fit a steeper trend.

Scoring can also be computed directly using the following:

```python
arima.score(y_test)
```

By default, the algorithm will allow for a maximum of 50 iterations. This can mean that the estimator might not converge. We set `maxiter` to 500 as a precautionary measure.

Let's see the model summary:

```{code-cell} ipython3
arima.summary()
```

The seasonal MA components are insignificant, as we might have expected from looking at the ACF plot. Each $AR$ component is actually meaningful: we might try to fit more of them.

The Ljung-Box is a portmanteau test for autocorrelation of the residuals. Our model pass the tests, i.e. the errors are serially non-correlated.

```{code-cell} ipython3
ar = ARIMA()
```

# SARIMAX

+++

Since the fit is so poor, we might want to include some external (exogenous) predictors. This can simply be done via the `fit` interface. We can reuse the code from our previous chapter - we just need to drop columns containing a string and turn `holiday` into a binary categorical variable:

```{code-cell} ipython3
# to add holidays features
import holidays

exogenous = (
    pd.DataFrame(daily_rentals)
    .reset_index()
    .assign(
        # we cannot use this yet, as there is only one year of observations available
        # year=lambda x: x["giorno_partenza"].dt.year,
        month=lambda x: x["giorno_partenza"].dt.month,
        week=lambda x: x["giorno_partenza"].dt.isocalendar().week,
        day=lambda x: x["giorno_partenza"].dt.weekday,
        is_weekend=lambda x: x["day"].apply(lambda day: 1 if day in [5, 6] else 0),
        day_of_month=lambda x: x["giorno_partenza"].dt.day,
        day_of_year=lambda x: x["giorno_partenza"].dt.dayofyear,
        holiday=lambda ts: ts["giorno_partenza"].apply(
            lambda x: holidays.CountryHoliday("IT").get(x)
        ),
        is_holiday=lambda ts: ts["holiday"].apply(lambda x: 1 if x is not None else 0),
    )
    .set_index("giorno_partenza")
    .astype({"week": "int64"})
    .drop(columns=["count", "holiday"], axis=1)
    .asfreq(freq="D")
)

exogenous.head()
```

```{code-cell} ipython3
exogenous.info()
```

We need to perform the temporal time split on this exogenous matrix too:

```{code-cell} ipython3
X_train, X_test = temporal_train_test_split(exogenous, test_size=0.1)

# model specification
sarimax = ARIMA(order=(1, 1, 1), seasonal_order=(2, 1, 3, 7), maxiter=500)

# model fitting
sarimax.fit(y_train, X=X_train)

# predictions
sarimax_pred = arima.predict(fh, X_test)

# arima model error
sarimax_error = mean_absolute_percentage_error(y_test, sarimax_pred)

# plot the model
plot_series(daily_rentals, sarimax_pred, labels=["observed", "sarimax"])

plt.title(f"error: {round(sarimax_error * 100)}%")

plt.show()
```

The performance of this model is underwhelming, to say the least. If we look at the model summary, we can immediately see why:

```{code-cell} ipython3
sarimax.summary()
```

Every time component is statistically insignificant

+++

# Auto ARIMA

+++

The conclusion is pretty dire. Let's see if the AutoARIMA can improve on it:

```{code-cell} ipython3
from sktime.forecasting.arima import AutoARIMA

auto_arima = AutoARIMA(d=1, max_order=10, maxiter=500)  # differencing order

auto_arima.fit(y_train)

auto_arima_pred = auto_arima.predict(fh)

auto_arima_error = mean_absolute_percentage_error(y_test, auto_arima_pred)

plot_series(daily_rentals, auto_arima_pred, labels=["observed", "auto-arima"])

plt.title(f"error: {round(auto_arima_error * 100)}%")

plt.show()
```

# Prophet

```{code-cell} ipython3
from sktime.forecasting.fbprophet import Prophet
```
