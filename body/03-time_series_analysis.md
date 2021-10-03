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

+++ {"tags": []}

# Time Series Analysis

+++

Let's plot the data to see some patterns that might be helpful to know in advance, before starting to model the data.

+++ {"incorrectly_encoded_metadata": "jp-MarkdownHeadingCollapsed=true", "tags": []}

## Import Libraries

```{code-cell} ipython3
:init_cell: true

# to add holidays features
import holidays

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

+++ {"incorrectly_encoded_metadata": "jp-MarkdownHeadingCollapsed=true", "tags": []}

## Load Data and Preprocessing

```{code-cell} ipython3
:init_cell: true

daily_outflow = pd.read_csv("../data/bikemi_csv/daily_outflow.csv", parse_dates=[0])

daily_outflow = (
    daily_outflow.assign(
        year=lambda x: x["giorno_partenza"].dt.year,
        month=lambda x: x["giorno_partenza"].dt.month,
        month_name=lambda x: x["giorno_partenza"].dt.month_name().astype("category"),
        week=lambda x: x["giorno_partenza"].dt.isocalendar().week,
        day=lambda x: x["giorno_partenza"].dt.weekday,
        is_weekend=lambda x: x["day"].apply(lambda day: 1 if day in [5, 6] else 0),
        day_name=lambda x: x["giorno_partenza"].dt.day_name(),
        day_of_month=lambda x: x["giorno_partenza"].dt.day,
        day_of_year=lambda x: x["giorno_partenza"].dt.dayofyear,
        # alternatively:
        # holiday = lambda ts: list(map(lambda x: holidays.CountryHoliday("IT").get(x), ts["giorno_partenza"]))
        holiday=lambda ts: ts["giorno_partenza"].apply(
            lambda x: holidays.CountryHoliday("IT").get(x)
        ).replace(to_replace=np.NaN, value="No"),
    )
    .set_index("giorno_partenza")
    .astype({
        "is_weekend": "category",
        "day_name": "category",
        "holiday": "category",
    })
)

daily_outflow.info()
```

Finally, let's see what our data looks like:

```{code-cell} ipython3
daily_outflow.head(10)
```

+++ {"incorrectly_encoded_metadata": "jp-MarkdownHeadingCollapsed=true", "tags": []}

# Time Series Plot

```{code-cell} ipython3
daily_outflow.plot(
    y="count",
    title="BikeMi Daily Rentals, 2019",
    color_discrete_sequence=px.colors.qualitative.T10,
).update_layout(**plotly_styles).update_traces(hovertemplate=None)
```

+++ {"incorrectly_encoded_metadata": "jp-MarkdownHeadingCollapsed=true", "tags": []}

# Rolling Statistics

+++

First, let's see how the mean and standard deviation change across time.

```{code-cell} ipython3
daily_outflow.plot(
    y=[
        "count",
        daily_outflow["count"].rolling(7).mean(),
        daily_outflow["count"].rolling(7).std(),
    ],
    title="Daily Rentals with Rolling Statistics (Window Size: 7)",
    color_discrete_sequence=px.colors.qualitative.Pastel,
).update_layout(**plotly_styles).update_traces(hovertemplate=None)
```

```{code-cell} ipython3
daily_outflow.plot(
    y=[
        "count",
        daily_outflow["count"].rolling(30).mean(),
        daily_outflow["count"].rolling(30).std(),
    ],
    title="Daily Rentals with Rolling Statistics (Window Size: 30)",
    color_discrete_sequence=px.colors.qualitative.Pastel,
).update_layout(**plotly_styles).update_traces(hovertemplate=None)
```

The most relevant thing about these statistics is that the seasonal component of the time series does not really smooth out even with a 30 days lag, suggesting a strong dependence even with past lags.

Given this distribution, we expect a strong relationship between data points that are seven lags from each other. More importantly, we expect that this variance will hinder the accuracy of our forecasts. This may require transforming the data (e.g. by taking logs or applying a Box-Cox transformation and searching for the optimal parameter $\lambda$) or *decomposing the time series*.

+++

### Non-Interactive Plot

+++

We can also make a pretty plot to export:

```{code-cell} ipython3
fig, ax = plt.subplots(2, 1, figsize=(12, 9), constrained_layout=True)

