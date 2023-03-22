#%%

import feature_importance


def test_feature_importance(): #shape of pipe
    if len(feature_importance.feat_imp.__defaults__[1]) == 1: #si la longeur est de 1
        assert feature_importance.feat_imp.test_id.isna().sum()==0,"Il y a des valeurs manquantes dans l'id sélectionnée, veuillez les remplir et renvoyer le fichier" #pas de valeurs manquantes
        

# %%
