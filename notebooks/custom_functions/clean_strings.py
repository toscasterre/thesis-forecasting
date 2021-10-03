import unicodedata
import pandas


def _strip_accents(string: str) -> str:
    """
    Removes accents from a string
    https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    """
    return "".join(
        letter
        for letter in unicodedata.normalize("NFD", string)
        if not unicodedata.combining(letter)
    )


def clean_series(series: pandas.Series) -> pandas.Series:
    return series\
        .str.strip()\
            .str.lower()\
            .apply(lambda x: _strip_accents(x))\
            .str.replace("""['"]""", "", regex=True)\
            .str.replace("[\s\-\.\/]+", "_", regex=True)\
            .str.replace("gimignano", "giminiano", regex=False)\
            .str.replace("donizzetti", "donizetti", regex=False)\
            .str.replace("soderini", "solderini", regex=False)\
            .str.replace("montenero", "monte_nero", regex=False)\
            .str.replace("d_eril", "deril", regex=False)\
            .str.replace("^bocconi_2", "universita_bocconi_2", regex=True)\
            .str.replace("_g_", "_grande_", regex=False)\
            .str.replace("piazza_nizza", "piazzale_nizza", regex=False)\
            .str.replace("_chiusa_provvisoriamente_", "", regex=False)\
            .str.replace("_chiusa_provv_", "", regex=False)


def clean_df(
        df: pandas.DataFrame,
        col: str,
        inplace: bool = False) -> pandas.DataFrame:

    if inplace:
        df[col] = clean_series(df[col])
    else:
        df["clean_" + col] = clean_series(df[col])

    return df
