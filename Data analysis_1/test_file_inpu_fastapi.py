# %%
#adaptation pour fastapi avec données du datasets

# 1. Library imports
import uvicorn
import asyncio
from fastapi import FastAPI, File, Request
import pandas as pd
from feature_importance import feat_imp
from typing import Union

# 2. Create the app object
app = FastAPI()

# 3. Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'message': 'Bonjour, pour quel client souhaitez vous avoir l\'étude du crédit (jeu de test) ?'}

@app.post('/predict/{client_id}')#pour la demo
def predict_credit( client_id :int): #recupere les colonnes avec les formats et le client_id  (data:Credit_demand_columns),
    return feat_imp(id=client_id)

@app.post('/predict/reel/')#pour la demo
async def predict_reel(data_to_pred: Request): #recupere les colonnes avec les formats et le client_id  (data:Credit_demand_columns),
    data_info = await data_to_pred.json()
    data = pd.read_json(data_info, orient='split')
    print(data)
    return (feat_imp(df=data))

@app.post("/receive_df")
async def receive_df(info: Request):
    req_info = await info.json()
    data = pd.read_json(req_info, orient='split')
    return (feat_imp(df=data,pred=False))
