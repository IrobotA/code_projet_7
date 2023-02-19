import pickle
import pandas as pd

test_2 = pd.read_csv(r'C:\Users\utilisateur\Documents\MyAmaWok\OC Data Scientist\Projet OC 7 Implementer un modele de Scoring\datasets\application_test.csv')

#Fonction de remplacement des valeurs 
def nettoyage(df):
    for col_na in df.isna().sum()[df.isna().sum() > 0 ].index: 
        print(col_na,df[col_na].dtype)
        if df[col_na].dtype =='object':
            print(col_na)
            df[col_na] = df[col_na].fillna(df[col_na].mode().values[0]) # var categ val mqte => mot le plus fréquent
        else :
            df[col_na] = df[col_na].fillna(df[col_na].median()) # val mqtes => mediane
    return df.isna().sum().sum()

pickle_in = open("pipel_3.pkl","rb") #notre pipeline importé v2 = pipel_2, v1 = pipel# v3 one hot et scaler
pipe=pickle.load(pickle_in) #chargé dans une variable

def feat_imp(pipe,df,id=456221) :
    nettoyage(df) #suppression val mqtes et ou remplacement par le mode pour valeur categorielle
    test_id = df[df['SK_ID_CURR']==id].copy() #sélection de la ligne que l'on va utiliser pour prédire le modèle
    val_transfo = pipe.steps[0][1].transform(test_id)[0][pipe.best_estimator_.steps[1][1].get_support()] # preprocessing des valeurs + selection des features peretinentes 
    return {'prediction':pipe.predict(test_id)[0],'feature_importance':pipe.best_estimator_.steps[1][1].estimator_.coef_* val_transfo[0]}# feature importance
    