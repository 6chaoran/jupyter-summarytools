import pandas as pd
from .summarytools import _var_name, _get_stats
from pathlib import Path
import numpy as np
from IPython.display import HTML
from .htmlwidgets import collapsible

def freq(data: pd.DataFrame, var: str = None,
         max_level: int=10, digits: int=2, order: str='levels',
         report_nans: bool=True, cumul: bool=True, totals: bool=True,
         tmp_dir: str='./tmp', is_collapsible=False):
    """generate HTML data frequency table

    Args:
        data (pd.DataFrame): [input dataframe]
        var (str, optional): [column name when `data` is a DataFrame; ignored when `data` is a Series]
        max_level (int, optional): [max level of categorical variable to be shown]. Defaults to 10.
        digits (int, optional): [number of rounding digits]. Defaults to 2.
        order (str, optional): [sort rows by values ('levels') or frequency ('freq')]. Defaults to 'levels'.
        report_nans (bool, optional): [flag to show missing values]. Defaults to True.
        cumul (bool, optional): [flag to show cumulative proportions]. Defaults to True.
        totals (bool, optional): [flag to show totals]. Defaults to True.
        tmp_dir (str, optional): [directory for temporary images]. Defaults to './tmp'.
        is_collapsible (bool, optional): [flag for collapsible page]. Defaults to False.
    
    Returns:
        [Pandas.Styler]: if is_collapsible = False
        [HTML]: if is_collapisbile = True
    """
    pass