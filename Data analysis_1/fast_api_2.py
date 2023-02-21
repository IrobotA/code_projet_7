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
    #dictionary update sequence element #0 errur du au fait que feature importance dans un array => solution avec .tolist()
     
    #test_id = test[test['SK_ID_CURR']==client_id].copy() #exemple sur lequel on va travailler # vérifier si une seule ligne
    #mise_en_forme(test_id)                               #rajoute la/les colonnes mqtes pour que mm forme que X_train => si col présnete dans x_test et pas dans train ? suppr?
    #test_id = test_id[templates['0'].values]             #réorganiser les colonnes comme X_train sur lequel le modele c'est entrainé
   #
    #prediction = classifier_test.predict(test_id)
#
    #val_avt_std = classifier_test['scaler'].transform(test_id)[0,:][classifier_test['rfe'].get_support()]
    #feat_imp = classifier_test['model'].coef_* val_avt_std# feature importance
    #
    #return {'prediction':[prediction[0].tolist()],'f':feat_imp.tolist()}
    
    

     # pour résoudre ce problème ( TypeError: cannot convert dictionary update sequence element #0 to a sequenc)

# 5. Run the API with uvicorn
#    Will run on http://127.0.0.1:8000
#if __name__ == '__main__':
#    uvicorn.run(app, host='127.0.0.1', port=8000)

# first_parameter  uvicorn file_name:(name of fastapi()) --reload


