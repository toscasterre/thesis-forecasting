---
jupytext:
  formats: notebooks///ipynb,body///md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: PyCharm (tesi)
  language: python
  name: pycharm-dd017f2c
---

+++ {"incorrectly_encoded_metadata": "jp-MarkdownHeadingCollapsed=true", "tags": []}

# Time Series Analysis

```{code-cell} ipython3
:init_cell: true

# Base libraries
import numpy as np
import pandas as pd

# Data visualisations
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

# to use pandas dtypes in matplotlib plots
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

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

```{code-cell} ipython3
daily_outflow = pd.read_csv("../data/bikemi_csv/daily_outflow.csv", index_col=[0], parse_dates=[0])

daily_outflow.info()
```

+++ {"tags": []}

## First Decomposition

+++

We first use the Python library `statsmodels` to attempt an initial time series decomposition and see some patterns.

```{code-cell} ipython3
from statsmodels.tsa.seasonal import seasonal_decompose

weekly_seasonal_decomposition = seasonal_decompose(
    x=daily_outflow["count"],
    model="additive"
)

pd.options.plotting.backend = "matplotlib"
fig, ax = plt.subplots(4, 1, figsize=(12, 8), constrained_layout=True)

# observed values
weekly_seasonal_decomposition.observed.plot(c=sns_c[0], ax=ax[0])
ax[0].set(title="observed", xlabel="")

# trend
weekly_seasonal_decomposition.trend.plot(c=sns_c[1], ax=ax[1])
ax[1].set(title="trend", xlabel="")

# seasonality
weekly_seasonal_decomposition.seasonal.plot(c=sns_c[2], ax=ax[2])
ax[2].set(title="seasonal", xlabel="")

# residuals
weekly_seasonal_decomposition.resid.plot(c=sns_c[3], ax=ax[3])
ax[3].set(title="residual", xlabel="")

plt.suptitle("Daily Rentals Additive Seasonal Decomposition")

plt.show()
```

Just by looking at the residuals, we realise that the seasonal component is not filtered out in the most optimal way - the residual variance changes across time. One strategy might be to take logs and see if the residuals become less volatile. Let's see what changes with a multiplicative decomposition:

```{code-cell} ipython3
weekly_seasonal_decomposition = seasonal_decompose(
    x=daily_outflow["count"],
    model="multiplicative",
    period=7
)

pd.options.plotting.backend = "matplotlib"
fig, ax = plt.subplots(4, 1, figsize=(12, 8), constrained_layout=True)

# observed values
weekly_seasonal_decomposition.observed.plot(c=sns_c[0], ax=ax[0])
ax[0].set(title="observed", xlabel="")

# trend
weekly_seasonal_decomposition.trend.plot(c=sns_c[1], ax=ax[1])
ax[1].set(title="trend", xlabel="")

# seasonality
weekly_seasonal_decomposition.seasonal.plot(c=sns_c[2], ax=ax[2])
ax[2].set(title="seasonal", xlabel="")

# residuals
weekly_seasonal_decomposition.resid.plot(c=sns_c[3], ax=ax[3])
ax[3].set(title="residual", xlabel="")

plt.suptitle("Daily Rentals Multiplicative Seasonal Decomposition")

plt.show()
```

While the first part of the series is slightly better handled, the declining trend in the last part of the year translates into a much greater variance towards of the residuals at the end of the year.

+++ {"tags": []}

## Differencing

```{code-cell} ipython3
pd.options.plotting.backend = "plotly"
```

+++ {"tags": []}

### First Differencing

+++

First, let's see how first differencing impacts the data:

```{code-cell} ipython3
daily_outflow.plot(
    y=daily_outflow["count"].diff(),
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title="BikeMi Daily Rentals, First Differences (2019)",
).update_layout(**plotly_styles).update_traces(hovertemplate=None)
```

Clearly, taking first differences does not remove the seasonal component - but removes the trend and seemingly returns stationary data. However, as recommended in Hyndman (quote), we need to apply first the seasonal differencing.

First differencing remarks the time-varying nature of the seasonal component of the series, pointing ever more convincingly to an STL decomposition.

+++ {"tags": []}

### Seasonal Differencing

```{code-cell} ipython3
daily_outflow.plot(
    y=daily_outflow["count"].diff(7),
    color_discrete_sequence=px.colors.qualitative.Vivid,
    title="BikeMi Daily Rentals, Seasonal Differences (7 days, 2019)",
).update_layout(**plotly_styles).update_traces(hovertemplate=None)
```

There is a great variance in the series: around the end of April, there are consecutive days where there is a difference of ten thousand rentals. At first glance, it seems that seasonal differences do not make the series unequivocally stationary. Let's verify it with a statistical test:

```{code-cell} ipython3
from statsmodels.tsa.stattools import adfuller, kpss

