from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit


POSSIBLE_HASH_FILTERS = {
    'air_freight_rate': {
      'direct': ['origin_airport_id', 'destination_airport_id', 'commodity', 'airline_id', 'operation_type', 'service_provider_id']
    }
  }
def list_air_freight_rate_audits(filters={},page_limit=10,page=1,sort_by='updated_at',sort_type='desc',pagination_data_required=True,user_data_required=False):
    query = get_query()
    query = apply_hash_filters(query)

def get_query(sort_by, sort_type):
    query = AirFreightRateAudit.select().order_by(eval("AirFreightRateAudit.{}.{}()".format(sort_by,sort_type)))
    return query

def apply_hash_filters(query):
    return query
