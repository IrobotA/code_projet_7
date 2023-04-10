from time import sleep
from bokeh.io import curdoc
import base64
import io
import pandas as pd
from bokeh.layouts import column
from bokeh.models import Button, Div, PreText, AutocompleteInput,FileInput

file_input = FileInput()
id = AutocompleteInput(completions = ['100000','200000','300000','400000','500000'],
                       description='ex 101099',
                       placeholder="Veuillez saisir l\'id client par exemple 101099...",
                       min_width=300) 
text =PreText()
#d = Div(text="start")
text.text='accueil'
value_input=[0]
decoded=[0]
#b = Button()

def work(attr, old, new):
    print('start_function_start')
    value_input[0] = id.value
    text.text = 'start'
    print('start_function_end')
    curdoc().add_next_tick_callback(cb)

def cb():
    print('predict_function_start')
    text.text = 'chargement_en_cours'
    print('predict_function_end')

def upload_word(attr, old, new):
    text.text='Chargement du fichier en cours...'
    sleep(2)
    decoded[0] = base64.b64decode(file_input.value)
    curdoc().add_next_tick_callback(read_csv)
    
def read_csv():
    print('lecture :',decoded[0])
    f = io.BytesIO(decoded[0])
    df_retrieved = pd.read_csv(f)  # df importé
    print(df_retrieved)
    text.text='Fin du chargement du fichier'

#b.on_click(work)
id.on_change("value",work)
print('code finished')
file_input.on_change('value', upload_word)#new

curdoc().add_root(column(file_input,
                         id,
                         text))