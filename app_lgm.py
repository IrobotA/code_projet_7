#adaptation pour fastapi avec données du datasets

# 1. Library imports
import uvicorn
from fastapi import FastAPI
#from Credit_demands import Credit_demand_columns pas nécessaire puisque non rentré à la main
import numpy as np
import pandas as pd
import pickle

import pandas as pd
# 2. Create the app object
app = FastAPI()

#clients_csv_file = pd.read_csv('../datasets/application_train.csv') #la ou il y a les infos clients
clients_csv_file = pd.read_csv('X_test.csv') #pas le bon 
pickle_in = open("classifier_2.pkl","rb") #notre modele importer
classifier_2=pickle.load(pickle_in)       #model loaded  

# 3. Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'message': 'Bonjour, quel client souhaitez vous analyser (jeu de test) ?'}


@app.post('/predict/{client_id}')
def predict_credit( client_id :int): #recupere les colonnes avec les formats et le client_id  (data:Credit_demand_columns),
    info_client = clients_csv_file[clients_csv_file['SK_ID_CURR']==client_id] # info client, 1 ligne
   
    prediction = classifier_2.predict(info_client)

    return {
        'prediction': [prediction[0]],
        'feature_importance': [f.item() for f in classifier_2.feature_importances_]#.item() pour avoir le int python => https://stackoverflow.com/questions/9452775/converting-numpy-dtypes-to-native-python-types

    } # pour résoudre ce problème ( TypeError: cannot convert dictionary update sequence element #0 to a sequenc)

# 5. Run the API with uvicorn
#    Will run on http://127.0.0.1:8000
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)

# first_parameter  uvicorn file_name:(name of fastapi()) --reload