adfuller_results = adfuller(
    # take seasonal diffs and drop the 7 missing values
    daily_outflow["count"].diff(7).dropna(),
    regression="ct"
)

kpss_results = kpss(
    daily_outflow["count"].diff(7).dropna(),
    regression="ct", nlags="auto"
)


console.print(
    f"""
Advanced Dickey-Fuller p-value is {adfuller_results[1]:.2%}: {"there is a unit root - i.e. the series is non-stationary"
    if adfuller_results[1] < 0.05 else "there is no unit root - the series is stationary"}.
KPSS p-value is {kpss_results[1]:.2%}: {"the series is stationary (there is no unit root)"
    if kpss_results[1] > 0.05 else "the series is non-stationary (there is a unit root)"}
    """
)
```

`statsmodels` guide summarises the ADFuller test in this way:

> The null hypothesis of the Augmented Dickey-Fuller is that there is a unit root, with the alternative that there is no unit root. If the p-value is above a critical size, then we cannot reject that there is a unit root.

The presence of a unit root signifies a non-stationary time series. The p-value is much smaller than 5%, so we can safely reject the null hypothesis: there is no unit root, i.e. the series is stationary.

THe Kwiatkowski-Phillips-Schmidt-Shin (KPSS) tests for the null hypothesis that a time series $x$ is level or trend stationary. In other words, we want the p-value to be greater than 5%: in this way, we fail to reject the null hypothesis and we can assume it is trend stationary.

`statsmodels` warns us that the test statistics are actually outside of the range of p-values available in the statistical table - this means that the p-value is greater than ten percent. This means we fail to reject the null and that our series is stationary.

However, we might not be satisfied with this - let's have a look at the double differences.

+++ {"tags": []}

### Log Double Differences

```{code-cell} ipython3
(
    daily_outflow
    .diff(1).diff(7).dropna() # remove missing values created by differencing
    .plot(
        color_discrete_sequence=px.colors.qualitative.Vivid,
        title="BikeMi Daily Rentals, Double Differences (1, 7) (2019)",
    )
    .update_layout(**plotly_styles)
    .update_traces(hovertemplate=None)
)
```

The series is more convincingly stationary, but still displays a large variance. We can see what happens if we take logs:

```{code-cell} ipython3
(
    daily_outflow
    .apply(np.log)
    .diff().diff(7)
    .plot(
        color_discrete_sequence=px.colors.qualitative.Vivid,
        title="BikeMi Daily Rentals, Logs, 1 and 7-Day Differences (2019)",
    )
    .update_layout(**plotly_styles)
    .update_traces(hovertemplate=None)
)
```

This transformation removes stationarity and seasonality but does not really deal with the variance in the data. We can use our human knowledge to explain some of this variation: holidays, first of all. Then we would expect the temperature to play a role, in conjunction with precipitation (i.e. the winter), which could explain the greater variance around the last months of the year.

This suggests that even a SARIMA model might not compete with something like Prophet, which can exploit holiday patterns and model piecewise trends. However, without the aid of external data, neither of the two models can take into account rainy days or colder weather - even via categorical variables such as dummies for each month. An ETS model could also exploit these patterns.

+++ {"tags": []}

## Autocorrelation and Partial Autocorrelation Plots

```{code-cell} ipython3
pd.options.plotting.backend = "matplotlib"
```

To complement the differencing, let's have a look at the autocorrelation functions.

```{code-cell} ipython3
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

fig, ax = plt.subplots(2, 1, constrained_layout=True)
plot_acf(
    x=daily_outflow["count"],
    ax=ax[0],
    title="BikeMi Rentals Autocorrelation",
    zero=False,
)
plot_pacf(
    x=daily_outflow["count"],
    ax=ax[1],
    title="BikeMi Rentals Partial Autocorrelation",
    zero=False,
)

