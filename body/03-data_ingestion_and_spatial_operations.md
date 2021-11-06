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
# path manipulation
from pathlib import Path

# data manipulation
import pandas as pd
import geopandas
import numpy as np

# connecting to the local database with the data
import psycopg2

# plotting
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as cx

# to use pandas dtypes in matplotlib plots
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
%matplotlib inline

# set settings for seaborn
sns.set_style(style="whitegrid", rc={"grid.color": ".9"})
sns.set_palette(palette="deep")

# store the palette
sns_c = sns.color_palette(palette="deep")  # will be useful later

# customise matplotlib and sns plot dimensions
plt.rcParams["figure.figsize"] = [12, 6]
plt.rcParams["figure.dpi"] = 100
title_font = {"fontname": "DejaVu Sans Mono"}

# create paths
data_path = Path(Path.cwd().parents[0] / "data")
milan_data = Path(data_path / "milan")

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

The data available ranges from the first of June, 2015, to the first of October, 2020, totalling to 15.842.891 observations. Data was made available in Excel spreadsheets, following the [Office Open XML SpreadsheetML File Format](https://docs.microsoft.com/en-us/openspecs/office_standards/ms-xlsx/f780b2d6-8252-4074-9fe3-5d7bc4830968) (the `.xlsx` file format). Python"s Pandas library has methods to read `.xlsx` files; however, given how big these files are, data manipulation would have proven unfeasible.

For this reason, we resorted to some useful and popular open source tools, which we used to build `bash` scripts and functions to automate conversion from `.xlsx` to `.csv` files, perform some elementary data cleaning and load the data into a local PostgreSQL database. Format conversion to Comma-Separated Values (`.csv`) was performed using [`csvkit`](https://github.com/wireservice/csvkit), a Python package to perform basic operations on `.csv` files from the command line. Being written in Python, `csvkit` can be slow. However, as part of a major trend for several command-line applications, `csvkit` was rewritten in Rust, a fast and secure programming language whose popularity has been rising in the last couple of years <cite id="jf5wt">(Perkel, 2020)</cite>. Much alike Julia <cite id="ge16g">(Perkel, 2019)</cite>, Rust is becoming a tool for data science, as well as scientific computing (for example in bio-statistics) as it is "a language that offer[s] the "expressiveness" of Python but the speed of languages such as C and C++" <cite id="1xb31">(Perkel, 2020)</cite>.

The Rust port of `csvkit` is called [`xsv`](https://github.com/BurntSushi/xsv), and is blazing fast. Much alike `awk` <cite id="tcloo">(<i>Gawk - GNU Project - Free Software Foundation (FSF)</i>, n.d.)</cite>, `xsv` can perform filtering operations, but also joins and partitions, as well as computing summary statistics. `xsv` does not offer format conversion (yet), but was used to filter out a negligible number of invalid observations from each original `.xslx` files (after the conversion to `.csv`), and select only the columns that would enter the final dataset.

Finally, `psql` (PostgreSQL"s command line utility) was used to upload the "clean" data into a local database instance. PostgreSQL was also used to perform basic survey statistics, like computing the number of rows, and data aggregation (such as counting the number of observations by year). Looking at the frequency tables by year, there appears to be an oddly small number of observations from 2018. This is because there is indeed missing data from June 2018 until the end of the year. For this reason, we chose to work only with data from June 2015 to the end of May 2018.

```{code-cell} ipython3
query = """
    SELECT
        EXTRACT("year" FROM b.data_prelievo) AS date,
        COUNT(b.bici)
    FROM bikemi_source_data b
    -- WHERE EXTRACT("year" FROM b.data_prelievo) < 2019
    GROUP BY EXTRACT("year" FROM b.data_prelievo);
"""

pd.read_sql(sql=query, con=conn).astype("int")
```

+++ {"tags": [], "jp-MarkdownHeadingCollapsed": true}

## Data Analysis

+++ {"tags": [], "jp-MarkdownHeadingCollapsed": true}

### Remove Outliers and Select the Time Span

+++

In addition to selecting only trips from June 2015 to June 2018, we also disregard all rentals whose duration is smaller than one minute - as previously done in the literature. This leaves us with more than 11,7 million observations. We store these in a [materialised view](https://www.postgresql.org/docs/current/sql-creatematerializedview.html):

```{code-cell} ipython3
query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS bikemi_rentals AS (
        SELECT
            b.tipo_bici,
            b.cliente_anonimizzato,
            DATE_TRUNC("second", b.data_prelievo) AS data_prelievo,
            b.numero_stazione_prelievo,
            b.nome_stazione_prelievo,
            DATE_TRUNC("second", b.data_restituzione) AS data_restituzione,
            b.numero_stazione_restituzione,
            b.nome_stazione_restituzione,
            b.durata_noleggio
        FROM bikemi_source_data b
        WHERE
            EXTRACT("year" FROM b.data_restituzione) < 2019 AND
            durata_noleggio > interval "1 minute"
    );
"""
```

+++ {"tags": [], "jp-MarkdownHeadingCollapsed": true}

### Top Users and Commuting Habits

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
        EXTRACT("year" FROM data_prelievo) AS anno,
        COUNT(DISTINCT cliente_anonimizzato)
    FROM bikemi_rentals
    GROUP BY EXTRACT("year" FROM data_prelievo);
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
        EXTRACT("year" FROM data_prelievo) AS anno
    FROM bikemi_rentals b
    GROUP BY
        cliente_anonimizzato,
        EXTRACT("year" FROM data_prelievo)
    ORDER BY noleggi_totali DESC
"""

pd.read_sql(query, conn).astype({"anno": "int"}).head(10).set_index("cliente_anonimizzato")
```

As expected, there are more observations from the years 2016 and 2017 as these are complete years. The great number of usage translates to an average of almost 4 trips per day - i.e., to reach the first train station and then the workplace.

+++ {"tags": [], "jp-MarkdownHeadingCollapsed": true}

### Usage Patterns and Origin-Destination Matrix

+++

As a starter, it is useful to look at the origin-destination (OD) matrix, to see which are the most popular starting and departure points. On the aggregate level, the most popular points on the OD matrix are the train stations and sightseeing places such as Duomo.

```{code-cell} ipython3
top_departure_stations_query = """
    SELECT
        nome_stazione_prelievo,
        COUNT(*) AS numero_noleggi
    FROM bikemi_rentals
    GROUP BY
        nome_stazione_prelievo
    ORDER BY numero_noleggi DESC;
"""

top_departure_stations = pd.read_sql(top_departure_stations_query, conn)

top_arrival_stations_query = """
    SELECT
        nome_stazione_restituzione,
        COUNT(*) AS numero_noleggi
    FROM bikemi_rentals
    GROUP BY
        nome_stazione_restituzione
    ORDER BY numero_noleggi DESC;
"""

top_arrival_stations = pd.read_sql(top_arrival_stations_query, conn)

pd.concat([top_departure_stations, top_arrival_stations], axis=1).head(10)
```

The ranking is basically unchanged if we look only at data from Monday to Friday and within "core" commuting hours (say, from 7 to 10 and from 17 to 20). However, trips towards stations become more frequent and destinations such as Moscova are slightly less popular. Indeed, employees might straight bike to Moscova after work to take a sip from their Negroni.

```{code-cell} ipython3
top_departure_stations_query = """
    SELECT
        nome_stazione_prelievo,
        COUNT(*) AS numero_noleggi
    FROM bikemi_rentals
    WHERE
        EXTRACT("dow" FROM data_restituzione) BETWEEN 0 AND 4 AND
        EXTRACT("hour" FROM data_restituzione) BETWEEN 7 AND 10 OR
        EXTRACT("hour" FROM data_restituzione) BETWEEN 17 AND 20
    GROUP BY
        nome_stazione_prelievo
    ORDER BY numero_noleggi DESC;
"""

top_departure_stations = pd.read_sql(top_departure_stations_query, conn)

top_arrival_stations_query = """
    SELECT
        nome_stazione_restituzione,
        COUNT(*) AS numero_noleggi
    FROM bikemi_rentals
    WHERE
        EXTRACT("dow" FROM data_restituzione) BETWEEN 0 AND 4 AND
        EXTRACT("hour" FROM data_restituzione) BETWEEN 7 AND 10 OR
        EXTRACT("hour" FROM data_restituzione) BETWEEN 17 AND 20
    GROUP BY
        nome_stazione_restituzione
    ORDER BY numero_noleggi DESC;
"""

top_arrival_stations = pd.read_sql(top_arrival_stations_query, conn)

pd.concat([top_departure_stations, top_arrival_stations], axis=1).head(10)
```

The behaviour changes if we look ad the individual trips, i.e. if we `GROUP BY` both departure and destination stations (`nome_stazione_prelievo` and `nome_stazione_restituzione`). To be exact, `Coni Zugna Solari` is close to both the station in Porta Genova as well as the Navigli and Darsena, which partly explains its popularity.

```{code-cell} ipython3
query = """
    SELECT
        nome_stazione_prelievo,
        numero_stazione_prelievo,
        nome_stazione_restituzione,
        numero_stazione_restituzione,
        COUNT(*) AS numero_noleggi
    FROM bikemi_rentals
    GROUP BY
        nome_stazione_prelievo,
        numero_stazione_prelievo,
        nome_stazione_restituzione,
        numero_stazione_restituzione
    ORDER BY numero_noleggi DESC;
"""

trips_rankings = pd.read_sql(query, conn)

trips_rankings.head(10)
```

The same considerations apply when looking at the commuting hours:

```{code-cell} ipython3
query = """
    SELECT
        nome_stazione_prelievo,
        numero_stazione_prelievo,
        nome_stazione_restituzione,
        numero_stazione_restituzione,
        COUNT(*) AS numero_noleggi
    FROM bikemi_rentals
    WHERE
        EXTRACT("dow" FROM data_restituzione) BETWEEN 0 AND 4 AND
        EXTRACT("hour" FROM data_restituzione) BETWEEN 7 AND 10 OR
        EXTRACT("hour" FROM data_restituzione) BETWEEN 17 AND 20
    GROUP BY
        nome_stazione_prelievo,
        numero_stazione_prelievo,
        nome_stazione_restituzione,
        numero_stazione_restituzione
    ORDER BY numero_noleggi DESC;
"""

trips_rankings_commuting_hours = pd.read_sql(query, conn)

trips_rankings_commuting_hours.head(10)
```

This reinforces the conclusion that BikeMi is consistently used for commuting purposes. However, this data can be better explored including its spatial representation.

+++

## Spatial Data Analysis

+++ {"citation-manager": {"citations": {"tfga6": [{"id": "7765261/RZW74C9X", "source": "zotero"}]}}, "tags": []}

On its open data portal, the Comune di Milano publishes all sorts of open data - like the daily entrances in the so-called Area C, where access to private cars is limited. On this treasure trove of data, we can also find things like the location of column fountains and newsstands, but also the geo-referenced data of bike tracks and the location of [BikeMi Stations](https://dati.comune.milano.it/it/dataset/ds65_infogeo_aree_sosta_bike_sharing_localizzazione_). As noted previously, the service has some 320 stations, spread unevenly across the town, as it was outlined by previous studies <cite id="tfga6">(Saibene &#38; Manzi, 2015)</cite>. As a starter, we filter out all stations that have been introduced after 2019. This leaves us with 281 official stations, versus 279 in the historic data.

```{code-cell} ipython3
bikemi_stalls = (
    geopandas.read_file(Path(milan_data / "bikemi-stalls.geo.json"))
    .filter(["numero", "nome", "zd_attuale", "anno", "geometry"])
    .rename(columns={"numero": "numero_stazione", "zd_attuale": "municipio" })
    .set_index("numero_stazione")
    .query("anno < 2019")
    .astype({"anno": "int"})
)

# bikemi_stalls.to_csv(Path(milan_data / "bikemi-stalls.csv"))

bikemi_stalls.head()
```

The data is represented with the (geographic) coordinate reference system (CRS) `EPSG:4326`, but in order to use the `contextily` library we need to cast it to the (projected) reference system `EPSG:3587`. As the map shows, the stalls stretch to the North, towards Bicocca and Sesto San Giovanni. We can already see that the stalls distribution outside the city centre follows bike lanes (in blue).

```{code-cell} ipython3
bike_lanes = geopandas.read_file(Path(milan_data / "transports-bike_lanes.geo.json"))

fig, ax = plt.subplots(1, 1, figsize=(10, 10))

bikes_dict = {"color": "firebrick", "marker": "."}

bikemi_stalls.to_crs(3857).plot(ax=ax, **bikes_dict)
bike_lanes.to_crs(3857).plot(ax=ax)
cx.add_basemap(ax)

plt.axis("off")

plt.title("BikeMi Stalls (Red Dots) and Bike Lanes (Blue)", **title_font)

plt.show()
```

### Inspecting Stations with Zero Daily Rentals

+++ {"tags": []}

The stalls in the outer stations are not as used as the ones in the city centre, which come up as an abundance of zeros in the data aggregated at daily and hourly level. Some of these stations are practically unused. Besides, the great count of stations would represent a problem in the context of multivariate regressions (the so-called $p > n$ problem). Hence, we can drop the unused stations from our data to help us reduce the dimensionality.

We start by creating another two `materialised views` with the daily and hourly rentals, by station. Since the service is only active between 7 and 24, we just keep hourly observations within that time span. If we simply were to `GROUP BY` station names and time units, we would obtain series with gaps in the time index. We first create a table with all possible combinations of stations and dates using a `CROSS JOIN` and a common table expression (or `CTE`), then left join on this table the values obtained via the `GROUP BY` on the reference table. A similar query is used to obtain the hourly rentals, with hourly time intervals instead of daily ones.

```{code-cell} ipython3
# query with cross join used to create the second materialised view
# another similar one is used to create the view for hourly observations
materialised_view_daily_rentals = """
    WITH cross_table AS (SELECT
        d.date AS data_partenza,
        s.nome AS stazione_partenza,
        s.numero_stazione
    FROM bikemi_stalls s
    CROSS JOIN (
       SELECT generate_series (timestamp "2015-06-01"
                             , timestamp "2018-06-01"
                             , interval  "1 day")::date
       ) d(date)
    ORDER BY nome, date ASC)

    SELECT
        c.data_partenza,
        c.stazione_partenza,
        c.numero_stazione,
        COUNT(b.*) AS noleggi_giornalieri
    FROM cross_table c
    LEFT JOIN bikemi_rentals b
        ON b.numero_stazione_prelievo = c.numero_stazione
        AND DATE_TRUNC("day", b.data_prelievo)::date = c.data_partenza
    GROUP BY
        c.data_partenza,
        c.stazione_partenza,
        c.numero_stazione
    ORDER BY stazione_partenza, data_partenza ASC;
"""

retrieve_daily_rentals = """
    SELECT * FROM daily_rentals;
"""

daily_rentals = pd.read_sql(retrieve_daily_rentals, conn).set_index("data_partenza")
```

Then, we compute the number of null values in the data (`null_obs`), pivot the table to wider format and compute the percentage of missing values in each station (`null_obs`). Using Pandas"`cut()` method, we can convert this numerical column into a categorical variable (`null_obs_ranking`) and choose the number of levels - five, in our case - to split the column into even intervals with.

```{code-cell} ipython3
obs_number = daily_rentals.index.unique().shape[0]

stations_missing_obs = (
    daily_rentals[[col for col in daily_rentals.columns if "numero_stazione" not in col]]
    .pivot(columns="stazione_partenza")
    .replace(0, np.nan)
    .isna().sum()
    .sort_values(ascending=False)
    .pipe(pd.DataFrame)
    # drop the redundant index
    .droplevel(0)
    .rename({0: "null_obs"}, axis=1)
    # create the % by dividing the number of null values by the length of the datetime idnex
    .assign(pct_null=lambda x: x.null_obs / obs_number)
)

# labels for the categorical variable, assumed to be ascending order
labels = ["very_low", "low", "average", "high", "very_high"]

stations_missing_obs["null_obs_ranking"] = pd.cut(
    stations_missing_obs["pct_null"], bins=5, labels=labels
)
```

In this way, we can see that the number of stations with an "unacceptable" number of missing values is smaller than thirty.

```{code-cell} ipython3
sns.histplot(stations_missing_obs, x="null_obs_ranking")

plt.xlabel("Percentage of null values")
plt.ylabel("")
plt.title("Frequency Distribution of Null Values Across Bikemi Stations", **title_font)

sns.despine()

plt.show()
```

More than 80 percent of the stations display a count of null observations inferior to 20 percent.

```{code-cell} ipython3
sns.ecdfplot(stations_missing_obs, x="pct_null")

plt.xlabel("Percentage of null values")
plt.ylabel("")
plt.title("Empirical Cumulative Distribution of Null Values Across BikeMi Stations", **title_font)

sns.despine()

plt.show()
```

We can also join this data with the station spatial data to plot them. While this does not expose patterns that could be used to reduce the dimensionality of the data, it shows that there are some stations that need to be dropped off even from the most crowded areas in the city. This could not be spotted before as, to the best of our knowledge, no one in the BikeMi literature has ever found a way to take into account of how public work on roads and infrastructure had effects on the bike sharing service.

```{code-cell} ipython3
bikemi_stalls_nulls = (
    bikemi_stalls
    .merge(stations_missing_obs, left_on="nome", right_index=True)
)

fig, ax = plt.subplots(1, 1, figsize=(10, 10))

(
    bikemi_stalls_nulls
    .to_crs(3857)
    .plot(
        column="null_obs_ranking",
        cmap="coolwarm",
        marker=".",
        legend=True,
        ax=ax)
)

cx.add_basemap(ax)

plt.axis("off")

plt.title("Bikemi Stalls, by Null Values (Low Usage)", **title_font)

plt.show()
```

### Area of Analysis

+++ {"citation-manager": {"citations": {"sopwq": [{"id": "7765261/RZW74C9X", "source": "zotero"}]}}, "tags": []}

Besides dropping the "emptiest" stations, we should also come up with a way to narrow down the geographic area inside which we perform the analysis. Previously, authors have chosen to analyse just the area inside the Bastioni, or "Area C" <cite id="sopwq">(Saibene &#38; Manzi, 2015)</cite>. This choice seems restricting, as it leaves out most of the train stations.

```{code-cell} ipython3
area_c = geopandas.read_file(Path(milan_data / "administrative-area_c.geo.json")).filter(["tipo", "geometry"]).query("tipo == 'AREA_C'")

fig, ax = plt.subplots(figsize=(10, 10))

area_c.to_crs(3857).plot(ax=ax, cmap="Pastel1", alpha=0.6)
bikemi_stalls.to_crs(3857).plot(ax=ax, **bikes_dict)
cx.add_basemap(ax)

plt.axis("off")

plt.title("BikeMi Stalls (dots) and Area C (red)", **title_font)

plt.show()
```

+++ {"tags": []}

For the purpose of our analysis, this would be simply too limiting and it would be better to widen the range. The following map depicts the distribution of train and metro stations that fall within the city of Milan, shaded in blue:

```{code-cell} ipython3
metro_stations = geopandas.read_file(Path(milan_data / "transports-metro_stops.geo.json"))

# train_stations = geopandas.read_file(Path(milan_data / "transports-train_stations.zip"))
# train_stations.to_file("../data/milan/milan-transports-train_stations.geo.json", driver="GeoJSON")

train_stations = geopandas.read_file(Path(milan_data / "transports-train_stations.geo.json"))

municipi = (
    geopandas
    .read_file(Path(milan_data / "administrative-municipi.geo.json"))
    .rename(str.lower, axis=1)
    .filter(["geometry", "municipio"])
)

nil = (
    geopandas
    .read_file(Path(milan_data / "administrative-nil.geo.json"))
    .rename(str.lower, axis=1)
    .filter(["id_nil", "nil", "geometry"])
)

milan = municipi.dissolve().rename({"municipio": "milano"}, axis=1)
```

```{code-cell} ipython3
milan_train_stations = train_stations.to_crs(4326).sjoin(milan)
milan_metro_stations = metro_stations.sjoin(milan)

fig, ax = plt.subplots(1, 1, figsize=(10, 10))

trains_dict = {"color": "tab:blue", "marker": "X"}
metro_dict = {"color": "rebeccapurple", "marker": "^"}

nil.to_crs(3857).plot(ax=ax, alpha=0.2)
milan_train_stations.to_crs(3857).plot(ax=ax, **trains_dict)
milan_metro_stations.to_crs(3857).plot(ax=ax, **metro_dict)
cx.add_basemap(ax)

plt.axis("off")

plt.title("Train Stations (Blue) and Metro Stations (Orange) in Milan", **title_font)

plt.show()
```

To avoid taking too many stations in, we choose to work only with those that fall inside the road ring that encapsulates Milan. This is arguably limiting, as the area does not take in Lambrate and Villapizzone/Bovisa train stations. However, one might argue that it is unlikely for to choose to go to Lambrate and then rent a bike to get to the city centre, as they can just get to Centrale; the same goes for the other stations. In other words, this area contains the sufficient amount of stations to provide a useful forecast for the policymaker, albeit neglecting the outer stalls.

This approach might just reinforce the bias towards the centre of the city, but given the technical constraints seems to be the more viable option. However, as a comparison, the Area C would only contain one train station, whereas this area contains all of the top rentals stalls from the origin-destination (OD) matrix.

```{code-cell} ipython3
area_circonvallazione = geopandas.read_file(Path(milan_data / "custom-area_circonvallazione.geo.json"))
train_stations_circ = train_stations.to_crs(4326).sjoin(area_circonvallazione)
metro_stations_circ = metro_stations.sjoin(area_circonvallazione)
bikemi_stalls_circ = bikemi_stalls_nulls.sjoin(area_circonvallazione)

fig, ax = plt.subplots(1, 1, figsize=(10, 10))

train_stations_circ.to_crs(3857).plot(ax=ax, **trains_dict)
metro_stations_circ.to_crs(3857).plot(ax=ax, **metro_dict)
bikemi_stalls_circ.to_crs(3857).plot(ax=ax, **bikes_dict)
cx.add_basemap(ax)

plt.axis("off")

plt.title("BikeMi Stalls and Stations Inside the Circonvallazione", **title_font)

plt.show()
```

## Retrieve Data Aggregated at Station-Level

```{code-cell} ipython3
# when the station_columns is specified, data for each station is retrieved
station_daily_outflow = (
    rf.retrieve_bike_flow(
        table="bikemi_2019",
        station_column=["nome_stazione_prelievo", "stazione_partenza"],
    )
    # it"s easier if we don"t pivot to wider immediately
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

This shows - as expected - that some stations are basically not used at all, while some others are quite popular. Let"s try to categorise them:

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

We don"t need to save the wide `DataFrame` too, as we can pivot the table with ease.

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
