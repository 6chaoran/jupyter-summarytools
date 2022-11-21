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
      border-bottom: 1px solid #ccc;
      display: flex;
      flex-wrap: wrap;
    }

    /* Style the buttons inside the tab */
    .tab>button {
      background-color: inherit;
      border: none;
      outline: none;
      cursor: pointer;
      padding: 1rem;
      transition: 0.1s;
      font-size: 15px;
      border-top-left-radius: 0.25rem;
      border-top-right-radius: 0.25rem;
      color: #0d6efd;
    }

    /* Change background color of buttons on hover */
    .tab>button:hover {
      background-color: #ccc;
    }

    /* Create an active/current tablink class */
    .tab>button.active-tab {
      background-color: white;
      border: 1px solid #ccc;
      border-bottom: none;
      margin-bottom: -1px;
      color: #495057;

    }"""

    style += f"""
    /* Style the tab content */
    .{tabcontent} {{
      display: none;
      padding: 0 0.5rem;
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



def collapsible(html:str, name:str = "", 
                closed_text:str = "Show Summary", 
                open_text:str = "Hide Summary"):
    """[summary]
    Args:
        html (str): HTML content to put in collapsible container
        name (str): name to be shown in collapsible header
        closed_text (str):
        open_text (str):
    Returns:
        str: HTML
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

    html = f"""<button type="button" class = "st-collapsible", 
    id = "btn-{id}" onclick = "coll_toggle_{id}()">{closed_text}{name}</button>
    <div class="st-content" id="cont-{id}">
      {html}
    </div>
    """
    css = f"""<style>
    #btn-{id}.st-collapsible {{
      background-color: white;
      color: #444;
      cursor: pointer;
      padding: 1.5rem 2rem;
      width: 100%;
      text-align: left;
      outline: none;
      font-size: 14px;
      border-top-left-radius: 0.375rem;
      border-top-right-radius: 0.375rem;
      border: 1px solid #dee2e6;
      border-bottom: none;
      font-weight: 500;
    }}

    #btn-{id}.active {{
      background-color: #e7f1ff;
      color: #0c63e4;
    }}

    #cont-{id}.st-content {{
      padding: 0 10px;
      background-color: white;
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.2s ease-out;
      border: 1px solid #dee2e6;
      border-top: none;
    }}

    #cont-{id}.st-content .active {{
      border: 1px solid #dee2e6;
      border-bottom-left-radius: 0.375rem;
      border-bottom-right-radius: 0.375rem;
    }}

    #btn-{id}.st-collapsible:after {{
      content: '';
      background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23212529'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
      color: #444;
      font-weight: bold;
      float: right;
      margin-left: 5px;
      height: 1.5em;
      width:  1.5rem;
      background-repeat: no-repeat;
      transition: transform 0.2s ease-in-out;
    }}

    #btn-{id}.active:after {{
      content: '';
      background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%230c63e4'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
      transform: rotate(180deg);
    }}
    </style>"""

    js = f"""<script>
    function coll_toggle_{id}(){{
        var coll = document.getElementById("btn-{id}");
        var content = document.getElementById("cont-{id}");
        coll.classList.toggle("active");
        if (content.style.maxHeight){{
          content.style.maxHeight = null;
          coll.innerHTML = "{closed_text}{name}";
        }} else {{
          content.style.maxHeight = content.scrollHeight + "px";
          coll.innerHTML = "{open_text}{name}";
        }}
    }}  

    </script>"""

    return (html + css + js)