![GitHub](https://img.shields.io/github/license/6chaoran/jupyter-summarytools) 

![PyPI](https://img.shields.io/pypi/v/summarytools?color=blue) ![PyPI - Status](https://img.shields.io/pypi/status/summarytools?color=blue) ![PyPI - Downloads](https://img.shields.io/pypi/dm/summarytools?color=blue) ![GitHub last commit](https://img.shields.io/github/last-commit/6chaoran/jupyter-summarytools?color=blue)

# DataFrame Summary Tools in Jupyter Notebook

This is python version of `summarytools`, which is used to generate standardized and comprehensive summary of dataframe in Jupyter Notebooks.

The idea is originated from the `summarytools` R package (https://github.com/dcomtois/summarytools).

* Only `dfSummary` function is made available for now
* Added two html widgets to avoid displaying lengthy content
    + [collapsible summary](#collapsible-summary) 
    + [tabbed summary](#tabbed-summary)

# Installation

```
pip install summarytools
```

## Dependencies
1. python 3.6+
2. pandas >= 1.4.0

# Quick Start

the quick-start notebook is available in [here](https://github.com/6chaoran/jupyter-summarytools/blob/master/quick-start-colab.ipynb) or <a href="https://colab.research.google.com/github/6chaoran/jupyter-summarytools/blob/master/quick-start-colab.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

out-of-box `dfSummary` function will generate a HTML based data frame summary.

```py
import pandas as pd
from summarytools import dfSummary
titanic = pd.read_csv('./data/titanic.csv')
dfSummary(titanic)
```
![](images/dfSummary.png)

## collapsible summary

```py
import pandas as pd
from summarytools import dfSummary
titanic = pd.read_csv('./data/titanic.csv')
dfSummary(titanic, is_collapsible = True)
```

![](images/collapsible.gif)

## tabbed summary

```py
import pandas as pd
from summarytools import dfSummary, tabset
titanic = pd.read_csv('./data/titanic.csv')
vaccine = pd.read_csv('./data/country_vaccinations.csv')
vaccine['date'] = pd.to_datetime(vaccine['date'])

tabset({
    'titanic': dfSummary(titanic).render(),
    'vaccine': dfSummary(vaccine).render()})
```

![](images/tabbed.gif)

# Export notebook as HTML

when export jupyter notebook to HTML, make sure `Export Embedded HTML
` extension is installed and enabled.

![](images/embedded_html.png)

Using the following bash command to retain the data frame summary in exported HTML.
```bash
jupyter nbconvert --to html_embed path/of/your/notebook.ipynb
```

------

## Stargazers over time
[![Stargazers over time](https://starchart.cc/6chaoran/jupyter-summarytools.svg?variant=adaptive)](https://starchart.cc/6chaoran/jupyter-summarytools)
