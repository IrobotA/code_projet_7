import pickle
import pandas as pd
import numpy as np
import re 
from fastapi.encoders import jsonable_encoder


test_2 = pd.read_csv(r'C:\Users\utilisateur\Documents\MyAmaWok\OC Data Scientist\Projet OC 7 Implementer un modele de Scoring\datasets\application_test.csv')

print('chargement df_test effectué')
#Fonction de remplacement des valeurs du df , directement dans l'interface

print('step1_def_nettoyage')

def nettoyage(df):
    for col_na in df.isna().sum()[df.isna().sum() > 0 ].index: 
        if df[col_na].dtype =='object':
            df[col_na] = df[col_na].fillna(df[col_na].mode().values[0]) # var categ val mqte => mot le plus fréquent
        else :
            df[col_na] = df[col_na].fillna(df[col_na].median()) # val mqtes => mediane
    return df.isna().sum().sum()

#import model
#pickle_in = open("pipel_4.pkl","rb") #notre pipeline importé v2 = pipel_2, v1 = pipel# v3 one hot et scaler
#pipe=pickle.load(pickle_in) #chargé dans une variable
#print('step_2_pipeline_loaded')

##### pipeline #####
pipeline_model = open("pipeline_transfo_model.pkl", "rb")  # import model
pipeline_model = pickle.load(pipeline_model)  # chargé dans une variable
print('step_2_pipeline_with_model_loaded')


##### shap #####
explainer = open("true_explainer.pkl", "rb")  # import model
explainer = pickle.load(explainer)  # chargé dans une variable
print('step_3_explainer_loaded')

##### feature_importance #####
def feat_imp(pred=True,
             df=test_2,
             pipeline=pipeline_model,
             id=456221,
             threshold = 0.1):
    print(df.shape)
    if df.shape != (1,245):
        nettoyage(df)
        #if cleaned is False : #si pas déjà nettoyé
        #    nettoyage(df)     #suppression val mqtes et ou remplacement par le mode pour valeur categorielle
        #    print('df_cleaned')
            
        print('feat_imp in progress')
        #if pred == False : #return df cleaned 
        #    val_to_return = {'df': df.to_dict()}
        #else : #si prediction necessaire 
        if len(df)!=1:
            test_id = df[df['SK_ID_CURR'] == id].copy()
        else :
            test_id = df # si une seule ligne
            id = test_id['SK_ID_CURR'].values
            
        
        #test_id.drop(['SK_ID_CURR'],axis=1, inplace =True)
        if df.shape[1] != 245:
            val_transfo = pipeline['categ_scaler'].transform(test_id)                   # preprocessing des valeurs 
        print('shape val transfo',val_transfo.shape)
        cols=[re.sub('one-hot-encoder__|remainder__','',col_names) for col_names in pipeline['categ_scaler'].get_feature_names_out()]
        print('proba',pipeline['modelisation'].predict_proba(val_transfo)[0][1])
        
    elif df.shape == (1,245) :
        print("one line and already transformed")
        val_transfo = df.values
        cols = df.columns
    
    shap_val = explainer(val_transfo)
    shap_val = shap_val.values
    #shap_val = round(shap_val,4)
    print('shap_values',shap_val[0,:])
    print('id',id)
    if pipeline['modelisation'].predict_proba(val_transfo)[0][1] >= threshold:  #seuillage => ou scoring 
        prediction = 1 # defaut de remboursement credit
    else:
        prediction = 0 # remboursement
    print(pipeline['modelisation'].predict_proba(val_transfo)[0][1] >= threshold, prediction)
    #print(cols.values)
    val_to_return = {
                    'prediction': prediction,
                    'feature_importance':[np.round(val,5) for val in shap_val[0,:]],
                    'nom_colonnes': [col for col in cols],
                    'score': pipeline['modelisation'].predict_proba(val_transfo)[0][1]}
        
    print('step_4_prediction_done')
    return val_to_return
