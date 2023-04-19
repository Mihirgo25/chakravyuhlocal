from database.db_session import db
from services.dpe.models.fcl_freight_rate_estimation import FclFreightRateEstimation
def create_fcl_estimated_rate_data(request):
    with db.atomic():
      return create_fcl_estimated_rate(request)
    
def create_fcl_estimated_rate(request):
    print(request)
    row = {
        "origin_location_id": request.get("origin_location_id"),
        "destination_location_id": request.get("destination_location_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "currency": request.get("currency")
    }
    
    rate=(
      FclFreightRateEstimation.select()
        .where(
            FclFreightRateEstimation.origin_location_id == request.get("origin_location_id"),
            FclFreightRateEstimation.destination_location_id == request.get("destination_location_id"),
            FclFreightRateEstimation.container_size == request.get("container_size"),
            FclFreightRateEstimation.container_type == request.get("container_type"),
            FclFreightRateEstimation.commodity == request.get("commodity"),
        )
        .first()
    )
   
    if not rate:
        rate = FclFreightRateEstimation()
        for key in list(row.keys()):
            setattr(rate, key, row[key])
    
    rate.lower_rate=request.get("lower_rate")
    rate.upper_rate=request.get("upper_rate")
    
    
    rate.save()



    return rate.id