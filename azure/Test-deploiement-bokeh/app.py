
from bokeh.models import AutocompleteInput
import requests #api request
import json # convert from bytes to dict 
from bokeh.models import CDSView, ColumnDataSource,BooleanFilter#?
from bokeh.plotting import curdoc, figure
from bokeh.models import Button
from bokeh.layouts import column, gridplot,row,layout
from bokeh.events import ButtonClick
from bokeh.models import PreText
import pandas as pd
import numpy as np #rajouter à requirements
from bokeh.palettes import Magma, Cividis

id_list = pd.read_csv(r'application_test.csv',usecols=['SK_ID_CURR']) # import colonne id de test
completion_list = [str(id) for id in id_list["SK_ID_CURR"].tolist()]        #liste des identifiants des clientst

text = PreText(text=(""),styles={'font-size':'20pt','color': 'red'}) # ,align ='center'on ne met rien au départ # 100005 feature_importance = 0 pk ? 

source = ColumnDataSource (data = {'feature_importance':[0],
                                   'colonnes':[0],
                                   'names':[0]}) #graph sans rien au départ
dict_credit = {0 :'payée',
               1 :'refusée'} # dico pour mapping apres avec la prédiction

url = "https://test-deploiement-fastapi-v1.azurewebsites.net/predict/"  #url de l'api pour récupérer prédiction et feature importance
#url ="http://127.0.0.1:8000/predict/"

TOOLTIPS = [
    ("index", "$index"),
    ("Importance de la variable", "@feature_importance"),#v3
    ("Nom de la variable","@names")
]
p = figure(
    title='Importance des variables dans la prise de décision',
    x_axis_label="Variables",
    y_axis_label="Feature Importance",
    sizing_mode="scale_width",
    tooltips=TOOLTIPS) #config graph de base

positive_ = [True for i in range (len(source.data['feature_importance']))] #mask sur feature positive
negative_ = [True for i in range (len(source.data['feature_importance']))]
view1 = CDSView(filter=BooleanFilter(positive_))
neg_view = CDSView(filter=BooleanFilter(negative_))

p.vbar(x= 'colonnes',
       top='feature_importance',
       width=0.5,
       source=source)#ajout du nom des axes et la source des données


#v4 rajouté pie plot avec pourcenatge de 0 et 1 pour la prise de décision selon le threshold

ph = figure(title = "Variables qui tendent vers un refus",
            x_axis_label = 'variables',
            y_axis_label='Importance de la variable',
            sizing_mode="scale_width",
            tooltips=TOOLTIPS)

ph.vbar(source = source,
        view= view1,
        x = 'colonnes',
        top = 'feature_importance',
        width=0.5,
        color = Cividis[10][1])

ph_1 = figure(title = "Variables qui tendent vers un octroi de crédit",
            x_axis_label = 'variables',
            y_axis_label='Importance de la variable',
            sizing_mode="scale_width",
            tooltips=TOOLTIPS)

ph_1.vbar(source = source,
        view= neg_view,
        x = 'colonnes',
        top = 'feature_importance',
        width=0.5,
        color= Magma[11][6],)


def update_id(attr, old, new):#attrname, old, new => obligatoire pour ce composant
    global res
    global value_input #pour récupérer la variable pour le graph
    print('dedans')
    value_input = auto_complete_input.value # valeur dans le champs
    res = requests.post(url+value_input) #requete a fastapi
      
def graph(event): #event obligatoire  pour ce composant
    #print('lapi est {}'.format(url)
    data_retrieved = json.loads(res._content.decode('utf-8')) #data_retrieved
    new_data = dict() #cd pour instancier en un seul coup avec les nouvelles données sinon erreur de longueur des colonnes
    new_data['feature_importance']=data_retrieved['feature_importance'][0] #premiere ligne
    new_data['colonnes']= [i for i in range(len(data_retrieved['feature_importance'][0]))] #sinon ne chnage qu'une information à la fois 0 index de la ligne
    #print(data_retrieved['nom_colonnes'])
    new_data['names']=data_retrieved['nom_colonnes']
    source.data = new_data
    text.text='Le crédit a été {} pour l\'id {}'.format(dict_credit[data_retrieved['prediction']],value_input) #100057
    #print(new_data) #debugging si graph n'apparait pas
    positive_ = [True if float(imp) > 0 else False for imp in source.data['feature_importance']]
    negative_ = [False if float(imp) > 0 else True for imp in source.data['feature_importance']]
    neg_view.filter = BooleanFilter(negative_)
    view1.filter =  BooleanFilter(positive_)
    
auto_complete_input =  AutocompleteInput(completions = completion_list, description ='ex 100001', placeholder = "Veuillez saisir l\'id client par exemple 100001...",min_width=300,restrict = True) #configuration liste auto suggestion seule
button = Button(label="Prédiction", button_type="success",height=30, sizing_mode='stretch_width',align = 'start') #création du bouton et colorie vert
button.on_click(graph)#apres click va dans la fonction graph

auto_complete_input.on_change('value',update_id) #quand la valeur est changée apres entrée ou click va dans la fonction update id
test = layout([
               row(children=[auto_complete_input,button], sizing_mode='fixed',height=250, width=150),
               row([text],sizing_mode="scale_width"),
               [p],
               [ph],
               [ph_1]],sizing_mode='stretch_both')#"
curdoc().add_root(test)
#curdoc().add_root(row(column(auto_complete_input,button,p),text,sizing_mode="stretch_both")) #row organise sur la meme rangée, column organise les uns en dessous des autres
# bokeh serve --show "Data analysis_1"\interface.py => tuto qui a aidé en partie https://www.codemag.com/Article/2111061/Building-Dashboards-Using-Bokeh
#https://stackoverflow.com/questions/54772820/bokeh-custom-layout pour organisation des graph