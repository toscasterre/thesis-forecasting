import pandas as pd
import holidays

# for type stubs
from typing import Optional, List, Dict, Union

# plotting
import matplotlib.pyplot as plt
import plotly.express as px
import custom_functions.plot_styles as ps


def milan_holidays(ts: pd.DataFrame) -> pd.Series:
    """Requires a DataFrame with a DateTimeIndex"""
    ita_holidays = holidays.CountryHoliday(
        "IT",
        prov="MI",
        years=[year for year in list(ts.index.year.unique())]
    )

    # you cannot use `.apply()` on Indexes, but you
    # can cast an Index as a Series!
    return pd.DataFrame(ts.index, index=ts.index).iloc[:, 0] \
        .apply(lambda x: ita_holidays.get(str(x)))\
        .fillna("None").astype("category")


def create_ts_features(
    dataframe: pd.DataFrame,
    features: List[str] = ["day", "month"]
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
    # this can also work:
    # df['month'] = [d.strftime('%b') for d in df.Fu]

    if "hour" in features:
        dataframe["hour"] = dataframe.index.hour.astype("category")

    if "day" in features:
        dataframe["day"] = (dataframe.index.day.astype("int") + 1) \
            .astype("category")

    if "day_names" in features:
        dataframe["day_name"] = dataframe.index.day_name().astype("category")

    if "weekends" in features:
        dataframe["is_weekend"] = dataframe.index.isocalendar().day \
            .apply(lambda x: 1 if x in [6, 7] else 0).astype("category")

    if "week" in features:
        dataframe["week"] = dataframe.index.isocalendar() \
            .week.astype("category")

    if "month" in features:
        dataframe["month"] = dataframe.index.month.astype("category")

    if "month_name" in features:
        dataframe["month_name"] = dataframe.index.month_name() \
            .astype("category")

    if "year" in features:
        dataframe["year"] = dataframe.index.year.astype("category")

    if "holidays" in features:
        dataframe["holiday"] = milan_holidays(dataframe).astype("category")

    return dataframe


def px_default_legend_dict() -> Dict[str, Union[int, float, str]]:
    return {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1,
        "xanchor": "right",
        "x": 1
    }


def px_rolling_statistics(
        ts: pd.DataFrame,
        col: str,
        lags: int,
        statistics: List[str] = ["mean"],
        legend_args: Dict[str, Union[int, float, str]
                          ] = px_default_legend_dict()
) -> None:
    """
    Plots the rolling statistics of a time series using Plotly

    Takes as input a pd.DataFrame with a DateTimeIndex.

    """
    title = "BikeMi Daily Rentals - Rolling "
    series_name = ["observed_values"]
    cols_to_plot = [ts[col]]

    if "mean" in statistics:
        title += "Mean "
        series_name.append("rolling mean")
        cols_to_plot.append(ts[col].rolling(lags).mean())

    if "std" in statistics:
        title += "Standard Deviation "
        series_name.append("rolling stdev")
        cols_to_plot.append(ts[col].rolling(lags).std())

    title += f"(Window Size: {lags})"

    rolling = px.line(
        ts,
        x=ts.index,
        y=[col for col in cols_to_plot],
        labels={"count": "Rentals ", "giorno_partenza": "Date ", "value": ""},
        color_discrete_sequence=px.colors.qualitative.T10,
        title=title
    ).update_layout(legend=legend_args)\
        .update_traces(hovertemplate=None)

    for idx, name in enumerate(series_name):
        rolling.data[idx].name = name

    return ps.plotly_style(rolling)


def plt_rolling_statistics(
        ts: pd.Series,
        lags: int,
        statistics: List[str] = ["mean"]) -> None:
    """Plots the rolling statistics of a time series using Matplotlib"""

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
    median_color: str = "tomato"
) -> Dict[str, Dict[str, Union[int, float]]]:
    # colors: https://matplotlib.org/stable/gallery/color/named_colors.html
    return {
        "boxprops": {"lw": line_width},
        "medianprops": {"lw": median_linewidth},
        "whiskerprops": {"lw": whiskers_linewidth},
        "capprops": {"lw": line_width}
    }


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
    ts_ = pd.DataFrame(ts)

    # obtain the time format from the input subunit
    # e.g. "%B" and "month"
    time_format = get_time_format(time_subunit)

    # create the new subunit column for pivoting
    ts_[time_subunit] = ts_.index.strftime(time_format)

    # create a sorting key to reorder columns after pivoting
    sorting_key = list(ts_[time_subunit].unique())

    # pivot time series and reorder columns
    df = ts_.pivot(columns=time_subunit, values=y).reindex(
        columns=sorting_key)

    return ps.plotly_style(
        df.plot(
            kind="box",
            title=f"Bike Rentals {time_subunit.capitalize()} Boxplot",
            color_discrete_sequence=px.colors.qualitative.Vivid
        ))
