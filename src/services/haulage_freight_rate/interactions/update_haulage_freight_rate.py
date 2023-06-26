
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate

def update_haulage_freight_rate(request):
    haulage = find_haulage_object(request)
    haulage.update_line_item_messages()
    haulage.set_platform_price()
    haulage.set_is_best_price()
    haulage.update_platform_prices_for_other_service_providers()

    return {"id": haulage.id}

def find_haulage_object(request):
    query = HaulageFreightRate.update({HaulageFreightRate.line_items: get_update_params(request)}).where(HaulageFreightRate.id == request.get('id'))
    return query

def get_update_params(request):
    keys_to_slice = ["line_items"]
    line_item = {key: request[key] for key in keys_to_slice if key in request}
    return line_item
