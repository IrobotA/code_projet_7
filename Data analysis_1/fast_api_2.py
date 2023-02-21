# %%
#adaptation pour fastapi avec données du datasets

# 1. Library imports
import uvicorn
from fastapi import FastAPI
#from Credit_demands import Credit_demand_columns pas nécessaire puisque non rentré à la main
import numpy as np
import pandas as pd
import pickle
import pandas as pd
from feature_importance import feat_imp

# 2. Create the app object
app = FastAPI()

#templates = pd.read_csv('../../datasets/X_columns_template.csv')
test_2 = pd.read_csv(r'C:\Users\utilisateur\Documents\MyAmaWok\OC Data Scientist\Projet OC 7 Implementer un modele de Scoring\datasets\application_test.csv')


# 3. Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'message': 'Bonjour, pour quel client souhaitez vous avoir l\'étude du crédit (jeu de test) ?'}

@app.post('/predict/{client_id}')
def predict_credit( client_id :int): #recupere les colonnes avec les formats et le client_id  (data:Credit_demand_columns),
    return feat_imp(id=client_id,df=test_2)
    
     # pour résoudre ce problème ( TypeError: cannot convert dictionary update sequence element #0 to a sequenc)

# 5. Run the API with uvicorn
#    Will run on http://127.0.0.1:8000
#if __name__ == '__main__':
#    uvicorn.run(app, host='127.0.0.1', port=8000)

# first_parameter  uvicorn file_name:(name of fastapi()) --reload


