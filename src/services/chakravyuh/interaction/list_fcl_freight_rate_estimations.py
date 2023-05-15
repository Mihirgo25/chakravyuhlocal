from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from fastapi.encoders import jsonable_encoder
from math import ceil


def list_fcl_freight_rate_estimations(filters, page_limit, page, sort_by, sort_type):
    query = FclFreightRateEstimation.select().order_by(eval('FclFreightRateEstimation.{}.{}()'.format(sort_by,sort_type)))

    pagination_data = get_pagination_data(query, page, page_limit)
    query = query.paginate(page,page_limit)

    data = get_data(query)


    return { 'list': data } | (pagination_data)


def get_data(query):
    data = jsonable_encoder(list(query.dicts()))


    for item in data:
        item['price'] = item['line_items'][0]
        del item['line_items']
    
    return data


def get_pagination_data(query, page, page_limit):
  total_count = query.count()
  
  pagination_data = {
    'page': page,
    'total': ceil(total_count/page_limit),
    'total_count': total_count,
    'page_limit': page_limit
    }
  
  return pagination_data