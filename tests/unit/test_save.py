from unittest.mock import patch

import pandas as pd

from datatechnicalse.storage import Storage


def test_storage_save() -> None:
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    storage = Storage("/tmp/test.csv")

    with patch("datatechnicalse.storage.fsspec.open") as mock_open:
        storage.save(df)
        mock_open.assert_called_once_with("/tmp/test.csv", "w")
