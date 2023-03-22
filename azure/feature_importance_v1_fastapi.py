import pickle
import pandas as pd
import re

test_2 = pd.read_csv('application_test.csv')
df_ = pd.DataFrame()

# Fonction de remplacement des valeurs
print('step1')


def nettoyage(df):
    for col_na in df.isna().sum()[df.isna().sum() > 0].index:
        if df[col_na].dtype == 'object':
            # var categ val mqte => mot le plus fréquent
            df[col_na] = df[col_na].fillna(df[col_na].mode().values[0])
        else:
            df[col_na] = df[col_na].fillna(
                df[col_na].median())  # val mqtes => mediane
    return df.isna().sum().sum()


# notre pipeline importé v2 = pipel_2, v1 = pipel# v3 one hot et scaler
pickle_in = open("pipel_4.pkl", "rb")
pipe = pickle.load(pickle_in)  # chargé dans une variable
print('step2')


def feat_imp(pred=True,
             df=test_2,
             pipeline=pipe,
             id=456221,
             threshold=0.1,
             cleaned=False):

    if cleaned is False:  # si pas déjà nettoyé
        # suppression val mqtes et ou remplacement par le mode pour valeur categorielle
        nettoyage(df)
    print('step3')
    if pred == False:
        val_to_return = {'df': df.to_dict()}
    else:  # si prediction necessaire renvoit prediction
        # ajout threshold
        if len(df) != 1:
            test_id = df[df['SK_ID_CURR'] == id].copy()
        else:
            test_id = df
        # preprocessing des valeurs + selection des features peretinentes
        val_transfo = pipeline.steps[0][1].transform(
            test_id)[0][pipeline.steps[1][1].get_support()]
        cols = [re.sub('one-hot-encoder__|remainder__', '', col_names)
                for col_names in pipeline.steps[0][1].get_feature_names_out()[pipeline['rfe'].get_support()]]

        if pipeline.decision_function(test_id)[0] > threshold:
            prediction = 1
        else:
            prediction = 0
        print("prediction_done")
        val_to_return = {'prediction': prediction,
                         'feature_importance': (pipeline.steps[1][1].estimator_.coef_ * val_transfo).tolist(),
                         'nom_colonnes': cols}

    return val_to_return
