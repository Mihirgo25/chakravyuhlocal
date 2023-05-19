from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit
from fastapi.encoders import jsonable_encoder
from math import ceil
from datetime import datetime




def get_periodic_fcl_freight_rate_estimation_trends(estimation_id, created_at_greater_than, created_at_less_than):
  query = FclFreightRateEstimationAudit.select(
      FclFreightRateEstimationAudit.data,
      FclFreightRateEstimationAudit.id,
      FclFreightRateEstimationAudit.created_at
  ).where(
      FclFreightRateEstimationAudit.object_id == estimation_id,
      FclFreightRateEstimationAudit.created_at.cast('date') >= datetime.fromisoformat(created_at_greater_than).date(),
      FclFreightRateEstimationAudit.created_at.cast('date') <= datetime.fromisoformat(created_at_less_than).date()
    ).order_by(eval('FclFreightRateEstimationAudit.{}.{}()'.format('created_at','desc')))


  data = get_data(query)

  return { 'data': data } 


def get_data(query):
    data = jsonable_encoder(list(query.dicts()))


    for item in data:
        estimation_data = item['data']
        line_items = estimation_data.get('line_items')
        actual_line_items = estimation_data.get('actual_line_items')

        freight_lineitem = {}

        actual_lineitem = {}

        if line_items:
            for line_item in line_items:
                if line_item['code'] == 'BAS':
                    freight_lineitem = line_item
                    break
        
        if actual_line_items:
            for line_item in actual_line_items:
                if line_item['code'] == 'BAS':
                    actual_lineitem = line_item
                    break
        
        item['tf'] = freight_lineitem
        item['actual_line_item'] = actual_lineitem
        item['created_at'] = datetime.fromisoformat(item['created_at']).date()
    
    group_by_date = {}

    for item in data:
        created_at = item['created_at']
        if created_at in group_by_date:
            group_by_date[created_at]
    
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