from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
from services.air_freight_rate.constants.air_freight_rate_constants import COGOXPRESS
from datetime import datetime
from configs.transformation_constants import HANDLING_TYPE_FACTORS, PACKING_TYPE_FACTORS, OPERATION_TYPE_FACTORS
from services.air_freight_rate.models.air_freight_location_cluster import AirFreightLocationCluster
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_airline_factor import AirFreightAirlineFactor
from micro_services.client import maps
from services.air_freight_rate.helpers.get_matching_weight_slab import get_matching_slab
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate

class AirFreightVyuh():
    def __init__(self, rate:dict={}):
        self.rate = rate

    def get_cluster_combination(self):
        origin_airport_id = self.rate['origin_airport_id']
        destination_airport_id = self.rate['destination_airport_id']

        clusters_query  = AirFreightLocationCluster.select(
                AirFreightLocationCluster.id,
                AirFreightLocationCluster.base_airport_id
            ).where(
                AirFreightLocationCluster.base_airport_id in [origin_airport_id, destination_airport_id],
                AirFreightLocationCluster.status == 'active'
            )
        clusters = jsonable_encoder(list(clusters_query.dicts()))
        
        origin_cluster_id = None
        destination_cluster_id = None

        for cluster in clusters:
            if cluster['base_airport_id'] == origin_airport_id:
                origin_cluster_id = cluster['id']
            if cluster['base_airport_id'] == destination_airport_id:
                destination_cluster_id = cluster['id']

        origin_locations = [origin_airport_id]
        destination_locations = [ destination_airport_id]
        cluster_ids = []
        if origin_cluster_id:
            cluster_ids.append(origin_cluster_id)
        
        if destination_cluster_id:
            cluster_ids.append(destination_cluster_id)
        if cluster_ids:
            location_mappings = AirFreightLocationClusterMapping.select(
                AirFreightLocationClusterMapping.location_id,
                AirFreightLocationClusterMapping.cluster_id).where(
                AirFreightLocationClusterMapping.cluster_id << cluster_ids
                )
            location_mappings = jsonable_encoder(list(location_mappings.dicts()))
            for location in location_mappings:
                if location['cluster_id'] == origin_cluster_id:
                    origin_locations.append(location['location_id'])
                else:
                    destination_locations.append(location['location_id'])
        return origin_locations,destination_locations

    def get_airlines_for_airport_pair(self,origin_airport_id,destination_airport_id):
        data = {
            'origin_airport_id': origin_airport_id,
            'destination_airport_id': destination_airport_id
        }
        airlines = maps.get_airlines_for_route(data)['airline_ids']

        return airlines
    def get_rate_combinations_to_extend(self):
        HANDLING_TYPES = []
        PACKING_TYPES = []
        OPERATION_TYPES = []
        extended_rates = []
        origin_locations,destination_locations = self.get_cluster_combination()
        for origin_airport_id in origin_locations:
            for destination_airport_id in destination_locations:
                if self.rate['airline_id'] in self.get_airlines_for_airport_pair(origin_airport_id,destination_airport_id):
                    rate = jsonable_encoder(self.rate)
                    rate['origin_airport_id'] = origin_airport_id
                    rate['destination_airport_id'] = destination_airport_id
                    extended_rates.append(rate)
        
        return extended_rates
    
    def get_existing_system_rates(self, requirement):
        from services.air_freight_rate.models.air_freight_rate import AirFreightRate
        existing_system_rates_query = AirFreightRate.select(
            AirFreightRate.id,
            AirFreightRate.source,
            AirFreightRate.validities,
            AirFreightRate.service_provider_id,
            AirFreightRate.airline_id,
            AirFreightRate.cogo_entity_id
        ).where(
            AirFreightRate.origin_airport_id == requirement["origin_airport_id"],
            AirFreightRate.destination_airport_id == requirement['destination_airport_id'],
            AirFreightRate.commodity_type == requirement['commodity_type'],
            AirFreightRate.commodity_sub_type == requirement['commodity_sub_type'],
            AirFreightRate.commodity == requirement['commodity'],
            AirFreightRate.shipment_type == requirement['shipment_type'],
            AirFreightRate.stacking_type == requirement['stacking_type'],
            AirFreightRate.source != 'predicted',
            AirFreightRate.rate_type == 'market_place',
           ~AirFreightRate.rate_not_available_entry
        )
        existing_system_rates = jsonable_encoder(list(existing_system_rates_query.dicts()))
        return existing_system_rates    
    
    def get_validities_to_create(self,rate_validity,to_add_validity_start,to_add_validity_end):
        validities_to_create = []
        validity_start = datetime.fromisoformat(rate_validity['validity_start']).date()
        validity_end = datetime.fromisoformat(rate_validity['validity_end']).date()
        if (to_add_validity_start < validity_start and to_add_validity_end < validity_start) or (to_add_validity_start > validity_end and to_add_validity_end > validity_end):
            """
            Case 1: No overlap
                ---------- 
                            -----------
                        OR
                            -----------
                ----------
            """
            validities_to_create.append({
                'validity_start': datetime.combine(to_add_validity_start,datetime.min.time()),
                'validity_end': datetime.combine(to_add_validity_end,datetime.min.time())
            })
        if validity_start > to_add_validity_start and validity_end < to_add_validity_end:
            """
            Case 2: 
            Current Validity :     -------------
            New Validity     :  ---------------------
            """
            start_validity = {
                'validity_start': datetime.combine(to_add_validity_start,datetime.min.time()),
                'validity_end': datetime.combine(validity_start,datetime.min.time())
            }
            end_validity = {
                'validity_start': datetime.combine(validity_end,datetime.min.time()),
                'validity_end': datetime.combine(to_add_validity_end,datetime.min.time())
            }
            validities_to_create =  validities_to_create + [start_validity, end_validity]
        elif validity_start > to_add_validity_start and validity_end > to_add_validity_end:
            """
            Case 3: 
            Current Validity :     -------------
            New Validity     :  ---------
            """
            validities_to_create.append({
                'validity_start': datetime.combine(to_add_validity_start,datetime.min.time()),
                'validity_end': datetime.combine(validity_start,datetime.min.time())
                })
        elif validity_end > to_add_validity_start and validity_end < to_add_validity_end:
            """
            Case 4: 
            Current Validity :     -------------
            New Validity     :           ---------------
            """
            validities_to_create.append({
                'validity_start': datetime.combine(validity_end,datetime.min.time()),
                'validity_end': datetime.combine(to_add_validity_end,datetime.min.time())
            })
        return validities_to_create

    def get_eligible_validities_to_create(self, requirement,validities_to_create):

        existing_system_rates = self.get_existing_system_rates(requirement)
        to_add_validity_start = self.rate['validity_start'].date()
        to_add_validity_end = self.rate['validity_end'].date()
        if len(existing_system_rates) == 0:
            return validities_to_create

        cogo_freight_rates_for_current_sl = []

        validities_to_create = []

        for esr in existing_system_rates:
            rate_validities = esr['validities'] or []
            if rate_validities and esr['service_provider_id'] == COGOXPRESS and esr['airline_id'] == requirement['airline_id'] and not esr['cogo_entity_id']:
                
                cogo_freight_rates_for_current_sl.append(esr)

                for rate_validity in rate_validities:
                    validities_to_create = self.get_validities_to_create(
                        rate_validity,
                        to_add_validity_start,
                        to_add_validity_end
                    )

                break 
        return validities_to_create
    
    def create_air_freight_rate_to_validities(self,rate_to_create):

        validity_start = self.rate['validity_start']
        validity_end = self.rate['validity_end']
        validities_to_create = [{ 'validity_start': validity_start, 'validity_end': validity_end }]

        validities_to_create = self.get_eligible_validities_to_create(rate_to_create,validities_to_create)
        rate_to_create['weight_slabs'] = self.get_weight_slabs(rate_to_create)
        for validity in validities_to_create:
            rate_to_create = rate_to_create | validity
            rate_to_create['extension_not_required'] = True
            try:
                create_air_freight_rate(rate_to_create)
            except:
                raise


    def extend_rate(self, source = 'rate_extension'):

        rates_to_create = self.get_rate_combinations_to_extend()
        # queue need to change to air_freight_rate
        for rate_to_create in rates_to_create:
            rate_to_create = rate_to_create | { 'source': 'rate_extension', 'service_provider_id': COGOXPRESS, "sourced_by_id": DEFAULT_USER_ID, "procured_by_id": DEFAULT_USER_ID, "performed_by_id": DEFAULT_USER_ID }
            self.create_air_freight_rate_to_validities(rate_to_create)

        return True

    def get_weight_slabs(self,rate):

        weight_slabs = rate['weight_slabs']

        original_rate_handling_type = self.rate['stacking_type']
        original_rate_packing_type = self.rate['shipment_type']
        original_rate_operation_type = self.rate['operation_type']

        current_rate_handling_type = rate['stacking_type']
        current_rate_packing_type = rate['shipment_type']
        current_rate_operation_type = rate['operation_type']

        handling_type_factor = (HANDLING_TYPE_FACTORS[current_rate_handling_type] or 1) / (HANDLING_TYPE_FACTORS[original_rate_handling_type] or 1)
        packing_type_factor = (PACKING_TYPE_FACTORS[current_rate_packing_type] or 1) / (PACKING_TYPE_FACTORS[original_rate_packing_type] or 1)
        operation_type_factor = (OPERATION_TYPE_FACTORS[current_rate_operation_type] or 1) / (OPERATION_TYPE_FACTORS[original_rate_operation_type] or 1)
        airline_factor = self.get_airline_factor(rate)
        new_weight_slabs = []
        for weight_slab in weight_slabs:
            if weight_slab['lower_limit'] < 500:
                new_weight_slab = jsonable_encoder(weight_slab)
                matching_slab = get_matching_slab(new_weight_slab['lower_limit'])
                new_weight_slab['tariff_price'] = weight_slab['tariff_price'] * handling_type_factor * packing_type_factor * operation_type_factor * airline_factor[matching_slab]
                new_weight_slabs.append(new_weight_slab)
        
        return new_weight_slabs
    
    def get_airline_factor(self,rate_to_rate):
        airline_factors = AirFreightAirlineFactor.select(AirFreightAirlineFactor.slab_wise_factor).where(
            AirFreightAirlineFactor.origin_airport_id == rate_to_rate['origin_airport_id'],
            AirFreightAirlineFactor.destination_airport_id == rate_to_rate['destination_airport_id'],
            AirFreightAirlineFactor.derive_airline_id == rate_to_rate['airline_id'],
            AirFreightAirlineFactor.base_airline_id == self.rate.get('airline_id')
        ).first()
        if not airline_factors:
            airline_factors = {
            "0.0-45":1,
            "45-100":1,
            "100-300":1,
            "300-500":1,
            "500-5000":1,
        }
        else:
            airline_factors = airline_factors.slab_wise_factor
        return jsonable_encoder(airline_factors)
