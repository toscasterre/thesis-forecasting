# for connections
import psycopg2

# for type stubs
from typing import Optional

# dataframes
import pandas as pd
# holidays
import holidays

# plotting
import matplotlib.pyplot as plt

# time series
import statsmodels.tsa.api as tsa
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# from plotnine import *  # plots à la ggplot


# use this to print out colored output with `print()`
class color:
    # define custom class to render formatted output
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def get_dict_items(dictio: dict) -> tuple:
    """Extract a tuple of key-value pairs from each dictionary item"""
    for key, value in dictio.items():
        return key, value


def retrieve_bike_flow(
    table: str,
    db_conn_detail: dict = {"dbname": "bikemi", "user": "luca"},
    # e.g. station_column = {"nome_stazione_prelievo" : "stazione_partenza"}
    # `None` as a type hint is replaced by `type(None)`
    station_column: None = None,
    # alternatively, {"data_restituzione" : "giorno_restituzione"}
    time_column: dict = {"data_prelievo": "giorno_partenza"},
        trunc: str = "day") -> pd.DataFrame:
    """
    From the PostgreSQL database, extract a DataFrame of the rental data,
    grouped at a certain time interval.
    The time interval is any argument accepted by SQL `DATE_TRUNC()`:
    it can be 'day', 'hour'...
    If `time_column` is `data_prelievo`, the function will return the outflow;
    if it is `data_restituzione` it will be the inflow.
    If `station_column` is specified, it returns a Series for each strall.
    Data is already indexed at the `time_column`.
    """
    db_conn = psycopg2.connect(
        "dbname = {dbname} user = {user}".format(**db_conn_detail))

    time_key, time_val = get_dict_items(time_column)

    if station_column is None:

        query = f'''
            SELECT
                DATE_TRUNC('{trunc}', {time_key}) AS {time_val},
                COUNT(bici)
            FROM {table}
            GROUP BY {time_val};
            '''
    else:
        station_key, station_val = get_dict_items(station_column)

        query = f'''
            SELECT
                {station_key} AS {station_val},
                DATE_TRUNC('{trunc}', {time_key}) AS {time_val},
                COUNT(bici)
            FROM {table}
            GROUP BY {time_val}, {station_val};
            '''

    return pd.read_sql(query, con=db_conn, index_col=f"{time_val}") \
        .sort_index()


def pivot_bike_flow(
        bike_flow: pd.Series,
        cols: list,
        vals: str = "count") -> pd.DataFrame:
    """Transform the flow into a panel dataframe (wide format)"""
    return bike_flow.pivot(columns=cols, values=vals)


def create_ts_features(
    dataframe: pd.DataFrame,
    features: list = ["day", "month"]
) -> pd.DataFrame:
    """
        Generates time-series features out of a dataframe.
        The index MUST be a DateTimeIndex.

        Args:
        dataframe ([type]):
            DateTimeIndex-ed Pandas DataFrame.

        features (list, optional):
            The number of features to extract.
            Defaults to ["day", "month", "year"].
            Possible values:
            ["hour", "day", "month", "is_weekend", "week",
            "year", "day_name", "month_name", "holidays"]

            One note: week numbers depend on the year.
            Sometimes the last days of one year may actually be part
            of the following years' first week, as it is the case with 2019.
            (this can help to spot the overlapping days:
            `dataframe.index.isocalendar().week.reset_index().groupby("week").size()`)

        Returns the same dataframe, but with new columns
    """

    if "hour" in features:
        dataframe["hour"] = dataframe.index.hour

    if "day" in features:
        dataframe["day"] = dataframe.index.day

    if "day_names" in features:
        dataframe["day_name"] = dataframe.index.day_name()

    if "weekends" in features:
        dataframe["is_weekend"] = dataframe.index.isocalendar().day \
            .apply(lambda x: 1 if x in [2, 3] else 0)

    if "week" in features:
        dataframe["week"] = dataframe.index.isocalendar().week

    if "month" in features:
        dataframe["month"] = dataframe.index.month

    if "month_name" in features:
        dataframe["month_name"] = dataframe.index.month_name()

    if "year" in features:
        dataframe["year"] = dataframe.index.year

    if "holidays" in features:

        ita_holidays = holidays.CountryHoliday(
            "IT",
            prov="MI",
            years=[year for year in list(dataframe.index.year.unique())]
        )

        # workaround to create the "holiday" column
        dataframe["dates"] = dataframe.index
        dataframe["holiday"] = dataframe["dates"] \
            .apply(lambda x: ita_holidays.get(str(x)))

    return dataframe


