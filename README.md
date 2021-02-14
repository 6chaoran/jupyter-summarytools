# DataFrame Summary Tools in Jupyter Notebook

This is python version of `summarytools`, which is used to generate standardized and comprehensive summary of dataframe.

The idea is originated from the `summarytools` R package (https://github.com/dcomtois/summarytools).

* Only `dfSummary` is made available for now
* Added two html widgets (collapsible / tabbed page)

# Installation
1. clone / download this repository
2. copy the `summarytools` folder to your project root directory.

# Quick Start

the quick-start notebook is available in [here](quick-start.ipynb)

out-of-box `dfSummary` function will generate a HTML based data frame summary.

```
import pandas as pd
from summarytools import dfSummary
titanic = pd.read_csv('./data/titanic.csv')
dfSummary(titanic)
```
![](images/dfSummary.png)

## collapsible summary

```
import pandas as pd
from summarytools import dfSummary
titanic = pd.read_csv('./data/titanic.csv')
dfSummary(titanic, is_collapsible = True)
```

![](images/collapsible.gif)

## tabbed summary

```
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
Using the following command to retain the data frame summary as HTML.
```
jupyter nbconvert --to html_embed path/of/your/notebook.ipynb
```