# create the windows
ma = [7, 30]

for i, m in enumerate(ma):

    daily_outflow[f"moving_average_{m}"] = (
        daily_outflow["count"].rolling(window=m).mean()
    )

    sns.lineplot(
        x=daily_outflow.index,
        y="count",
        label="count",
        data=daily_outflow,
        alpha=0.5,
        ax=ax[i],
    )
    sns.lineplot(
        x=daily_outflow.index,
        y=f"moving_average_{m}",
        label=f"moving_average_{m}",
        data=daily_outflow,
        color=sns_c[i + 1],
        ax=ax[i],
    )
    ax[i].legend(loc="upper left")
    ax[i].set(title="", ylabel="")

plt.suptitle("Bikemi Rentals (Daily) - Smooth Moving Average", y=1.02)
```

# Histograms

+++

Then, we look for patterns. First, let's see what changes across weekends and during holidays.

```{code-cell} ipython3
daily_outflow.plot.bar(
    x=daily_outflow.index,
    y="count",
    title="BikeMi Rentals against Weekends (2019)",
    color="is_weekend",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    labels={"count": "Rentals ", "giorno_partenza": "Date ", "is_weekend": "Weekend "},
).update_layout(**plotly_styles)
```

```{code-cell} ipython3
(
    daily_outflow.plot.bar(
        x=daily_outflow.index,
        y="count",
        title="Bikemi Rentals against Holidays (2019)",
        color="holiday",
        color_discrete_sequence=px.colors.qualitative.Vivid,
        labels={"count": "Rentals ", "giorno_partenza": ""},
    )
    .update_layout(**plotly_styles)
    .update_traces(hovertemplate=None)
)
```

# Other Kinds of Seasonalities: Monthly and Daily Data Distributions

+++

Let's have a closer look at seasonal patterns. We import some custom functions we developed to plot these special patterns:

+++ {"incorrectly_encoded_metadata": "jp-MarkdownHeadingCollapsed=true", "tags": []}

## Seasonal Plots

```{code-cell} ipython3
# play with color palettes: https://plotly.com/python/discrete-color/
(
    pd.pivot_table(
        data=daily_outflow[["day_name", "month_name", "count"]],
        index="day_name",
        columns="month_name",
    )["count"]
    .plot(color_discrete_sequence=px.colors.qualitative.Dark24)
    .update_layout(**plotly_styles)
    .update_traces(hovertemplate=None)
)
```

Looking at the series' plot, it seems clear that the most important source of variation clearly is the weekly seasonality. The boxplot function is designed to accept various time formats, so we can adapt it pretty quickly:

```{code-cell} ipython3
subunits_boxplot(daily_outflow["count"], y="count", time_subunit="weekday")
```

Note: the plot starts on Tuesday because the data starts on Tuesday and the categorical variable is coded with its first level to be that day.

+++ {"tags": []}

# Appendix: Functions for Rolling Statistics

+++

The following function work with matplotlib (plt)

```{code-cell} ipython3
from custom_functions.time_series_analysis import plt_rolling_statistics, px_rolling_statistics
```

```{code-cell} ipython3
plt_rolling_statistics(
    ts=daily_outflow["count"], lags=7, statistics=["mean", "std"]
)
```

```{code-cell} ipython3
plt_rolling_statistics(
    ts=daily_outflow["count"], lags=30, statistics=["mean", "std"]
)
```

```{code-cell} ipython3
px_rolling_statistics(
    ts=daily_outflow, col="count", lags=7, statistics=["mean", "std"]
)
```

```{code-cell} ipython3
px_rolling_statistics(
    ts=daily_outflow, col="count", lags=30, statistics=["mean", "std"]
)
```
