import logging

import fsspec
import pandas as pd

logger = logging.getLogger(__name__)


class Storage:
    """
    Class to save the final csv on a cloud provider...
    """

    def __init__(self, path: str) -> None:
        """Initialize the Storage instance.

        Args:
            path: The path where the object will be stored
        """
        self._path = path

    def save(self, df: pd.DataFrame) -> None:
        """Function that saves the dataframe on the
        cloud provider.

        Args:
            df: The dataframe that will be stored
        """
        with fsspec.open(self._path, "w") as f:
            df.to_csv(f, index=False)
