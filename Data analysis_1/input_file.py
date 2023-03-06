import base64
from bokeh.plotting import curdoc,figure
from bokeh.models.widgets import FileInput
from bokeh.models import ColumnDataSource,BooleanFilter,PreText,CDSView
from bokeh.layouts import column,row
import io
import pandas as pd
import requests
import json
from bokeh.models import AutocompleteInput
from bokeh.palettes import Magma, Cividis

id_list = pd.read_csv(r'C:\Users\utilisateur\Documents\MyAmaWok\OC Data Scientist\Projet OC 7 Implementer un modele de Scoring\datasets\application_test.csv',usecols=['SK_ID_CURR']) # import colonne id de test

# tornado client limited to 100mb 

url = "http://127.0.0.1:8000/"
df = pd.DataFrame()
dict_credit = {0: 'payée',
               1: 'refusée'}
#source = ColumnDataSource(df)
text = PreText(text=(""),styles={'font-size':'20pt','color': 'red'}) # ,align ='center'on ne met rien au départ # 100005 feature_importance = 0 pk ? 

source = ColumnDataSource (data = {'feature_importance':[0],
                                   'colonnes':[0],
                                   'names':[0]}) #graph sans rien au départ
#columns = [TableColumn(field=col, title = col) for col in df.columns]
file_input = FileInput(accept=".csv",width=400, height=50)

df_retrieved = [pd.DataFrame(columns=(["SK_ID_CURR"]))]
completion_list = [0]
if len(df_retrieved[0]) == 0:
    # liste des identifiants des clients
    completion_list[0] = [str(id) for id in id_list["SK_ID_CURR"].tolist()]

auto_complete_input = AutocompleteInput(completions=completion_list[0], description='ex 100001',
                                        placeholder="Veuillez saisir l\'id client par exemple 100001...",
                                        min_width=300,
                                        restrict=True)  # configuration liste auto suggestion seule

TOOLTIPS = [
    ("index", "$index"),
    ("Importance de la variable", "@feature_importance"),  # v3
    ("Nom de la variable", "@names")
]
p = figure(
    title='Importance des variables dans la prise de décision',
    x_axis_label="Variables",
    y_axis_label="Feature Importance",
    sizing_mode="scale_width",
    tooltips=TOOLTIPS,
    height=300)  # config graph de base

# mask sur feature positive
positive_ = [True for i in range(len(source.data['feature_importance']))]
negative_ = [True for i in range(len(source.data['feature_importance']))]
view1 = CDSView(filter=BooleanFilter(positive_))
neg_view = CDSView(filter=BooleanFilter(negative_))

p.vbar(x='colonnes',
       top='feature_importance',
       width=0.5,
       source=source)  # ajout du nom des axes et la source des données


# v4 rajouté pie plot avec pourcenatge de 0 et 1 pour la prise de décision selon le threshold

ph = figure(title="Variables qui tendent vers un refus",
            x_axis_label='variables',
            y_axis_label='Importance de la variable',
            sizing_mode="scale_width",
            tooltips=TOOLTIPS,
            height=150)

ph.vbar(source=source,
        view=view1,
        x='colonnes',
        top='feature_importance',
        width=0.5,
        color=Cividis[10][1])

ph_1 = figure(title="Variables qui tendent vers un octroi de crédit",
              x_axis_label='variables',
              y_axis_label='Importance de la variable',
              sizing_mode="scale_width",
              tooltips=TOOLTIPS,
              height=150)

ph_1.vbar(source=source,
          view=neg_view,
          x='colonnes',
          top='feature_importance',
          width=0.5,
          color=Magma[11][6])

#def graph(event):
    
    
#callback
def upload_data(attr, old, new): #charger et envoyer df fastapi nettoya
    auto_complete_input.visible = False
    print("dataset has been uploaded succesfully")
    decoded =  base64.b64decode(new)
    f = io.BytesIO(decoded)
    df= pd.read_csv(f)
    res = requests.post(url+"receive_df", json=df.to_json(orient='split'))
    data_retrieved = json.loads(res._content.decode('utf-8'))
    df_retrieved[0] = pd.DataFrame(data_retrieved['df']) #le dataframe dans source
    completion_list[0] = [str(id) for id in df_retrieved[0]["SK_ID_CURR"]]
    auto_complete_input.completions = completion_list[0]
    print(df_retrieved[0])
    auto_complete_input.visible = True
    

   
def update_id(attr, old, new):#attrname, old, new => obligatoire pour ce composant
    global res
    global value_input #pour récupérer la variable pour le graph
    print('dedans')
    value_input = auto_complete_input.value # valeur dans le champs
    #res = requests.post(url+value_input) #requete a fastapi
    print(value_input)
    
    if (len(df_retrieved[0]) != 0) & (int(value_input) in df_retrieved[0]['SK_ID_CURR'].tolist()): #si dataset nettoyé récupéré donc pas demo mais données réelles
        print('df_remplie et id complété',value_input)
        df_filtered = df_retrieved[0][df_retrieved[0]['SK_ID_CURR']==int(value_input)]
        print('df avec id',df_filtered)
        res = requests.post(url+"predict/reel/", json=df_filtered.to_json(orient='split'))
    elif len(df_retrieved[0])==0:
        res =requests.post(url+"predict/"+str(value_input))
    print('2eme req',res._content)
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
    
auto_complete_input.on_change('value',update_id) #quand la valeur est changée apres entrée ou click va dans la fonction update id
    
file_input.on_change('value',upload_data)

 # transformer dataframe en json 

#data_table = DataTable(source=source, columns =columns, width=400, height=400)


curdoc().add_root(column(row(auto_complete_input,file_input),text,p,ph,ph_1))#,data_table

####### PART 1 ######### get file working


#sending this dataframe to fastapi
#bokeh serve --show input_file.py
#bokeh serve --log-level=debug input_file.py log mais faut comprendre
