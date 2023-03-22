# %%
#adaptation pour fastapi avec données du datasets

# 1. Library imports
from fastapi import FastAPI, File, Request, UploadFile
import pandas as pd
import json
from feature_importance import feat_imp
import csv
from io import BytesIO, TextIOWrapper

# 2. Create the app object
app = FastAPI()

# 3. Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'message': 'Bonjour, pour quel client souhaitez vous avoir l\'étude du crédit (jeu de test) ?'}

@app.post('/predict/{client_id}')#pour la demo
def predict_credit( client_id :int): #recupere les colonnes avec les formats et le client_id  (data:Credit_demand_columns),
    return feat_imp(id=client_id)

#@app.post('/predict/reel/')#pour la demo
#async def predict_reel(data_to_pred: Request): #recupere les colonnes avec les formats et le client_id  (data:Credit_demand_columns),
#    data_info = await data_to_pred.json()
#    data = pd.read_json(data_info, orient='split')
#    print(data)
#    return (feat_imp(df=data))

#@app.post("/receive_df") #sera prochainement supprimer
#async def receive_df(info: Request):
#    req_info = await info.json()
#    data = pd.read_json(req_info, orient='split')
#    return (feat_imp(df=data,pred=False))

@app.post("/uploadfile/") # charger un fichier d'une ligne pour faire une prediction 
async def create_upload_file(file: UploadFile=File(...)):
    print('1')
    contents = await file.read()
    print('fastapi lecture fichier',len(contents),type(contents), contents)
    csv_data = csv.reader(TextIOWrapper(BytesIO(contents))) #BytesIO(contents)
    rows = [row for row in csv_data] #{"filename": file.filename, "contents": rows}
    #df = pd.DataFrame(columns= rows[0], data =rows[1:])
    df = pd.read_csv(BytesIO(contents))
    print('dataframe',df.values)
    return  feat_imp(df=df)


