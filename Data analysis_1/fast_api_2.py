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

# 2. Create the app object
app = FastAPI()



templates = pd.read_csv('../../datasets/X_columns_template.csv')
test = pd.read_csv('../../datasets/new_df_test.csv')

def mise_en_forme(data_line):
    
    ''' objectif == meme  colonne que l'apprentissage
    
        patrameters:
        dataline => ligne de données avec les colonnes
        
        return :
        rajoute les colonnes qui ne sont pas présentes dans le jeu de test'''
    
    cols_not_in_test = [col_train for col_train in templates['0'].values if col_train not in data_line.columns] # ['0']nom de la colonne ou il y a les noms de colonnes colonnes qui sont absentes du test
    cols_not_in_train = [col_test for col_test in test.columns if col_test not in templates.columns]
    
    ##if len(cols_not_in_train) !=0:
    #    print(f"mama mia {len(cols_not_in_train)} colonnes supplémentaires dans le test_set")
    #    data_line = data_line.drop(cols_not_in_train, axis =1)
    for cols  in  cols_not_in_test :
        print(cols)
        if cols != 'TARGET':
            data_line[cols] =-1  #attribution de la valeur atypique vue que absent
            
    return cols_not_in_test


#enlever toute la mise en forme déjà dans la fonction qui renverra le résultat, il manquera le score et 

pickle_in = open("pipel.pkl","rb")     #notre pipeline importé
classifier_test=pickle.load(pickle_in) #chargé dans une variable
#classifier_test.predict(test_id)       #prediction

# 3. Index route, opens automatically on http://127.0.0.1:8000
@app.get('/')
def index():
    return {'message': 'Bonjour, pour quel client souhaitez vous avoir l\'étude du crédit (jeu de test) ?'}


@app.post('/predict/{client_id}')
def predict_credit( client_id :int): #recupere les colonnes avec les formats et le client_id  (data:Credit_demand_columns),
     
    test_id = test[test['SK_ID_CURR']==client_id].copy() #exemple sur lequel on va travailler # vérifier si une seule ligne
    mise_en_forme(test_id)                               #rajoute la/les colonnes mqtes pour que mm forme que X_train => si col présnete dans x_test et pas dans train ? suppr?
    test_id = test_id[templates['0'].values]             #réorganiser les colonnes comme X_train sur lequel le modele c'est entrainé
   
    prediction = classifier_test.predict(test_id)

    val_avt_std = classifier_test['scaler'].transform(test_id)[0,:][classifier_test['rfe'].get_support()]
    feat_imp = classifier_test['model'].coef_* val_avt_std# feature importance
    
    return {'prediction':[prediction[0].tolist()],'f':feat_imp.tolist()}

     # pour résoudre ce problème ( TypeError: cannot convert dictionary update sequence element #0 to a sequenc)

# 5. Run the API with uvicorn
#    Will run on http://127.0.0.1:8000
#if __name__ == '__main__':
#    uvicorn.run(app, host='127.0.0.1', port=8000)

# first_parameter  uvicorn file_name:(name of fastapi()) --reload


