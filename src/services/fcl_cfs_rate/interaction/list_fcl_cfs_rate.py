POSSIBLE_DIRECT_FILTERS = ['id', 'location_id', 'country_code', 'trade_id', 'content_id', 'trade_type', 'service_provider id', 'importer_exporter_id', 'commodity', 'container_type', 'container_size', 'cargo_handling_type']
POSSIBLE_INDIRECT_FILTERS = ['location_ids', 'importer_exporter_present', 'is_rate_available']


def list_fcl_cfs_rate(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False,pagination_data_required=True ):
    
    return 0
    