import numpy as np
from IPython.display import HTML, display

class Tags():
    def __init__(self):
        pass

    def _tags(self, tag, text, _class, **kwargs):
        if len(kwargs) > 0:
            attr = [f'{k} = "{v}"' for k, v in kwargs.items() if len(v) > 0]
            attr = ' '+' '.join(attr)
        else:
            attr = ''
        if len(_class) > 0:
            _class = f' class="{_class}"'
        return f"<{tag}{attr}{_class}>{text}</{tag}>"

    def p(self, text = '', _class = '', **kwargs):
        return self._tags('p', text, _class, **kwargs)

    def strong(self, text = '', _class = '', **kwargs):
        return self._tags('strong', text, _class, **kwargs)

    def button(self, text = '', _class = '', **kwargs):
        return self._tags('button', text, _class, **kwargs)
    
    def div(self, text = '', _class = '', **kwargs):
        text = '\n' + text + '\n'
        return self._tags('div', text, _class, **kwargs)


def fun(x):
    """[summary]

    Args:
        x ([type]): [description]
    """

def tabset(tabs: dict):
    """tabbed summary
    Args:
        tabs ([dict]): {tab-name : tab-html}
    Returns:
        rendered tabbed summary
    Examples:
    ```
    html1 = "<h1>This is Tab1</h1>"
    html2 = "<h1>This is Tab2</h1>"
    tabset({'tab1': html1, 'tab2':html2})
    ```
    """    
    id = str(int(np.random.random() * 10000))
    tags = Tags()

    openTabFunc = f"OpenTab_{id}"
    tablinks = f"tablinks-{id}"
    tabcontent = f"tabcontent-{id}"
    defaultOpen = f"defaultOpen-{id}"

    buttons = [tags.button(k,
                           _class=tablinks,
                           id=defaultOpen if i == 0 else '',
                           onclick=f"{openTabFunc}(event, '{k}-{id}')")
               for i, (k, v) in enumerate(tabs.items())]
    buttons = '\n'.join(buttons)
    html = (tags.div(buttons, _class='tab'))

    for k, v in tabs.items():
        html += tags.div(v, id=f'{k}-{id}', _class=tabcontent) + '\n'

    style = """<style>
    /* Style the tab */
    .tab {
      overflow: hidden;
      border: 1px solid #ccc;
      background-color: #f1f1f1;
    }

    /* Style the buttons inside the tab */
    .tab button {
      background-color: inherit;
      float: left;
      border: none;
      outline: none;
      cursor: pointer;
      padding: 10px;
      transition: 0.3s;
      font-size: 15px;
    }

    /* Change background color of buttons on hover */
    .tab button:hover {
      background-color: #ddd;
    }

    /* Create an active/current tablink class */
    .tab button.active-tab {
      background-color: #ccc;
    }"""

    style += f"""
    /* Style the tab content */
    .{tabcontent} {{
      display: none;
      padding: 6px 12px;
      border: 1px solid #ccc;
      border-top: none;
    }}
    </style>"""

    script = f"""
    <script>
    function {openTabFunc}(evt, cityName) {{
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName("{tabcontent}");
      for (i = 0; i < tabcontent.length; i++) {{
        tabcontent[i].style.display = "none";
      }}
      tablinks = document.getElementsByClassName("{tablinks}");
      for (i = 0; i < tablinks.length; i++) {{
        tablinks[i].className = tablinks[i].className.replace(" active-tab", "");
      }}
      document.getElementById(cityName).style.display = "block";
      evt.currentTarget.className += " active-tab";
    }}

    // Get the element with id="defaultOpen" and click on it
    document.getElementById("{defaultOpen}").click();
    </script>"""
    return display(HTML(html + style + script))



def collapsible(html:str, name:str = ""):
    """[summary]
    Args:
        html ([str]): HTML content to put in collapsible container
        name ([str]): name to be shown in collapsible header
    Returns:
        [str]: HTML
    Examples:
    ```
    from IPython.display import dispaly, HTML
    html = "<h1>This is a collapsible page</h1>"
    name = "Page1"
    html_coll = collapsible(html, name)
    display(HTML(html_coll)) # render collapsible page
    ```
    """    

    id = f"{str(int(np.random.random() * 10000))}"
    if len(name) > 0:
        name = " - " + name

    html = f"""<button type="button" class = "collapsible", 
    id = "btn-{id}" onclick = "coll_toggle_{id}()">Show Summary{name}</button>
    <div class="content" id="cont-{id}">
      {html}
    </div>
    """
    css = """<style>
    .collapsible {
      background-color: #eee;
      color: #444;
      cursor: pointer;
      padding: 10px;
      width: 100%;
      border: none;
      text-align: left;
      outline: none;
      font-size: 14px;
    }

    .active, .collapsible:hover {
      background-color: #ccc;
    }

    .content {
      padding: 0 10px;
      background-color: white;
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.2s ease-out;
    }

    .collapsible:after {
      content: '\053'; /* Unicode character for "plus" sign (+) */
      color: white;
      font-weight: bold;
      float: right;
      margin-left: 5px;
    }

    .active:after {
      content: '\055';
    }
    </style>"""

    js = f"""<script>
    function coll_toggle_{id}(){{
        var coll = document.getElementById("btn-{id}");
        var content = document.getElementById("cont-{id}");
        coll.classList.toggle("active");
        if (content.style.maxHeight){{
          content.style.maxHeight = null;
          coll.innerHTML = "Show Summary{name}";
        }} else {{
          content.style.maxHeight = content.scrollHeight + "px";
          coll.innerHTML = "Hide Summary{name}";
        }}
    }}  

    </script>"""

    return (html + css + js)