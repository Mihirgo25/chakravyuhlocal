from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from datetime import datetime, timedelta
import pandas as pd, os, joblib
from services.envision.helpers.air_freight_rate_preprocessing import air_freight_preprocessing
from peewee import *
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
from configs.definitions import ROOT_DIR

def air_freight_rate_prediction_training():
    date = datetime.now() - timedelta(days = 30)
    rates_data_query = AirFreightRate.select(
                    AirFreightRate.origin_airport_id,
                    AirFreightRate.destination_airport_id,
                    AirFreightRate.commodity,
                    AirFreightRate.length,
                    AirFreightRate.breadth,
                    AirFreightRate.height,
                    AirFreightRate.airline_id,
                    AirFreightRate.shipment_type,
                    AirFreightRate.stacking_type,
                    AirFreightRate.created_at,
                    AirFreightRate.weight_slabs
                ).where(AirFreightRate.rate_not_available_entry == False,
                        AirFreightRate.created_at <= date,
                        ~AirFreightRate.source << ['predicted','rate_extension','expired_extension'])

    batch_size = 5000
    offset = 0
    data_frames = []

    print('Fetching Data...')
    while True:
        batch_query = rates_data_query.offset(offset).limit(batch_size)
        batch_data = [
            {
                "origin_airport_id": rate.origin_airport_id,
                "destination_airport_id": rate.destination_airport_id,
                "commodity": rate.commodity,
                "length": rate.length,
                "breadth": rate.breadth,
                "height": rate.height,
                "airline_id": rate.airline_id,
                "shipment_type": rate.shipment_type,
                "stacking_type": rate.stacking_type,
                "created_at":rate.created_at,
                "weight_slabs":rate.weight_slabs
            }
            for rate in batch_query
        ]
        
        data_frames.append(pd.DataFrame(batch_data))
        offset += batch_size

        if not batch_data:
            break    

    # Concatenate the data frames into a single DataFrame
    air_freight_rates = pd.concat(data_frames, ignore_index=True)
    air_freight_rates = air_freight_preprocessing(air_freight_rates)
    print('Building Pipeline...')
    create_pipeline_for_model(air_freight_rates)

    return None

def create_pipeline_for_model(air_freight_rates):
    num_cols = air_freight_rates.select_dtypes(include = [int, float]).columns.tolist()
    cat_cols = air_freight_rates.select_dtypes(include = 'object').columns.tolist()

    num_cols.remove('price_USD')
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder()

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)
        ])

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', GradientBoostingRegressor(loss='squared_error', learning_rate=0.15,
                                            n_estimators=2000, max_depth=5)
        )])

    X = air_freight_rates[num_cols + cat_cols]
    y = air_freight_rates['price_USD']
    print('Model Training....')
    pipeline.fit(X, y)
    print('Model Training Done...')

    air_freight_model = open(os.path.join(ROOT_DIR, "services", "envision", "prediction_based_model", "air_freight_forecasting_model.pkl"),'wb')
    joblib.dump(pipeline, air_freight_model, compress = 3)
    return 'Model Created'