
from bokeh.models import AutocompleteInput
import requests #api request
import json # convert from bytes to dict 
from bokeh.models import ColumnDataSource#?
from bokeh.plotting import curdoc, figure
from bokeh.models import Button
from bokeh.layouts import column, gridplot,row,layout
from bokeh.events import ButtonClick
from bokeh.models import PreText
import pandas as pd

id_list = pd.read_csv('../datasets/new_df_test.csv',usecols=['SK_ID_CURR']) # import colonne id de test
completion_list = [str(id) for id in id_list["SK_ID_CURR"].tolist()]        #liste des identifiants des clientst

text = PreText(text=("")) #on ne met rien au départ

source = ColumnDataSource (data = {'feature_importance':[0],
                                   'colonnes':[0]}) #graph sans rien au départ

dict_credit = {1 :'payée',
               0 :'refusée'} # dico pour mapping apres avec la prédiction

url = "http://127.0.0.1:8000/predict/"  #url de l'api pour récupérer prédiction et feature importance


p = figure(
    title='Feature importance',
    x_axis_label="Variables",
    y_axis_label="Feature Importance"
) #config graph de base


p.vbar(x= 'colonnes', top='feature_importance', width=0.5, source=source)#ajout du nom des axes et la source des données

def update_id(attr, old, new):#attrname, old, new => obligatoire pour ce composant
    global res  #pour récupérer la variable pour le graph
    value_input = auto_complete_input.value # valeur dans le champs
    res = requests.post(url+value_input) #requete a fastapi
      
    
def graph(event): #event obligatoire  pour ce composant
    data_retrieved = json.loads(res._content.decode('utf-8')) #data_retrieved
    new_data = dict() # pour instancier en un seul coup avec les nouvelles données sinon erreur de longueur des colonnes
    new_data['feature_importance']=data_retrieved['f'][0]
    new_data['colonnes']= [i for i in range(len(data_retrieved['f'][0]))] #sinon ne chnage qu'une information à la fois
    source.data = new_data
    text.text='Le crédit a été {}'.format(dict_credit[data_retrieved['prediction'][0]])
    #print(len(data_retrieved['f'][0]), len(data_retrieved['f'][0]))
    
    
auto_complete_input =  AutocompleteInput(title="Veuillez saisir l\'id client:",
                                         completions = completion_list, description ='ex 100001') #configuration liste auto suggestion seule
button = Button(label="Prédiction", button_type="success") #création du bouton et colorie vert
button.on_click(graph)#apres click va dans la fonction graph

auto_complete_input.on_change('value',update_id) #quand la valeur est changée apres entrée ou click va dans la focntion update id

curdoc().add_root(row(column(auto_complete_input,button,p),text)) #row organise sur la meme rangée, column organise les uns en dessous des autres
# bokeh serve --show "Data analysis_1"\interface.py