from pathlib import Path
from matplotlib import pyplot as plt
from pandas.api.types import is_datetime64_any_dtype as _is_datetime
from pandas.api.types import is_numeric_dtype as _is_numerical

import numpy as np
import pandas as pd
from IPython.display import HTML, display
import inspect
from .htmlwidgets import collapsible, tabset
import base64

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

def encode_img_base64(img):
    with open(img, "rb") as image_file:
        x = image_file.read()
        encoded_string = base64.b64encode(x).decode()
    src = f"data:image/png;base64, {encoded_string}"
    return src

def _graph_cat_col(stats, filename, figsize):
    fig = plt.figure(figsize=figsize)
    pct = stats / stats.sum()
    plt.barh(pct.index, pct, color='gray', alpha=0.3, edgecolor='black')
    plt.gca().invert_yaxis()
    plt.xlim(0, 1)
    plt.axis('off')
    fig.savefig(filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    base64str = encode_img_base64(filename)
    return f'<img src = "{base64str}"></img>'


def _graph_num_col(x, filename, figsize):
    fig = plt.figure(figsize=figsize)
    x = x[~x.isna()]
    _ = plt.hist(x, bins=10, color='gray', edgecolor='black', alpha=0.3)
    plt.axis('off')
    plt.tight_layout()
    fig.savefig(filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    base64str = encode_img_base64(filename)
    return f'<img src = "{base64str}"></img>'


def _graph_date_col(x: pd.Series, filename, figsize):
    freqs = (x - x.min()).map(lambda x: x.days)
    fig = plt.figure(figsize=figsize)
    plt.hist(freqs, bins=10, color='gray', alpha=0.3, ec='black')
    plt.axis('off')
    fig.savefig(filename, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    base64str = encode_img_base64(filename)
    return f'<img src = "{base64str}"></img>'


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


def _stats_num_col(x: pd.Series, show_graph: bool, filename: str) -> dict:

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
    
def _summarize_col(series: pd.Series, max_level: int = 10, tbl_name: str = 'df', i:str=0,
              show_graph: bool = True, tmp_dir: str = './tmp') -> dict:
    filename = tmp_dir.joinpath(f'{tbl_name}_{i:03d}.png')
    num_uniq = series.nunique()
    if _is_categorical(series, num_uniq, max_level):
        return _stats_cat_col(series, max_level, show_graph, filename)
    elif _is_datetime(series):
        return _stats_date_col(series, show_graph, filename)
    elif _is_bool(series):
        return _stats_cat_col(series, max_level, show_graph, filename)
    elif _is_numerical(series):
        return _stats_num_col(series, show_graph, filename)
    else:
        return {'Stats / Values': f'not supported dtype {series.dtype}'}
    
def _summarize_col_2(x, max_level, tbl_name, show_graph, tmp_dir):
    series, i = x
    return _summarize_col(series, max_level, tbl_name, i, show_graph, tmp_dir)

def _get_stats(data: pd.DataFrame, max_level: int, tbl_name: str, show_graph: bool, tmp_dir: str):
    stats = []
    for i, v in enumerate(data.columns):
        stats += [_summarize_col(data[v], max_level, tbl_name, i, show_graph, tmp_dir)]
    return stats

