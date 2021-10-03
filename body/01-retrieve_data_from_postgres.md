---
jupytext:
  formats: notebooks///ipynb,body///md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Data Ingestion

## Import Libraries

```{code-cell} ipython3
import pandas as pd

pd.options.plotting.backend = "plotly"  # change to an interactive plotting backend

import custom_functions.plot_styles as ps

# custom functions
import custom_functions.retrieval_functions as rf

# plotting library
import plotly.express as px
```

To resolve the `Pylance(reportMissingImports)`, you have to add to `.vscode/settings.json` the paths from which you import what's needed in `"python.analysis.extraPaths"`:

```json
{
    "python.pythonPath": "C:\\Anaconda3\\envs\\bikemi_win\\bin\\python",
    "python.analysis.extraPaths": [
        "./notebooks/"
    ]
}
```

+++

## Check in on the PostgreSQL Server
First, we run a custom script to check if the `PostgreSQL` server is started or to start it.

```{code-cell} ipython3
!bash $MYBINS/pg_server_status

# in alternative:
# get_ipython().system('bash $MYBINS/pg_server_status')
```

As explained in the previous chapter, inserting the data into an SQL database enables faster operations on the data - which in this case amount in mostinstances to `GROUP BY`. Data is hence served much faster.

Now, two datasets are retrieved:

* The **daily outflow for the whole municipality** of Milan.
* The **daily outflow for each station** in the city.
 
The custom function`retrieve_bike_flow` has an argument, `time_column` which has a predefined value: `{"data_prelievo": "giorno_partenza"}`. This implies that the function will retrieve data aggregated on the time by which the bikes leave the station and not when they are returned once the ride is finished. In other words,by default the daily outflow will be retrieved.

Besides, the parameter `trunc` is set to default to `day`: this will mean that the `time_column` will be aggregated to the **daily level** - but this parameter can be set to other time units, such as `hour` to retrive hourly data. Regardless, we expect the daily aggregation to yield better overall results, as the hourly data becomes quite more noisy, especially when considering a single time series for each station.

+++

## Retrieve Data Aggregated at the Municipality Level

```{code-cell} ipython3
# when no argument other than the table name is specified, daily data for Milan is retrieved
daily_outflow = rf.retrieve_bike_flow(table="bikemi_2019")
daily_outflow.head()
```

```{code-cell} ipython3
# let's get some info
daily_outflow.info()
```

The data already has a `DateTimeIndex`, which can easily be indexed. There are no null values - which we can also check in the following way.

```{code-cell} ipython3
# display NaNs
daily_outflow.isna().sum()
```

Note that there are 366 observations (instead of 365). This happens because the original data (retrieved from an `.xlsx` file) contains some trips that occurred on the last day of the year. In other words, in the record there are some observations coming from the following year.

We can check how many there are just by looking at the last row:

```{code-cell} ipython3
daily_outflow.tail()
```

We can also check the number of trips that finished in the 2020 (i.e., the `daily_inflow`) by retrieving the data aggregating on `stazione_destinazione`, i.e. the arrival point:

```{code-cell} ipython3
daily_inflow = rf.retrieve_bike_flow(
    table="bikemi_2019",
    time_column=["data_restituzione", "giorno_restituzione"],
)

daily_inflow.tail()
```

This discrepancy suggests that some data from 2020 was spilled into the 2019 Excel. To deal with this, we can just drop the last row, then we can save it to a `.csv` file for the next steps.

```{code-cell} ipython3
daily_outflow[:"2019-12-31"].to_csv("../data/bikemi_csv/daily_outflow.csv")
```

## Retrieve Data Aggregated at Station-Level

```{code-cell} ipython3
# when the station_columns is specified, data for each station is retrieved
station_daily_outflow = (
    rf.retrieve_bike_flow(
        table="bikemi_2019",
        station_column=["nome_stazione_prelievo", "stazione_partenza"],
    )
    # it's easier if we don't pivot to wider immediately
    # .pipe(rf.pivot_bike_flow, cols="stazione_partenza")
    # .fillna(0) later
    .convert_dtypes().sort_values(  # make double into integers
        by=["giorno_partenza", "stazione_partenza"], ascending=False
    )
)

station_daily_outflow.tail()
```

At first glance, there appears to be quite a few missing values. We also need to get rid of the January 2020 data:

```{code-cell} ipython3
station_daily_outflow = station_daily_outflow.loc[
    station_daily_outflow.index != "2020-01-01"
]
```

Then we look into the missing data:

```{code-cell} ipython3
station_wide = station_daily_outflow.pivot(columns="stazione_partenza")
```

```{code-cell} ipython3
station_missing_obs = (
    station_wide.isnull()
    .sum()
    .reset_index()
    .rename(columns={"index": "station_name", 0: "missing_obs"})
)

station_missing_obs.head()
```

```{code-cell} ipython3
station_missing_obs["pct_missing"] = station_missing_obs["missing_obs"] / 366 * 100

station_missing_obs.sort_values("pct_missing", ascending=False).head(10)
```

This shows - as expected - that some stations are basically not used at all, while some others are quite popular. Let's try to categorise them:

```{code-cell} ipython3
labels = ["very_high", "high", "average", "low", "very_low"]

station_missing_obs["usage_ranking"] = pd.cut(
    station_missing_obs["pct_missing"], bins=5, labels=labels
)
```

`pd.cut()` will always return a `category` `dtype`. These can also be further manipulated via [`pandas.DataFrame.cat.set_categories()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.cat.set_categories.html) (works with `pandas.Index` and `pandas.DataFrame` too.)

We can tabulate and plot this data:

```{code-cell} ipython3
# `.size()` counts the number of member in each category
fig = (
    station_missing_obs.groupby("usage_ranking")
    .size()
    .plot(
        kind="barh",
        template="none",
        labels=dict(value="count", usage_ranking=""),
        title="Stations Ranked by Missing Values (%)",
    )
)

ps.plotly_style(fig)

fig.show()
```

Before saving the data to a `.csv` file, we should replace the missing observations with `0`:

```{code-cell} ipython3
station_daily_outflow.fillna(0).to_csv("../data/bikemi_csv/station_daily_outflow.csv")
```

We don't need to save the wide `DataFrame` too, as we can pivot the table with ease.

+++

## Hourly Data

We could also extract hourly data, but we argued it will be noisy:

```{code-cell} ipython3
# we can also extract the hourly data at the aggregate level:
hourly_outflow = rf.retrieve_bike_flow(table="bikemi_2019", trunc="hour")
```

```{code-cell} ipython3
ps.plotly_style(hourly_outflow.plot(title="Hourly Bike Count, 2019"))
```