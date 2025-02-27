import os
import yaml
import joblib

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

class LoadYmls():
    FCL_FREIGHT_CHARGES = None
    FCL_FREIGHT_LOCAL_CHARGES = None
    FCL_FREIGHT_CURRENCIES = None
    FCL_FREIGHT_SEASONAL_CHARGES = None
    FCL_CFS_CHARGES  = None
    FCL_CUSTOMS_CHARGES = None
    AIR_FREIGHT_CHARGES=None
    AIR_FREIGHT_LOCAL_CHARGES = None
    AIR_FREIGHT_SURCHARGES = None
    AIR_FREIGHT_WAREHOUSE_CHARGES=None
    AIR_FREIGHT_CURRENCIES= None
    HAULAGE_FREIGHT_CHARGES = None
    FTL_FREIGHT_CHARGES = None
    FTL_FREIGHT_CURRENCIES = None
    
    AIR_CUSTOMS_CHARGES = None

    def __init__(self):
        self.FCL_FREIGHT_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_freight_charges.yml"))
        self.FCL_FREIGHT_LOCAL_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_freight_local_charges.yml"))
        self.FCL_FREIGHT_CURRENCIES = self.load_ymls(os.path.join(ROOT_DIR, "libs", "currencies.yml"))
        self.FCL_FREIGHT_SEASONAL_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_freight_seasonal_charges.yml"))
        self.FCL_CFS_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_cfs_charges.yml"))
        self.FCL_CUSTOMS_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_customs_charges.yml"))
        self.AIR_FREIGHT_CHARGES=self.load_ymls(os.path.join(ROOT_DIR,"charges","air_freight_charges.yml"))
        self.AIR_FREIGHT_LOCAL_CHARGES=self.load_ymls(os.path.join(ROOT_DIR,"charges","air_freight_local_charges.yml"))
        self.AIR_FREIGHT_SURCHARGES = self.load_ymls(os.path.join(ROOT_DIR,"charges","air_freight_surcharges.yml"))
        self.AIR_FREIGHT_WAREHOUSE_CHARGES=self.load_ymls(os.path.join(ROOT_DIR,"charges","air_freight_warehouse_charges.yml"))
        self.AIR_FREIGHT_CURRENCIES=self.load_ymls(os.path.join(ROOT_DIR,"libs","currencies.yml"))        
        self.HAULAGE_FREIGHT_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "haulage_freight_charges.yml"))
        self.FTL_FREIGHT_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "ftl_freight_charges.yml"))
        self.FTL_FREIGHT_CURRENCIES=self.load_ymls(os.path.join(ROOT_DIR,"libs","currencies.yml"))        
        
        self.AIR_CUSTOMS_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "air_customs_charges.yml"))

    def load_ymls(self, file):
        with open(file, 'r') as f:
            data = yaml.safe_load(f)
        return data

yml_obj = LoadYmls()

FCL_FREIGHT_CHARGES = yml_obj.FCL_FREIGHT_CHARGES
FCL_FREIGHT_LOCAL_CHARGES = yml_obj.FCL_FREIGHT_LOCAL_CHARGES
FCL_FREIGHT_CURRENCIES = yml_obj.FCL_FREIGHT_CURRENCIES
FTL_FREIGHT_CURRENCIES = yml_obj.FTL_FREIGHT_CURRENCIES
FCL_FREIGHT_SEASONAL_CHARGES = yml_obj.FCL_FREIGHT_SEASONAL_CHARGES
FCL_CFS_CHARGES  = yml_obj.FCL_CFS_CHARGES 
FCL_CUSTOMS_CHARGES = yml_obj.FCL_CUSTOMS_CHARGES
AIR_FREIGHT_CHARGES=yml_obj.AIR_FREIGHT_CHARGES
AIR_FREIGHT_LOCAL_CHARGES=yml_obj.AIR_FREIGHT_LOCAL_CHARGES
AIR_FREIGHT_SURCHARGES= yml_obj.AIR_FREIGHT_SURCHARGES
AIR_FREIGHT_WAREHOUSE_CHARGES=yml_obj.AIR_FREIGHT_WAREHOUSE_CHARGES
AIR_FREIGHT_CURRENCIES= yml_obj.AIR_FREIGHT_CURRENCIES
HAULAGE_FREIGHT_CHARGES = yml_obj.HAULAGE_FREIGHT_CHARGES
FTL_FREIGHT_CHARGES = yml_obj.FTL_FREIGHT_CHARGES
AIR_CUSTOMS_CHARGES = yml_obj.AIR_CUSTOMS_CHARGES

class LoadPredictionModels():
    FCL_PREDICTION_MODEL = None
    AIR_PREDICTION_MODEL = None
    FTL_PREDICTION_MODEL = None
    HAULAGE_PREDICTION_MODEL = None

    def __init__(self):
        self.FCL_PREDICTION_MODEL = self.load_prediction_model(os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models", "fcl_freight_prediction_model.pkl"))
        self.AIR_PREDICTION_MODEL = self.load_prediction_model(os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models", "air_freight_prediction_model.pkl"))
        self.FTL_PREDICTION_MODEL = self.load_prediction_model(os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models", "ftl_freight_prediction_model.pkl"))
        self.HAULAGE_PREDICTION_MODEL = self.load_prediction_model(os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models","haulage_freight_prediction_model.pkl"))

    def load_prediction_model(self, path):
        model = joblib.load(open(path, 'rb'))
        return model

pred_model_obj = LoadPredictionModels()

FCL_PREDICTION_MODEL = pred_model_obj.FCL_PREDICTION_MODEL
AIR_PREDICTION_MODEL = pred_model_obj.AIR_PREDICTION_MODEL
FTL_PREDICTION_MODEL = pred_model_obj.FTL_PREDICTION_MODEL
HAULAGE_PREDICTION_MODEL = pred_model_obj.HAULAGE_PREDICTION_MODEL