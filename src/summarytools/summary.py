import pandas as pd
from .summarytools import _var_name, _get_stats
from pathlib import Path
import numpy as np
from IPython.display import HTML
from .htmlwidgets import collapsible


from .summarytools import _summarize_col
import multiprocessing as mp

def get_stats(df, num_proc: int, max_level: int = 10, tbl_name: str = 'df', show_graph: bool = True, tmp_dir: str ='./tmp'):
    tmp_dir = Path(tmp_dir)
    data = [(df[col], max_level, tbl_name, i, show_graph, tmp_dir) for i, col in enumerate(df.columns)]

    with mp.Pool(num_proc) as pool:
        results = pool.starmap(_summarize_col, data)

    return results


def dfSummary(data: pd.DataFrame, max_level: int = 10,
              show_graph: bool = True, tmp_dir: str = './tmp',
              is_collapsible=False, num_proc = 1):
    """generate HTML data summary

    Args:
        data (pd.DataFrame): [input dataframe]
        max_level (int, optional): [max level of categorical variable to be shown]. Defaults to 10.
        show_graph (bool, optional): [flag to show Graph column]. Defaults to True.
        tmp_dir (str, optional): [directory for temporary images]. Defaults to './tmp'.
        is_collapsible (bool, optional): [flag for collapsible page]. Defaults to False.

    Returns:
        [Pandas.Styler]: if is_collapsible = False
        [HTML]: if is_collapisbile = True

    Examples:
    ```
    from summarytools import dfSummary
    import pandas as pd
    data = pd.read_csv('./your-data-path.csv')
    # default summary view
    dfSummary(data)
    # collapsible summary
    dfSummary(data, is_collapsible = True)
    # tabbed summary
    from summarytools import tabset
    tab1 = dfSummary(data).to_html()
    tabset({'tab1', tab1})
    ```
    """

    tbl_name = _var_name(data)
    tbl_dups = f"Duplicates: {data.duplicated().sum():,}"
    tbl_dims = "Dimensions: {:,} x {:,}".format(*data.shape)
    tbl_caption = "<strong>Data Frame Summary</strong><br>"
    tbl_caption += tbl_name + "<br>" + tbl_dims + "<br>" + tbl_dups

    nrows, ncols = data.shape
    num_uniques = data.apply(pd.Series.nunique)

    variable = data.columns.values.astype(str)
    variable = [f'<strong>{i}</strong>' for i in variable]
    no = np.arange(1, ncols + 1)
    dtype = [f'<br>[{i}]' for i in data.dtypes.astype(str)]
    variable = np.char.array(variable) + np.char.array(dtype)
    out = pd.DataFrame({'No': no, 'Variable': variable})

    tmp_dir = Path(tmp_dir)
    if show_graph:
        tmp_dir.mkdir(exist_ok=True, parents=True)

    # Stats / Freqs / Graphs
    if num_proc > 1:
        stats = get_stats(data, num_proc, max_level, tbl_name, show_graph, tmp_dir)
    else:
        stats = _get_stats(data, max_level, tbl_name, show_graph, tmp_dir)
    stats = pd.DataFrame(stats)
    out = pd.concat([out, stats], axis=1)

    # Missing
    missing = np.char.array([f'{i:,}' for i in data.isna().sum()])
    missing_pct = np.char.array([f'<br>({i:.1%})' for i in data.isna().mean()])
    out['Missing'] = missing + missing_pct

    # styles
    out = (out.style
           .set_properties(**{'text-align': 'left',
                'font-size':'12px',
                'vertical-align':'middle'})
           .set_table_styles([{'selector':'thead>tr>th', 'props': 'text-align : left'}])
           .set_properties(subset=['No'], **{'width':'5%', 
                'max-width':'50px', 
                'min-width':'20px'})
           .set_properties(subset=['Variable'], **{'width':'15%',
                'max-width':'200px',
                'min-width':'100px',
                'word-break':'break-word'})
           .set_properties(subset=['Stats / Values'], **{'width':'30%', 
                'min-width':'100px'})
           .set_properties(subset=['Freqs / (% of Valid)'], **{'width':'25%',
                'min-width':'100px'})\
           .set_properties(subset=['Missing'], width='10%') \
           .hide(axis='index')\
           .set_caption(tbl_caption))
    if show_graph:
        out = out.set_properties(subset=['Graph'], **{'width':'20%', 'min-width':'150px'})

    if is_collapsible:
        out = out.to_html()
        out = collapsible(out, tbl_name)
        return HTML(out)

    return out