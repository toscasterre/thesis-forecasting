---
jupytext:
  formats: notebooks///ipynb,body///md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.10.3
kernelspec:
  display_name: Bike Sharing Forecasting
  language: python
  name: bikemi
---

# BikeMi Data

```{code-cell} ipython3
# data manipulation
import pandas as pd
import geopandas as gpd

# connecting to the local database with the data
import psycopg2

# plotting
import plotly.express as px
import matplotlib.pyplot as plt
import contextily as cx

# establish connection with the database
conn = psycopg2.connect("dbname=bikemi user=luca")
```

+++ {"tags": [], "jp-MarkdownHeadingCollapsed": true}

## Data Ingestion

+++

The data was made available thanks to a partnership established by Prof. Giancarlo Manzi of the University of Milan and Clear Channel Italia, the provider of the service. The data is comprised of all the individual trips performed by each client (`cliente_anonimizzato`). This includes the bike type (which can either be a regular bike or an electric bike), the bike identifier, the station of departure and arrival with the time, the duration of the trip `durata_noleggio` plus the total travel distance. We do not know how the total travel distance `distanza_totale` is computed.

```{code-cell} ipython3
query = """
    SELECT *
    FROM bikemi_source_data
    LIMIT 5;
"""

pd.read_sql(sql=query, con=conn)
```

+++ {"citation-manager": {"citations": {"tcloo": [{"id": "7765261/2TTUU9QV", "source": "zotero"}], "jf5wt": [{"id": "7765261/NQ8DBQNG", "source": "zotero"}], "ge16g": [{"id": "7765261/574YW5KY", "source": "zotero"}], "1xb31": [{"id": "7765261/NQ8DBQNG", "source": "zotero"}]}}, "tags": []}

The data available ranges from the first of June, 2015, to the first of October, 2020, totalling to 15.842.891 observations. Data was made available in Excel spreadsheets, following the [Office Open XML SpreadsheetML File Format](https://docs.microsoft.com/en-us/openspecs/office_standards/ms-xlsx/f780b2d6-8252-4074-9fe3-5d7bc4830968) (the `.xlsx` file format). Python's Pandas library has methods to read `.xlsx` files; however, given how big these files are, data manipulation would have proven unfeasible.

For this reason, we resorted to some useful and popular open source tools, which we used to build `bash` scripts and functions to automate conversion from `.xlsx` to `.csv` files, perform some elementary data cleaning and load the data into a local PostgreSQL database. Format conversion to Comma-Separated Values (`.csv`) was performed using [`csvkit`](https://github.com/wireservice/csvkit), a Python package to perform basic operations on `.csv` files from the command line. Being written in Python, `csvkit` can be slow. However, as part of a major trend for several command-line applications, `csvkit` was rewritten in Rust, a fast and secure programming language whose popularity has been rising in the last couple of years <cite id="jf5wt">(Perkel, 2020)</cite>. Much alike Julia <cite id="ge16g">(Perkel, 2019)</cite>, Rust is becoming a tool for data science, as well as scientific computing (for example in bio-statistics) as it is "a language that offer[s] the 'expressiveness' of Python but the speed of languages such as C and C++" <cite id="1xb31">(Perkel, 2020)</cite>.

The Rust port of `csvkit` is called [`xsv`](https://github.com/BurntSushi/xsv), and is blazing fast. Much alike `awk` <cite id="tcloo">(<i>Gawk - GNU Project - Free Software Foundation (FSF)</i>, n.d.)</cite>, `xsv` can perform filtering operations, but also joins and partitions, as well as computing summary statistics. `xsv` does not offer format conversion (yet), but was used to filter out a negligible number of invalid observations from each original `.xslx` files (after the conversion to `.csv`), and select only the columns that would enter the final dataset.

Finally, `psql` (PostgreSQL's command line utility) was used to upload the 'clean' data into a local database instance. PostgreSQL was also used to perform basic survey statistics, like computing the number of rows, and data aggregation (such as counting the number of observations by year). Looking at the frequency tables by year, there appears to be an oddly small number of observations from 2018. This is because there is indeed missing data from June 2018 until the end of the year. For this reason, we chose to work only with data from June 2015 to the end of May 2018.

```{code-cell} ipython3
query = """
    SELECT
        EXTRACT('year' FROM b.data_prelievo) AS date,
        COUNT(b.bici)
    FROM bikemi_source_data b
    -- WHERE EXTRACT('year' FROM b.data_prelievo) < 2019
    GROUP BY EXTRACT('year' FROM b.data_prelievo);
"""

pd.read_sql(sql=query, con=conn).astype("int")
```

## BikeMi Data Analysis 

+++

### Finalising Data Selection

+++

In addition to selecting only trips from June 2015 to June 2018, we also disregard all rentals whose duration is smaller than one minute - as previously done in the literature. This leaves us with more than 11,7 million observations. We store these in a [materialised view](https://www.postgresql.org/docs/current/sql-creatematerializedview.html):

```{code-cell} ipython3
query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS bikemi_rentals AS (
        SELECT
            b.tipo_bici,
            b.cliente_anonimizzato,
            DATE_TRUNC('second', b.data_prelievo) AS data_prelievo,
            b.numero_stazione_prelievo,
            b.nome_stazione_prelievo,
            DATE_TRUNC('second', b.data_restituzione) AS data_restituzione,
            b.numero_stazione_restituzione,
            b.nome_stazione_restituzione,
            b.durata_noleggio
        FROM bikemi_source_data b
        WHERE
            EXTRACT('year' FROM b.data_restituzione) < 2019 AND
            durata_noleggio > interval '1 minute'
    );
"""
```

### Users and Patterns

```{code-cell} ipython3
query = """
    SELECT
        COUNT(DISTINCT cliente_anonimizzato)
    FROM bikemi_rentals;
    """

pd.read_sql(query, conn)
```

The service has almost 200 thousands unique subscribers in the time period. Then breakdown by year is the following:

```{code-cell} ipython3
query = """
    SELECT
        EXTRACT('year' FROM data_prelievo) AS anno,
        COUNT(DISTINCT cliente_anonimizzato)
    FROM bikemi_rentals
    GROUP BY EXTRACT('year' FROM data_prelievo);
    """

pd.read_sql(query, conn).astype({"anno": "int"}).set_index("anno")
```

The number of subscriptions is declining in 2015 and 2018, as there are observations for six months only. In particular, for the year 2018 the count is even lower because the autumn/winter months are missing.

It is also interesting to look at the top users:

```{code-cell} ipython3
query = """
    SELECT
        cliente_anonimizzato,
        COUNT(*) AS noleggi_totali
    FROM bikemi_rentals b
    GROUP BY
        cliente_anonimizzato
    ORDER BY noleggi_totali DESC
"""

users_ranking = pd.read_sql(query, conn).set_index("cliente_anonimizzato")

users_ranking.head(10)
```

But it might be of greater interest to look at the distribution by year:

```{code-cell} ipython3
query = """
    SELECT
        cliente_anonimizzato,
        COUNT(*) AS noleggi_totali,
        EXTRACT('year' FROM data_prelievo) AS anno
    FROM bikemi_rentals b
    GROUP BY
        cliente_anonimizzato,
        EXTRACT('year' FROM data_prelievo)
    ORDER BY noleggi_totali DESC
"""

pd.read_sql(query, conn).astype({"anno": "int"}).head(10).set_index("cliente_anonimizzato")
```

As expected, there are more observations from the years 2016 and 2017 as these are complete years. The great number of usage translates to an average of almost 4 trips per day - i.e., to reach the first train station and then the workplace.

+++

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
