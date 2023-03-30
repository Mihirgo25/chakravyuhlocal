from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from database.rails_db import get_organization
from configs.fcl_freight_rate_constants import LOCATION_HIERARCHY_FOR_WEIGHT
from fastapi.encoders import jsonable_encoder

possible_direct_filters = [
    'origin_location_id',
    'destination_location_id',
    'origin_location_type',
    'destination_location_type',
    'organization_category',
    'shipping_line_id',
    'service_provider_id',
    'importer_exporter_id',
    'is_cogo_assured',
    'container_size',
    'commodity',
    'trade_type'
]

def get_most_relevant_slabs(data, direct_filters):

    for object in data:
        filters_count = 0
        for key, value in object.items():
            if key in direct_filters:
                if value and direct_filters[key]:
                    filters_count += 1
        object['filters_count'] = filters_count

    data = sorted(data, key=lambda t: (
        -t['filters_count'],
        0 if t['service_provider_id'] else 1,
        0 if t['organization_category'] else 1,
        0 if t['importer_exporter_id'] else 1,
        0 if t['trade_type'] else 1,
        LOCATION_HIERARCHY_FOR_WEIGHT[t['origin_location_type']] if t['origin_location_type'] else 1,
        LOCATION_HIERARCHY_FOR_WEIGHT[t['destination_location_type']] if t['destination_location_type'] else 1,
        0 if t['shipping_line_id'] else 1,
        0 if t['container_size'] else 1,
        0 if t['commodity'] else 1)
    )
    try:
        return {'max_weight': data[0]['max_weight'], 'slabs':data[0]['slabs']}
    except:
        return None

def get_fcl_freight_weight_slabs_for_rates(requirements, rates):

    origin_locations = [requirements["origin_port_id"], requirements["origin_country_id"], None]
    destination_locations = [requirements["destination_port_id"], requirements["destination_country_id"], None]

    service_provider_ids = []
    shipping_line_ids = []
    for rate in rates:
        service_provider_ids.append(rate["service_provider_id"])
        shipping_line_ids.append(rate["shipping_line_id"])

    service_provider_ids.append(None)
    shipping_line_ids.append(None)

    service_providers = get_organization(id=service_provider_ids)

    service_providers_to_category = {}

    all_categories = [None]

    for sp in service_providers:
        service_providers_to_category[sp["id"]] = sp
        ctypes = sp["category_types"] or []
        all_categories = all_categories + ctypes


    weight_slabs_query = FclWeightSlabsConfiguration.select(
        FclWeightSlabsConfiguration.origin_location_id,
        FclWeightSlabsConfiguration.destination_location_id,
        FclWeightSlabsConfiguration.origin_location_type,
        FclWeightSlabsConfiguration.destination_location_type,
        FclWeightSlabsConfiguration.shipping_line_id,
        FclWeightSlabsConfiguration.service_provider_id,
        FclWeightSlabsConfiguration.importer_exporter_id,
        FclWeightSlabsConfiguration.is_cogo_assured,
        FclWeightSlabsConfiguration.container_size,
        FclWeightSlabsConfiguration.commodity,
        FclWeightSlabsConfiguration.organization_category,
        FclWeightSlabsConfiguration.slabs,
        FclWeightSlabsConfiguration.trade_type,
        FclWeightSlabsConfiguration.status,
        FclWeightSlabsConfiguration.max_weight,
    ).where(
        FclWeightSlabsConfiguration.origin_location_id << origin_locations,
        FclWeightSlabsConfiguration.destination_location_id << destination_locations,
        FclWeightSlabsConfiguration.origin_location_type << ['seaport', 'country', None],
        FclWeightSlabsConfiguration.destination_location_type << ['seaport', 'country', None],
        FclWeightSlabsConfiguration.shipping_line_id << shipping_line_ids,
        FclWeightSlabsConfiguration.service_provider_id << service_provider_ids,
        FclWeightSlabsConfiguration.is_cogo_assured == False,
        FclWeightSlabsConfiguration.container_size << [requirements['container_size'], None],
        FclWeightSlabsConfiguration.commodity << [requirements['commodity'], None],
        # FclWeightSlabsConfiguration.container_type << [requirements['container_type'], None],
        FclWeightSlabsConfiguration.organization_category << all_categories,
    )

    if 'importer_exporter_id' in requirements:
        weight_slabs_query = weight_slabs_query.where(((FclWeightSlabsConfiguration.importer_exporter_id == requirements["importer_exporter_id"]) | (FclWeightSlabsConfiguration.importer_exporter_id == None)))

    weight_slabs = jsonable_encoder(list(weight_slabs_query.dicts()))


    if len(weight_slabs) > 0:

        group_by_rate = {}

        for rate in rates:
            key = rate["id"]
            if key not in group_by_rate:
                group_by_rate[key] = []
            sp_id = rate["service_provider_id"]
            for weight_slab in weight_slabs:
                if ('service_provider_id' not in weight_slab or weight_slab['service_provider_id'] == sp_id) and ('shipping_line_id' not in weight_slab or weight_slab['shipping_line_id'] == rate["shipping_line_id"]) and ('organization_category' not in weight_slab or weight_slab['organization_category'] in service_providers_to_category[sp_id]):
                    group_by_rate[key].append(weight_slab)

        common_direct_filters = {
            "origin_location_id": origin_locations,
            "destination_location_id": destination_locations,
            "origin_location_type": ['seaport', 'country', None],
            "destination_location_type": ['seaport', 'country', None],
            "importer_exporter_id": [requirements["importer_exporter_id"], None],
            "container_size": [requirements["container_size"], None],
            "commodity": [requirements["commodity"], None],
            "container_type": [requirements["container_type"], None],
            "is_cogo_assured": [False, None],
        }
        category = service_providers_to_category[sp_id] or []
        final_result = {}
        for rate in rates:
            direct_filters = {
                "shipping_line_id": [rate["shipping_line_id"], None],
                "service_provider_id": [rate["service_provider_id"], None],
                "organization_category": category + [None]
            } | common_direct_filters
            if rate["id"] in group_by_rate:
                configs = group_by_rate[rate["id"]]
                final_result[rate["id"]] = get_most_relevant_slabs(configs, direct_filters)
            else:
                final_result[rate["id"]] = None
        return final_result

    final_result = {}
    for rate in rates:
        final_result[rate["id"]] = []
    return final_result



