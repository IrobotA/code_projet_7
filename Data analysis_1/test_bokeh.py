#affiche plusieurs de bouton et d'options possible etc

# noqa: E501
#from bokeh.document import Document
#from bokeh.io import curdoc
#from bokeh.embed import file_html
#from bokeh.models import (Button, CheckboxButtonGroup, CheckboxGroup, Column,
#                          CustomJS, Dropdown, RadioButtonGroup, RadioGroup, Toggle)
#from bokeh.resources import INLINE
#from bokeh.util.browser import view
#
#button = Button(label="Button (enabled) - has click event", button_type="primary")
#button.js_on_event("button_click", CustomJS(code="console.log('button: click ', this.toString())"))
#button.js_on_event("button_click", CustomJS(code="console.log('button: click ', this.toString())"))
#
#button_disabled = Button(label="Button (disabled) - no click event", button_type="primary", disabled=True)
#button_disabled.js_on_event("button_click", CustomJS(code="console.log('button(disabled): click ', this.toString())"))
#
#toggle_inactive = Toggle(label="Toggle button (initially inactive)", button_type="success")
#toggle_inactive.js_on_event('button_click', CustomJS(code="console.log('toggle(inactive): active=' + this.origin.active, this.toString())"))
#
#toggle_active = Toggle(label="Toggle button (initially active)", button_type="success", active=True)
#toggle_active.js_on_event('button_click', CustomJS(code="console.log('toggle(active): active=' + this.origin.active, this.toString())"))
#
#menu = [("Item 1", "item_1_value"), ("Item 2", "item_2_value"), None, ("Item 3", "item_3_value")]
#
#dropdown = Dropdown(label="Dropdown button", button_type="warning", menu=menu)
#dropdown.js_on_event("button_click", CustomJS(code="console.log('dropdown: click ' + this.toString())"))
#dropdown.js_on_event("menu_item_click", CustomJS(code="console.log('dropdown: ' + this.item, this.toString())"))
#
#dropdown_disabled = Dropdown(label="Dropdown button (disabled)", button_type="warning", disabled=True, menu=menu)
#dropdown_disabled.js_on_event("button_click", CustomJS(code="console.log('dropdown(disabled): click ' + this.toString())"))
#dropdown_disabled.js_on_event("menu_item_click", CustomJS(code="console.log('dropdown(disabled): ' + this.item, this.toString())"))
#
#dropdown_split = Dropdown(label="Split button", split=True, button_type="danger", menu=menu)
#dropdown_split.js_on_event("button_click", CustomJS(code="console.log('dropdown(split): click ' + this.toString())"))
#dropdown_split.js_on_event("menu_item_click", CustomJS(code="console.log('dropdown(split): ' + this.item, this.toString())"))
#
#checkbox_group = CheckboxGroup(labels=["Option 1", "Option 2", "Option 3"], active=[0, 1])
#checkbox_group.js_on_change('active', CustomJS(code="console.log('checkbox_group: active=' + this.active, this.toString())"))
#
#radio_group = RadioGroup(labels=["Option 1", "Option 2", "Option 3"], active=0)
#radio_group.js_on_change('active', CustomJS(code="console.log('radio_group: active=' + this.active, this.toString())"))
#
#checkbox_button_group = CheckboxButtonGroup(labels=["Option 1", "Option 2", "Option 3"], active=[0, 1])
#checkbox_button_group.js_on_event("button_click", CustomJS(code="console.log('checkbox_button_group: active=' + this.origin.active, this.toString())"))
#
#radio_button_group = RadioButtonGroup(labels=["Option 1", "Option 2", "Option 3"], active=0)
#radio_button_group.js_on_event("button_click", CustomJS(code="console.log('radio_button_group: active=' + this.origin.active, this.toString())"))
#
#widget_box = Column(children=[
#    button, button_disabled,
#    toggle_inactive, toggle_active,
#    dropdown, dropdown_disabled, dropdown_split,
#    checkbox_group, radio_group,
#    checkbox_button_group, radio_button_group,
#])
#
#curdoc().title = "Hello, world!"
#curdoc().add_root(widget_box)
#
#
#server.io_loop.start() #tester sans pour voir si ça fonctionne

#
#if __name__ == "__main__":
#    doc.validate()
#    filename = "buttons.html"
#    with open(filename, "w") as f:
#        f.write(file_html(doc, INLINE, "Button widgets"))
#    print("Wrote %s" % filename)
#    view(filename)

# add a button widget and configure with the call back

from bokeh.models import AutocompleteInput
import requests #api request
import json # convert from bytes to dict 
from bokeh.models import ColumnDataSource#?
from bokeh.plotting import curdoc, figure
from bokeh.models import Button, CustomJS
from bokeh.layouts import column, gridplot,row,layout
from bokeh.events import ButtonClick
from bokeh.models import PreText
import pandas as pd

#origin_path = r'C:\Users\utilisateur\Documents\MyAmaWok\OC Data Scientist\"Projet OC 7 Implementer un modele de Scoring"\datasets'
templates = pd.read_csv('../datasets/X_columns_template.csv')
id_list = pd.read_csv('../datasets/new_df_test.csv',usecols=['SK_ID_CURR'])

text = PreText(text=("test"))
completion_list = [str(id) for id in id_list["SK_ID_CURR"].tolist()]

url = "http://127.0.0.1:8000/predict/" # api url on local to get the predictions and the feature importance
           
res = requests.post(url+'100038') # predict this id, should he have a credit or not
data_retrieved = json.loads(res._content.decode('utf-8')) # convert from bytes to dictionary
source = ColumnDataSource (data = {'feature_importance':[0],
                                   'colonnes':[0]})
                                   
dict_credit = {1 :'acceptée',
               0 :'refusée'}


#def graph() :
#    source.data['feature_importance'] = data_retrieved['f'][0]
#    source.data['colonnes']= [i for i in range(len(data_retrieved['f'][0]))]
#    #text.text(text=("La demande de crédit a été  {}".format(dict_credit[data_retrieved['prediction'][0]])),width=500, height=100)

def update_id():#attrname, old, new
    res = requests.post(url+auto_complete_input.value_input)
    data_retrieved = json.loads(res._content.decode('utf-8'))
    source.data['feature_importance'] = data_retrieved['f'][0]
    source.data['colonnes']= [i for i in range(len(data_retrieved['f'][0]))]  #source.data['feature_importance']
    
    #return graph(data_retrieved)
    

button = Button(label="Prédiction", button_type="success")
button.on_click(update_id)#au lieu de graph


auto_complete_input =  AutocompleteInput(title="Veuillez écrire l\'id client:", completions = completion_list,
                                         value = completion_list[0])


auto_complete_input.on_change('value',update_id)

p = figure(
        title='Feature importance',
        x_axis_label="Variables",
        y_axis_label="Feature Importance"
    )
    
p.vbar(x= 'colonnes', top='feature_importance', width=0.5, source=source)

l = column(gridplot([[ row(button,auto_complete_input, text)]]),p)

curdoc().title = "Octroi Crédit" #Web page Title
curdoc().add_root(l) # button, Add the figure to our webpage auto_complete_input

#bokeh serve --show bokeh_app.py
# bokeh serve --show "Data analysis_1"\test_bokeh.py pour ajouter path avec espace