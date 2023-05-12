from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation


def list_fcl_freight_rate_estimations(filters, page_limit, page, sort_by, sort_type):
    query = FclFreightRateEstimation.select().order_by(eval('FclFreightRateEstimation.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
