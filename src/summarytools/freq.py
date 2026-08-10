import pandas as pd
from .summarytools import _var_name, _fmt_freq, _fmt_pct
import numpy as np
from IPython.display import HTML
from .htmlwidgets import collapsible

def freq(data: pd.DataFrame, var: str = None,
         max_level: int=10, digits: int=2, order: str='levels',
         report_nans: bool=True, cumul: bool=True, totals: bool=True,
         is_collapsible=False):
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
        is_collapsible (bool, optional): [flag for collapsible page]. Defaults to False.
    
    Returns:
        [Pandas.Styler]: if is_collapsible = False
        [HTML]: if is_collapsible = True

    Examples:
    ```
    from summarytools import freq
    import pandas as pd
    data = pd.read_csv('./your-data-path.csv')
    # default freq view
    freq(data, var='var_name')
    freq(data['var_name'])
    # collapsible frequency table
    freq(data, var='var_name', is_collapsible = True)
    # tabbed frequency table
    from summarytools import tabset
    tab1 = freq(data['var1']).to_html()
    tab2 = freq(data['var2']).to_html()
    tabset({'tab1': tab1, 'tab2': tab2})
    ```
    """
    # resolve pd.DataFrame vs pd.Series
    if isinstance(data, pd.DataFrame):
        if var is None:
            raise ValueError("`var` must be specified when `data` is a pd.DataFrame")
        s = data[var].copy()
        var_name = str(s.name)
        tbl_name = _var_name(data) + ": " + var_name
    elif isinstance(data, pd.Series):
        s = data.copy()
        var_name = str(s.name)
        tbl_name = var_name
    else:
        raise ValueError("`data` must be a pd.Series or pd.DataFrame")
    
    # weights for frequency
    w = pd.Series(np.ones(len(s)), index=s.index)

    n_total = w.sum()
    is_na = s.isna()
    n_missing = w[is_na].sum()
    n_valid = n_total - n_missing

    valid_s = s[~is_na]
    valid_w = w[~is_na]
    grouped = valid_w.groupby(valid_s).sum()

    # max level of categorical variable to be shown
    other_sum = None
    if max_level is not None and len(grouped) > max_level:
        grouped_sorted = grouped.sort_values(ascending=False)
        grouped = grouped_sorted.iloc[:max_level]
        other_sum = grouped_sorted.iloc[max_level:].sum()

    # ordering of the table
    if order == 'freq':
        grouped = grouped.sort_values(ascending=False)
    else:  # 'levels'
        try:
            grouped = grouped.sort_index()
        except TypeError:
            # if cannot sort index, fall back to frequency order
            grouped = grouped.sort_values(ascending=False)

    if other_sum is not None and other_sum > 0:
        grouped = pd.concat([grouped, pd.Series({'(other)': other_sum})])
        grouped.loc['(other)'] = other_sum


    # build table
    freq_col = grouped.values.astype(float)
    pct_valid = freq_col / n_valid * 100 if n_valid > 0 else np.zeros_like(freq_col)
    pct_valid_cum = np.cumsum(pct_valid)
    pct_total = freq_col / n_total * 100 if n_total > 0 else np.zeros_like(freq_col)
    pct_total_cum = np.cumsum(pct_total)

    out = pd.DataFrame({
        var_name: grouped.index.astype(str),
        'Freq': freq_col,
        '% Valid': pct_valid,
        '% Valid Cum.': pct_valid_cum,
        '% Total': pct_total,
        '% Total Cum.': pct_total_cum,
    })

    if report_nans:
        na_row = {
            var_name: 'NaN',
            'Freq': n_missing,
            '% Valid': np.nan,
            '% Valid Cum.': np.nan,
            '% Total': (n_missing / n_total * 100) if n_total > 0 else np.nan,
            '% Total Cum.': 100.0,
        }
        out = pd.concat([out, pd.DataFrame([na_row])], ignore_index=True)

    if totals:
        total_row = {
            var_name: 'Total',
            'Freq': n_total,
            '% Valid': 100.0 if n_valid > 0 else np.nan,
            '% Valid Cum.': 100.0 if n_valid > 0 else np.nan,
            '% Total': 100.0,
            '% Total Cum.': 100.0,
        }
        out = pd.concat([out, pd.DataFrame([total_row])], ignore_index=True)

    if not report_nans and not cumul:
        out = out.drop(columns=['% Valid Cum.', '% Total', '% Total Cum.'])
        pct_cols = ['% Valid']
    elif not cumul:
        out = out.drop(columns=['% Valid Cum.', '% Total Cum.'])
        pct_cols = ['% Valid', '% Total']
    elif not report_nans:
        out = out.drop(columns=['% Total', '% Total Cum.'])
        pct_cols = ['% Valid', '% Valid Cum.']
    else:
        pct_cols = ['% Valid', '% Valid Cum.', '% Total', '% Total Cum.']


    # styles
    tbl_caption = f"<strong>Frequency Table</strong><br>{var_name}"
    tbl_caption += f"<br>Valid: {n_valid:,.0f} &nbsp; Missing: {n_missing:,.0f} &nbsp; Total: {n_total:,.0f}"

    out = (out.style
           .format({'Freq': _fmt_freq, **{c: _fmt_pct for c in pct_cols}})
           .set_properties(**{'text-align':'left',
                              'font-size':'12px',
                              'vertical-align':'middle'})
           .set_table_styles([{'selector':'thead>tr>th',
                               'props':'text-align: left'}])
           .set_properties(subset=[var_name], **{'width':'25%',
                                                 'min-width':'100px',
                                                 'word-break':'break-word'})
           .set_properties(subset=['Freq'], **{'width':'10%',
                                               'min-width':'60px'})
           .set_properties(subset=pct_cols, **{'width':'16%',
                                               'min-width':'80px'})
           .hide(axis='index')
           .set_caption(tbl_caption))

    if is_collapsible:
            out = out.to_html()
            out = collapsible(out, tbl_name)
            return HTML(out)
    
    return out