plt.plot()
```

The autocorrelation plot shows a sinusoidal dependence with past lags; the first (and second) lags are significant, and so do the multiples of 7, even beyond the 30th lag. This fact should not be too surprising: we could already spot it from the 30-day window moving average but is still remarkable. This will likely entail a greater MA component for our (S)ARIMA models; in particular, the ACF suggests a moving average component with 1-2 lags and possibly even more seasonal lags. The partial autocorrelation function indicates an autoregressive component of 1 and a seasonal AR component of perhaps 1 lag.

+++ {"tags": []}

## STL Decomposition

+++ {"citation-manager": {"citations": {"hmqko": [{"id": "7765261/JEKFIWNG", "source": "zotero"}]}}, "tags": []}

STL decomposition exploits LOESS, i.e. locally estimated scatterplot smoothing, which can handle time-varying seasonality. However, as pointed out by Hyndman and ..., STL «does not handle a trading day or calendar variation automatically, and it only provides facilities for additive decompositions». This method was developed by <cite id="hmqko">(Cleveland et al., 1990)</cite>.

In `statsmodels`, the function to perform the STL decomposition is `STL`. It has the following categories of parameters:

Main parameters:

* `endog` is the data to be decomposed.
* `period` is the periodicity of the sequence. It is detected automatically if the data is provided as a Pandas `DataFrame`. For example, if the data is monthly, the period is 12. In our case, since the data is daily, the period will be 365. As of now, the problem with our data is that it only consists of 365 observations.
* `seasonal` is the length of the seasonal smoother and is set to 7 by default.
* `trend` is the length of the trend smoother. Must be an odd integer. If not provided uses the smallest odd integer greater than 1.5 * `period` / (1 - 1.5 / `seasonal`)
* `low_pass` is the length of the low-pass filter. Must be an odd integer >=3. If not provided, uses the smallest odd integer > period.

Degrees parameters, i.e. whether to use a constant or a constant and trend:

* `seasonal_degint` is the degree of seasonal LOESS. Accepted values are 0 (constant) or 1 (constant and trend).
* `trend_degint` is the degree of trend LOESS. Accepted values are 0 (constant) or 1 (constant and trend).
* `low_pass_degint` is the degree of low pass LOESS. Accepted values are 0 (constant) or 1 (constant and trend).

Interpolation step parameters:

* `seasonal_jumpint` is a positive integer determining the linear interpolation step. If larger than 1, the LOESS is used for every `seasonal_jump` point and linear interpolation is between fitted points. Higher values reduce estimation time.
* `trend_jumpint` is a positive integer determining the linear interpolation step. If larger than 1, the LOESS is used for every `trend_jump` point, and values between the two are linearly interpolated. Higher values reduce estimation time.
* `low_pass_jumpint` is the last positive integer determining the linear interpolation step. If larger than 1, the LOESS is used for every `low_pass_jump` point, and values between the two are linearly interpolated. Higher values reduce estimation time.

The function also has a `robustbool` flag, indicating whether to use a weighted version that is robust to some forms of outliers.

These defaults ensure that we can pretty much cast the function without tweaking the parameters

```{code-cell} ipython3
from statsmodels.tsa.seasonal import STL

stl_decomposition = STL(daily_outflow, period=7).fit()
```

```{code-cell} ipython3
fig, ax = plt.subplots(4, 1, figsize=(12, 8), constrained_layout=True)

stl_decomposition.observed.plot(c=sns_c[0], ax=ax[0])
ax[0].set(title="observed", xlabel="")
stl_decomposition.trend.plot(c=sns_c[1], ax=ax[1])
ax[1].set(title="trend", xlabel="")
stl_decomposition.seasonal.plot(c=sns_c[2], ax=ax[2])
ax[2].set(title="seasonal", xlabel="")
stl_decomposition.resid.plot(c=sns_c[3], ax=ax[3])
ax[3].set(title="residual", xlabel="")

plt.suptitle("STL Decomposition")

plt.show()
```

The results are remarkable: the seasonal component captures a great deal of variance - yet not all of it. The solution might be to employ a multiplicative decomposition - which cannot directly be attained by the STL decompositions and will require us to go through taking logs of the data.

```{code-cell} ipython3
stl_log_decomposition = STL(daily_outflow.apply(np.log), period=7).fit()
```

Before plotting, we need to revert the series to levels, applying an exponential transformation.

```{code-cell} ipython3
fig, ax = plt.subplots(4, 1, figsize=(12, 8), constrained_layout=True)

# observed values
stl_log_decomposition.observed.apply(np.exp).plot(c=sns_c[0], ax=ax[0])
ax[0].set(title="observed", xlabel="")

# trend
stl_log_decomposition.trend.apply(np.exp).plot(c=sns_c[1], ax=ax[1])
ax[1].set(title="trend", xlabel="")

# seasonality
stl_log_decomposition.seasonal.apply(np.exp).plot(c=sns_c[2], ax=ax[2])
ax[2].set(title="seasonal", xlabel="")

# residuals
stl_log_decomposition.resid.apply(np.exp).plot(c=sns_c[3], ax=ax[3])
ax[3].set(title="residual", xlabel="")

plt.suptitle("STL Decomposition Using Logs")

plt.show()
```