def get_time_format(time_unit: str) -> Optional[str]:
    """
    Takes a string such as "month" and returns
    the corresponding format for functions like `strftime`.

    Args:
    time_unit (string): a string with a time unit.
    Values accepted:
    ["year","month","weekday","hour","minute","second"]

    Returns:
    [string]: one of the following:
    ["%Y","%B","%A","%H","%M","%S"]
    """

    units_and_formats = {
        "year": "%Y",
        "month": "%B",
        "weekday": "%A",
        "hour": "%H",
        "minute": "%M",
        "second": "%S",
    }

    return units_and_formats.get(time_unit.lower())


def default_boxplot_props(
        line_width: float = 1.5,
        median_linewidth: float = 2.5,
        whiskers_linewidth: int = 1,
        median_color: str = "tomato") -> dict:
    # colors: https://matplotlib.org/stable/gallery/color/named_colors.html
    return dict(
        boxprops=dict(lw=line_width),
        medianprops=dict(lw=median_linewidth),
        whiskerprops=dict(lw=whiskers_linewidth),
        capprops=dict(lw=line_width)
    )


def subunits_boxplot(
        ts: pd.Series,
        y: str,
        time_subunit: str,
        boxplot_props: dict = default_boxplot_props()) -> None:
    """
    Plots a time-series y againsts a subunit of its time column/index.
    Accepted time-subunits are: year, month, weekday, hour, minute, second.
    """
    # duplicate the inputted time series to prevent overwriting
    ts_ = ts.copy()

    # obtain the time format from the input subunit
    # e.g. "%B" and "month"
    time_format = get_time_format(time_subunit)

    # create the new subunit column for pivoting
    ts_[time_subunit] = ts_.index.strftime(time_format)

    # create a sorting key to reorder columns after pivoting
    sorting_key = list(ts_.index.strftime(time_format).unique())

    # pivot time series and reorder columns
    df = ts_.pivot(columns=time_subunit, values=y).reindex(columns=sorting_key)

    fig, ax = plt.subplots()
    df.plot(
        kind="box", ax=ax,
        title=f"Daily Outflow of Bikes, {time_subunit.capitalize()} Boxplots",
        **boxplot_props
    )


def rolling_statistics(
        ts: pd.Series,
        lags: int,
        statistics: list = ["mean"]) -> None:
    """Plots the rolling statistics of a time series."""

    fig, ax = plt.subplots()

    # colors via tableau palette (tab:<colname>)
    ax.plot(ts, color="tab:blue", label="Observed Values")  # actual series

    if "mean" in statistics:  # if specified, plot rolling mean
        ax.plot(ts.rolling(lags).mean(),
                color="tab:red",
                label="Rolling Mean")

    if "std" in statistics:  # if specified, plot rolling standard deviation
        ax.plot(ts.rolling(lags).std(),
                color="tab:gray",
                label="Rolling Standard Deviation")

    if "mean" in statistics:
        if "std" in statistics:
            title = "Rolling Mean and Standard Deviation"
        else:
            title = "Rolling Mean"
    else:
        title = "Rolling Standard Deviation"

    title += f"\nWindow size: {lags}"

    ax.set_title(title)
    ax.legend(loc="best")
    plt.show()


def plot_acf_and_pacf(ts: pd.Series) -> None:
    """Plots pd.Series autocorrelation (ACF)
    and partial-autocorrelation function (PACF)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    plot_acf(ts, title="Autocorrelation (95% CI)", ax=ax1)
    plot_pacf(ts, title="Partial Autocorrelation (95% CI)", ax=ax2)
    plt.show()


def perform_adfuller(ts: pd.Series, regression: str = "ct") -> None:
    """
    Plots the rollign statistics of a time series,
    then performs the Advanced Dickey-Fuller test for stationarity.

    ADF Null Hypothesis is that there is a unit root,
    i.e. the series is non-stationary.
    To reject the null hypothesis (i.e., the series is stationary),
    the test statistics must be smaller than the critical value.

    Default test is with constant and trend.
    """

    # Advanced Dickey Fuller test:
    adf_results = tsa.adfuller(ts, regression=regression)

    results_string = f"""
        Test Statistics: {adf_results[0]}
        p-value: {adf_results[1]}\n
        Number of lags: {adf_results[2]}
        Number of observations: {adf_results[3]}\n
        Critical Value (1%): {adf_results[4].get("1%")}
        Critical Value (5%): {adf_results[4].get("5%")}
        Critical Value (10%): {adf_results[4].get("10%")}\n
        AIC: {adf_results[5]}\n
        {color.BOLD}The series is
        {f'{color.RED}non-' if adf_results[1] > 0.05 else ''}
        stationary {color.END}
        """
    print(results_string)

    # complicated version
    # for key, value in adf_results[4].items():
    #     if ad_res[0] > value:
    #         print(f"""
    #         We fail to reject the null hypothesis at the {key} level.
    #         The series appears to be non-stationary.
    #         """)
    #     else:
    #         print(f"""
    #         We reject the null hypothesis at the {key} level.
    #         The series appears to be stationary.
    #         """)
