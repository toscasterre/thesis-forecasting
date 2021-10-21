from typing import Union, List
import pandas


def anti_join(x: pandas.Series, y: pandas.Series, on: Union[List[str], str]):
    """Return rows in x which are not present in y"""

    if type(on) is list:
        mismatches = pandas.merge(
            left=x, right=y, how='left',
            indicator=True, left_on=on[0], right_on=on[1])
    elif type(on) is str:
        mismatches = pandas.merge(
            left=x, right=y, how='left',
            indicator=True, on=on)
    else:
        raise Exception(
            "Please insert either a list of two\
                 or a string for the argument `on`")

    return mismatches.loc[mismatches._merge == 'left_only', :]\
        .drop(columns='_merge')


def mismatches(
    left_series: pandas.Series,
    right_series: pandas.Series,
    left_on: str,
    right_on: str,
    text: bool = True
):
    mismatched_stations = anti_join(
        right_series, left_series,
        on=[right_on, left_on])[right_on]
    mismatched_stalls = anti_join(
        left_series, right_series,
        on=[left_on, right_on])[left_on]

    if text:
        print(f"""
        {mismatched_stations.size} stations are only in the time series data.
        {mismatched_stalls.size} stalls are only in the stalls data.
        """)
        return None
    return mismatched_stations, mismatched_stalls
