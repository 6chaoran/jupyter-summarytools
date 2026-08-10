import pandas as pd
from .summarytools import _var_name, _fmt_freq, _fmt_pct
import numpy as np
from IPython.display import HTML
from .htmlwidgets import collapsible

def ctable(x: pd.Series | str, y: pd.Series | str, data: pd.DataFrame=None,
         prop: str="row", digits: int=2,
         report_nans: bool=True, chisq: bool=True, totals: bool=True,
         is_collapsible=False):
    """generate cross-tabulations (joint frequencies) for pairs of categorical variables

    Args:
        x (pd.Series or str): [first categorical variable, values will appear as row names]
        y (pd.Series or str): [second categorical variable, values will appear as column names]
        data (pd.DataFrame, optional): [input dataframe]. Defaults to None if `x`,`y` are pd.Series.
        prop (str, optional): [proportions to show ('row', 'col', 'tot', 'none')]. Defaults to 'row'.
        digits (int, optional): [number of rounding digits]. Defaults to 2.
        report_nans (bool, optional): [flag to show missing values]. Defaults to True.
        chisq (bool, optional): [flag to display chi-square statistic along with p-value]. Defaults to True.
        totals (bool, optional): [flag to show totals]. Defaults to True.
        is_collapsible (bool, optional): [flag for collapsible page]. Defaults to False.
    
    Returns:
        [Pandas.Styler]: if is_collapsible = False
        [HTML]: if is_collapsible = True
    
    Examples:
    ```
    TODO
    ```
    """
    # resolve pd.Series vs str
    if isinstance(x, pd.Series) and isinstance(y, pd.Series):
        df = pd.merge(x.copy(), y.copy(), left_index=True, right_index=True).astype(str)
        x_name, y_name = str(x.name), str(y.name)
        tbl_name = x_name + ' * ' + y_name
    elif isinstance(x, str) and isinstance(y, str):
        if data is None:
            raise ValueError("`data` must be specified when `x`,`y` are str")
        df = data[[x, y]].astype(str).copy()
        x_name, y_name = x, y
        tbl_name = _var_name(data) + ": " + x_name + ' * ' + y_name
    else:
        raise ValueError("`x`,`y` must be a pd.Series or str")

    # build table
    out = pd.DataFrame()
    
    # styles
    tbl_name = ''
    tbl_caption = ''

    out = (out.style
           .set_caption(tbl_caption))

    if is_collapsible:
        out = out.to_html()
        out = collapsible(out, tbl_name)
        return HTML(out)
    
    return out