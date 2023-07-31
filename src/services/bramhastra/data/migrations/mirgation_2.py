from database.rails_db import get_connection
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder


















class PopulateAirFreightRateStatistics(MigrationHelpers):
    def __init__(self) -> None:
        self.cogoback_connection = get_connection()
    
    def populate_active_rate_ids(self):
        query = AirFreightRate.select().where(AirFreightRate.validities.is_null(False) and AirFreightRate.validities != '[]').order_by(AirFreightRate.id)
        total_count = query.count()
        
        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())
        count = 0
        offset = 0
   
        while offset < total_count:
            cur_query = query.offset(offset).limit(BATCH_SIZE)
            rates = jsonable_encoder(list(cur_query .dicts()))
            offset+= BATCH_SIZE
            row_data = []
            for rate in rates: 
                for validity in rate['validities']:
                    count+= 1
                    
                    identifier = '{}_{}'.format(rate['id'], validity['id'])
                          
                    rate_params = {key: value for key, value in rate.items() if key in RATE_PARAMS} 
                    validity_params = self.get_validity_params(validity)
                    
                    row = {
                        **rate_params, 
                        **validity_params,
                        "containers_count": rate.get("containers_count") or 0,
                        'identifier' : identifier,
                        'rate_id' : rate.get('id'),
                        "rate_created_at": rate.get('created_at'),
                        "rate_updated_at": rate.get('updated_at'),
                        "rate_type": rate.get('rate_type') or DEFAULT_RATE_TYPE,
                        "origin_region_id": REGION_MAPPING.get(rate.get('origin_port_id')),
                        "destination_region_id": REGION_MAPPING.get(rate.get('destination_port_id')),
                        "market_price": validity.get('market_price') or validity.get('price'),
                        'validity_id' : validity.get('id'),
                    }
                    row_data.append(row)
                    print(count)
            AirFreightRateStatistic.insert_many(row_data).execute()
            
