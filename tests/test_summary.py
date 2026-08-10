from pathlib import Path

import pandas as pd
from IPython.display import HTML

from summarytools import _summarize_col, dfSummary


def test_summarize_numeric_column_without_graph(tmp_path):
    result = _summarize_col(
        pd.Series([1.0, 2.0, 3.0, None]),
        max_level=2,
        show_graph=False,
        tmp_dir=tmp_path,
    )

    assert "Mean (sd) : 2.0 (1.0)" in result["Stats / Values"]
    assert result["Freqs / (% of Valid)"] == "3 distinct values"
    assert "Graph" not in result


def test_summarize_categorical_column_groups_extra_levels(tmp_path):
    result = _summarize_col(
        pd.Series(["a", "a", "b", "c"]),
        max_level=2,
        show_graph=False,
        tmp_dir=tmp_path,
    )

    assert result["Stats / Values"] == "1. a<br>2. b<br>3. other"
    assert result["Freqs / (% of Valid)"] == "2 (50.0%)<br>1 (25.0%)<br>1 (25.0%)"


def test_summarize_datetime_column(tmp_path):
    result = _summarize_col(
        pd.Series(pd.to_datetime(["2024-01-01", "2024-01-03"])),
        show_graph=False,
        tmp_dir=tmp_path,
    )

    assert result["Stats / Values"] == "Min: 2024-01-01<br>Max: 2024-01-03<br>Duration: 2 days"
    assert result["Freqs / (% of Valid)"] == "2 distinct values"


def test_df_summary_builds_expected_table():
    frame = pd.DataFrame({"number": [1, 2, 3], "label": ["a", "b", None]})

    result = dfSummary(frame, max_level=1, show_graph=False)

    assert result.data.columns.tolist() == [
        "No",
        "Variable",
        "Stats / Values",
        "Freqs / (% of Valid)",
        "Missing",
    ]
    assert result.data["Missing"].tolist() == ["0<br>(0.0%)", "1<br>(33.3%)"]
    assert "Dimensions: 3 x 2" in result.caption


def test_df_summary_generates_graphs(tmp_path):
    frame = pd.DataFrame({"number": [1.0, 2.0, 3.0]})

    result = dfSummary(frame, max_level=1, show_graph=True, tmp_dir=tmp_path)

    assert "data:image/png;base64" in result.data.loc[0, "Graph"]
    assert list(Path(tmp_path).glob("*.png"))


def test_df_summary_can_return_collapsible_html():
    result = dfSummary(
        pd.DataFrame({"value": [1, 2]}),
        max_level=1,
        show_graph=False,
        is_collapsible=True,
    )

    assert isinstance(result, HTML)
    assert "Data Frame Summary" in result.data
    assert "st-collapsible" in result.data
