from pathlib import Path
from matplotlib import pyplot as plt
from pandas.api.types import is_datetime64_any_dtype as _is_datetime
import numpy as np
import pandas as pd
from IPython.display import HTML, display
import inspect
from .htmlwidgets import collapsible, tabset

def _is_numerical(x:pd.Series):
    return (x.dtype == int) or (x.dtype == float)

def _is_categorical(x: pd.Series, num_unique, max_level):
    try:
        if x.dtype == 'category':
            return True
    except:
        pass
    if x.dtype == 'object':
        return True
    if x.dtype in ['int', 'float']:
        if num_unique <= max_level:
            return True
    return False

def _is_bool(x: pd.Series):
    return x.dtype == bool

def _graph_cat_col(stats, filename, figsize):
    fig = plt.figure(figsize=figsize)
    pct = stats / stats.sum()
    plt.barh(pct.index, pct, color='gray', alpha=0.3, edgecolor='black')
    plt.gca().invert_yaxis()
    plt.xlim(0, 1)
    plt.axis('off')
    fig.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()
    return f'<img src = "{filename}"></img>'


def _graph_num_col(x, filename, figsize):
    fig = plt.figure(figsize=figsize)
    x = x[~x.isna()]
    _ = plt.hist(x, bins=10, color='gray', edgecolor='black', alpha=0.3)
    plt.axis('off')
    plt.tight_layout()
    fig.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()
    return f'<img src = "{filename}"></img>'


def _graph_date_col(x: pd.Series, filename, figsize):
    freqs = (x - x.min()).map(lambda x: x.days)
    fig = plt.figure(figsize=figsize)
    plt.hist(freqs, bins=10, color='gray', alpha=0.3, ec='black')
    plt.axis('off')
    fig.savefig(filename, bbox_inches='tight', pad_inches=0)
    plt.close()
    return f'<img src = "{filename}"></img>'


def _stats_date_col(x: pd.Series, show_graph: bool, filename: str):

    stats = f"Min: {x.min().strftime('%Y-%m-%d')}<br>"
    stats += f"Max: {x.max().strftime('%Y-%m-%d')}<br>"
    stats += f"Duration: {(x.max() - x.min()).days:,} days"

    freqs = f"{x.nunique()} distinct values"

    out = {
        'Stats / Values': stats,
        'Freqs / (% of Valid)': freqs}

    if show_graph:
        graph = _graph_date_col(x, filename, figsize=(2, 1))
        out['Graph'] = graph

    return out


def _stats_cat_col(x: pd.Series, max_level: int, show_graph: bool, filename: str, max_str_len=30):

    stats = x.astype(str).value_counts()
    values = [f'{i+1}. {v[:max_str_len]}' for i, v in enumerate(stats.index)]
    total = stats.values.sum()
    freqs = stats.map(lambda i: f"{i:,} ({i/total:.1%})")

    if len(stats) > max_level:
        values = [f'{i+1}. {v[:max_str_len]}' for i,
                  v in enumerate(stats.index[:max_level])]
        values += [f'{max_level + 1}. other']
        freqs = stats[:max_level].map(
            lambda i: f"{i:,} ({i/total:.1%})").to_list()
        freqs += [f"{stats[max_level:].sum():,} ({stats[max_level:].sum()/total:.1%})"]
        stats = pd.concat([stats.head(max_level), 
            pd.Series({'other': stats[max_level:].sum()})])

    out = {
        'Stats / Values': '<br>'.join(values),
        'Freqs / (% of Valid)': '<br>'.join(freqs)}

    if show_graph:
        graph = _graph_cat_col(stats, filename, figsize=(2, 0.3 * len(stats)))
        out['Graph'] = graph

    return out


def _stats_num_col(x: pd.Series, show_graph: bool, filename: str):

    stats = f"Mean (sd) : {x.mean():.1f} ({x.std():.1f})"
    stats += f"<br>min < med < max:"
    stats += f"<br>{x.min():.1f} < {x.median():.1f} < {x.max():.1f}"
    stats += f"<br>IQR (CV) : {x.quantile(0.75) - x.quantile(0.25):.1f} ({x.mean()/x.std():.1f})"

    values = f"{x.nunique():,} distinct values"

    out = {
        'Stats / Values': stats,
        'Freqs / (% of Valid)': values}

    if show_graph:
        graph = _graph_num_col(x, filename, figsize=(2, 1))
        out['Graph'] = graph

    return out


def _var_name(var):
    lcls = inspect.stack()[2][0].f_locals
    for name in lcls:
        if id(var) == id(lcls[name]):
            return name
    return ""
    

def dfSummary(data: pd.DataFrame, max_level: int = 10,
              show_graph: bool = True, tmp_dir: str = './tmp',
              is_collapsible=False):
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
    stats = []
    for i, v in enumerate(data.columns):
        filename = tmp_dir.joinpath(f'{tbl_name}_{i:03d}.png')
        if _is_categorical(data[v], num_uniques[v], max_level):
            stats += [_stats_cat_col(data[v], max_level, show_graph, filename)]
        elif _is_datetime(data[v]):
            stats += [_stats_date_col(data[v], show_graph, filename)]
        elif _is_bool(data[v]):
            stats += [_stats_cat_col(data[v], max_level, show_graph, filename)]
        elif _is_numerical(data[v]):
            stats += [_stats_num_col(data[v], show_graph, filename)]
        else:
            pass
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
