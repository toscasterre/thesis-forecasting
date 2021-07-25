# for connections
import psycopg2

# dataframes
import pandas as pd


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

    time_key, time_val = time_column.items()

    if station_column is None:

        query = f'''
            SELECT
                DATE_TRUNC('{trunc}', {time_key}) AS {time_val},
                COUNT(bici)
            FROM {table}
            GROUP BY {time_val};
            '''
    else:
        station_key, station_val = station_column.items()

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


