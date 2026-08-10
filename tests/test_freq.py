import pandas as pd
import pytest
from IPython.display import HTML

from summarytools import freq


def test_freq_counts_missing_values_and_totals():
    series = pd.Series(["b", "a", "b", None], name="category")

    result = freq(series).data

    assert result["category"].tolist() == ["a", "b", "NaN", "Total"]
    assert result["Freq"].tolist() == [1.0, 2.0, 1.0, 4.0]
    assert result["% Valid"].iloc[:2].tolist() == pytest.approx([100 / 3, 200 / 3])
    assert result["% Total"].iloc[:2].tolist() == pytest.approx([25.0, 50.0])


def test_freq_limits_levels_and_orders_by_frequency():
    series = pd.Series(["a", "b", "b", "c", "c", "c"], name="category")

    result = freq(series, max_level=2, order="freq", report_nans=False, totals=False).data

    assert result["category"].tolist() == ["c", "b", "(other)"]
    assert result["Freq"].tolist() == [3.0, 2.0, 1.0]
    assert "% Total" not in result.columns


def test_freq_accepts_a_dataframe_column():
    frame = pd.DataFrame({"answer": ["yes", "no", "yes"]})

    result = freq(frame, var="answer", report_nans=False, cumul=False).data

    assert result.columns.tolist() == ["answer", "Freq", "% Valid"]
    assert result.iloc[-1].to_dict() == {"answer": "Total", "Freq": 3.0, "% Valid": 100.0}


def test_freq_validates_input():
    with pytest.raises(TypeError, match="var.*specified"):
        freq(pd.DataFrame({"answer": ["yes"]}))

    with pytest.raises(TypeError, match="Series or pd.DataFrame"):
        freq(["yes", "no"])


def test_freq_can_return_collapsible_html():
    result = freq(pd.Series([1, 1, 2], name="value"), is_collapsible=True)

    assert isinstance(result, HTML)
    assert "Frequency Table" in result.data
    assert "st-collapsible" in result.data
