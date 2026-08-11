import pandas as pd
import pytest
from IPython.display import HTML

from summarytools import ctable


def test_ctable_builds_row_proportions_and_totals_from_series():
    x = pd.Series(["a", "a", "b", "b"], name="x")
    y = pd.Series(["yes", "no", "yes", "yes"], name="y")

    result = ctable(x, y, chisq=False)

    assert result.data.index.tolist() == ["a", "b", "Total"]
    assert result.data.columns.tolist() == ["no", "yes", "Total"]
    assert result.data.loc["a"].tolist() == [
        "1 (50.00%)",
        "1 (50.00%)",
        "2 (100.00%)",
    ]
    assert result.data.loc["b"].tolist() == [
        "0 (0.00%)",
        "2 (100.00%)",
        "2 (100.00%)",
    ]
    assert "x * y" in result.caption


def test_ctable_accepts_dataframe_column_names():
    frame = pd.DataFrame({"group": ["a", "a", "b"], "answer": ["yes", "no", "yes"]})

    result = ctable("group", "answer", data=frame, prop="none", chisq=False)

    assert result.data.loc["a", "no"] == "1"
    assert result.data.loc["a", "yes"] == "1"
    assert result.data.loc["b", "yes"] == "1"
    assert result.data.loc["Total", "Total"] == "3"


@pytest.mark.parametrize(
    ("prop", "cell", "expected"),
    [
        ("col", ("a", "yes"), "1 (33.33%)"),
        ("tot", ("a", "yes"), "1 (25.00%)"),
        ("none", ("a", "yes"), "1"),
    ],
)
def test_ctable_supports_proportion_modes(prop, cell, expected):
    x = pd.Series(["a", "a", "b", "b"], name="x")
    y = pd.Series(["yes", "no", "yes", "yes"], name="y")

    result = ctable(x, y, prop=prop, chisq=False)

    assert result.data.loc[cell] == expected


def test_ctable_can_hide_missing_values_and_totals():
    x = pd.Series(["a", None, "b"], name="x")
    y = pd.Series(["yes", "yes", None], name="y")

    result = ctable(x, y, report_nans=False, totals=False, chisq=False)

    assert result.data.index.tolist() == ["a"]
    assert result.data.columns.tolist() == ["yes"]
    assert result.data.loc["a", "yes"] == "1 (100.00%)"


def test_ctable_reports_missing_values_last():
    x = pd.Series([None, "a"], name="x")
    y = pd.Series(["yes", None], name="y")

    result = ctable(x, y, report_nans=True, totals=False, chisq=False)

    assert result.data.index.tolist() == ["a", "NaN"]
    assert result.data.columns.tolist() == ["yes", "NaN"]


def test_ctable_validates_inputs_and_prop():
    series = pd.Series(["a"], name="x")

    with pytest.raises(TypeError, match="data.*specified"):
        ctable("x", "y")

    with pytest.raises(TypeError, match="must both be"):
        ctable(series, "y")

    with pytest.raises(ValueError, match="prop.*row.*col.*tot.*none"):
        ctable(series, pd.Series(["b"], name="y"), prop="invalid", chisq=False)


def test_ctable_can_return_collapsible_html():
    result = ctable(
        pd.Series(["a"], name="x"),
        pd.Series(["b"], name="y"),
        chisq=False,
        is_collapsible=True,
    )

    assert isinstance(result, HTML)
    assert "Cross-Tabulation Table" in result.data
    assert "st-collapsible" in result.data


def test_ctable_preserves_categories_named_total():
    x = pd.Series(["Total", "a"], name="x")
    y = pd.Series(["yes", "yes"], name="y")

    result = ctable(x, y, prop="none", chisq=False)

    assert result.data.loc["Total", "yes"] == "1"
    assert result.data.loc["Total (all)", "Total (all)"] == "2"


def test_ctable_does_not_multiply_rows_with_duplicate_indexes():
    x = pd.Series(["a", "b"], index=[0, 0], name="x")
    y = pd.Series(["yes", "no"], index=[0, 0], name="y")

    result = ctable(x, y, prop="none", chisq=False)

    assert result.data.loc["Total", "Total"] == "2"


def test_ctable_accepts_equally_named_series():
    x = pd.Series(["a", "b"], name="value")
    y = pd.Series(["yes", "no"], name="value")

    result = ctable(x, y, prop="none", chisq=False)

    assert result.data.loc["Total", "Total"] == "2"
