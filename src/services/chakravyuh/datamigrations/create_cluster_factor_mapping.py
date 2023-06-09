from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_location_cluster_factor import AirFreightLocationClusterFactor
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from joblib import delayed,Parallel
def create_cluster_factor_mapping():
    with db.atomic():
        cluster_data = AirFreightLocationClusters.select(AirFreightLocationClusters.id).execute()
        data_list = [row.id for row in cluster_data]
        main_list = []
        location_data=AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.location_id,AirFreightLocationClusterMapping.cluster_id)

        location_data = jsonable_encoder(list(location_data.dicts()))
        for i in range(0,len(data_list)):
            for j in range(i+1,len(data_list)):
                factor_list = []
                for location in location_data:
                    if location['cluster_id'] == data_list[i] or location['cluster_id']==data_list[j]:
                        row={
                            'origin_cluster_id':data_list[i],
                            'destination_cluster_id':data_list[j],
                            'location_id':location['location_id'],
                            'cluster_id':location['cluster_id'],
                        }
                        row2={
                            'origin_cluster_id':data_list[j],
                            'destination_cluster_id':data_list[i],
                            'location_id':location['location_id'],
                            'cluster_id':location['cluster_id'],
                        }
                        factor_list.append(row)
                        factor_list.append(row2)
                if factor_list:
                    main_list.append(factor_list)

        
        Parallel(n_jobs=4)(delayed(insert_into_factor_mappings)(factor) for factor in main_list)

def insert_into_factor_mappings(factors):
    AirFreightLocationClusterFactor.insert_many(factors).execute()
    
                












