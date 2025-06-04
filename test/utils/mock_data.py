import pandas as pd

def Get_data_for_peak_finder() -> pd.DataFrame:
    """
        Idea behind this df is it has a peak, then it has some years without a peak and has an elogated peak, also a big decrease.
    """
    return pd.DataFrame(
        {
            'year': [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997],
            'count': [5_000, 150_000, 60_000, 60_000, 180_000, 180_000, 190_000, 80_000]
        }
    )