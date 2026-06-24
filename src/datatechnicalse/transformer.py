import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    A class to transform a dataframe
    used to create 2 new columns, a_count and contains_a
    """

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Receives a panda dataframe, create 2 new columns and returns
        the new dataframe.

        Args:
            df: The panda DataFrame that will be modifyed.

        Returns:
            The modified DataFrame with the new columns.

        """
        df["a_count"] = (
            df["FinInstrmGnlAttrbts.FullNm"].str.count("a").fillna(0)
        )
        df["contains_a"] = df["a_count"].apply(
            lambda x: "YES" if x > 0 else "NO"
        )
        return df
