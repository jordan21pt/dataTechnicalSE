import pandas as pd

from datatechnicalse.transformer import DataTransformer


def test_a_count() -> None:
    df = pd.DataFrame(
        {"FinInstrmGnlAttrbts.FullNm": ["banana", "apple", "xyz", None]}
    )
    transformer = DataTransformer()
    result = transformer.transform(df)
    assert result["a_count"].tolist() == [3, 1, 0, 0]


def test_contains_a() -> None:
    df = pd.DataFrame(
        {
            "FinInstrmGnlAttrbts.FullNm": ["banana", "apple", "xyz", None],
        }
    )
    transformer = DataTransformer()
    result = transformer.transform(df)
    assert result["contains_a"].tolist() == ["YES", "YES", "NO", "NO"]
