from micro_services.client import maps

def get_fcl_freight_relevant_vessel_extensions(vessel_number):
    service_lane = maps.get_service_lane(data={ 'vessel_number': vessel_number })