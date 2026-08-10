import pandas as pd
from .summarytools import _var_name, _fmt_freq, _fmt_pct
import numpy as np
from IPython.display import HTML
from .htmlwidgets import collapsible

try:
    from scipy.stats import chi2
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False

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
    from summarytools import ctable
    import pandas as pd
    data = pd.read_csv('./your-data-path.csv')
    # default ctable view
    ctable(x=data['x'], y=data['y'])
    ctable(x='x', y='y', data=data)
    # collapsible cross-tabulation
    ctable(x='x', y='y', data=data, is_collapsible=True)
    # tabbed tables
    from summarytools import tabset
    tab1 = freq(data1['x1'], data1['y1']).to_html()
    tab2 = freq(data2['x2'], data2['y2']).to_html()
    tabset({'tab1': tab1, 'tab2': tab2})
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
        raise ValueError("`x`,`y` must both be pd.Series or str")
    
    if report_nans:
        df[x_name] = df[x_name].where(df[x_name].notna(), 'NaN').astype(str)
        df[y_name] = df[y_name].where(df[y_name].notna(), 'NaN').astype(str)

    # build table
    tbl = df.groupby([x_name, y_name]).size().unstack()
        
    if '<NA>' in tbl.index:
        order = [i for i in tbl.index if i != '<NA>'] + ['<NA>']
        tbl = tbl.reindex(index=order)
    if '<NA>' in tbl.columns:
        order = [c for c in tbl.columns if c != '<NA>'] + ['<NA>']
        tbl = tbl.reindex(columns=order)

    n_rows = tbl.shape[0]
    n_cols = tbl.shape[1]
    total_all = tbl.values.sum()
    total_rows = tbl.sum(axis=0)
    total_cols = tbl.sum(axis=1)

    if chisq:  # chi-squared test
        if _HAS_SCIPY:
            chisq_ddof = (n_rows-1)*(n_cols-1)
            expected = np.outer(total_cols, total_rows) / total_all
            chisq_test = ((tbl - expected)**2 / expected).values.sum()
            chisq_pvalue = 1 - chi2.cdf(chisq_test, chisq_ddof)
            
    if totals:
        tbl['Total'] = tbl.sum(axis=1)
        tbl.loc['Total'] = tbl.sum(axis=0)

    # proportions
    counts_arr = tbl.values.astype(float)
    if prop == 'row':
        denom = counts_arr[:, [-1]] if totals else counts_arr.sum(axis=1, keepdims=True)
        pct_arr = np.divide(counts_arr, denom, out=np.zeros_like(counts_arr), where=denom != 0) * 100
    elif prop == 'col':
        denom = counts_arr[[-1], :] if totals else counts_arr.sum(axis=0, keepdims=True)
        pct_arr = np.divide(counts_arr, denom, out=np.zeros_like(counts_arr), where=denom != 0) * 100
    elif prop == 'tot':
        pct_arr = counts_arr / total_all * 100 if total_all > 0 else np.zeros_like(counts_arr)
    elif prop == 'none':
        pct_arr = None
    else:
        raise ValueError("`prop` must be one of 'row', 'col', 'tot', 'none'")
    
    # styles
    out = pd.DataFrame(index=tbl.index, columns=tbl.columns, dtype=object)
    for i in range(counts_arr.shape[0]):
        for j in range(counts_arr.shape[1]):
            n_val = counts_arr[i, j]
            p_val = pct_arr[i,j] if pct_arr is not None else None
            out.iat[i,j] = _fmt_freq(n_val) if p_val is None else f'{_fmt_freq(n_val)} ({_fmt_pct(p_val, digits=digits)})'

    tbl_caption = f"<strong>Cross-Tabulation Table</strong><br>{tbl_name}"
    if chisq:
        if not _HAS_SCIPY:
            tbl_caption += f"<br>(scipy not installed - chi-square test skipped)"
        else:
            tbl_caption += f"<br>Chi-squared: {chisq_test:.4f} &nbsp; ddof={chisq_ddof:.0f} &nbsp; p-value={chisq_pvalue:,.4f}"
    
    out = (out.style
           .set_properties(**{'text-align':'right',
                              'font-size':'12px',
                              'vertical-align':'middle'})
           .set_table_styles([{'selector':'thead>tr>th',
                               'props':'text-align: left'},
                              {'selector':'table',
                               'props':'min_width : 800px'},
                              {'selector':'caption',
                               'props':'white-space : nowrap'}])
           .set_caption(tbl_caption))

    if is_collapsible:
        out = out.to_html()
        out = collapsible(out, tbl_name)
        return HTML(out)
    
    return out