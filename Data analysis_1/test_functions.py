
import feature_importance


def test_feature_importance(): #shape of pipe
    assert len(feature_importance.pipe)==2  #1)categ_scaler 2)RFE
    assert len(feature_importance.feat_imp.val_transfo)==164,  "val_transfo length is not 164 it is "+ str(len(feature_importance.feat_imp.val_transfo)) #nombre de features sélectionnées
    assert feature_importance.feat_imp.val_transfo != 0 ,"erreur dans les feature importances"
    assert feature_importance.feat_imp.test_id.isna().sum()==0,"Il y a des valeurs manquantes dans test_id" #pas de valeurs manquantes
    
    