from datetime import date

def update_haulage_freight_rate_platform_prices(request):
    from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
    freight_objects = HaulageFreightRate.select().where(
    HaulageFreightRate.origin_location_id == request.get('origin_location_id'),
    HaulageFreightRate.destination_location_id == request['destination_location_id'],
    HaulageFreightRate.container_size == request['container_size'],
    HaulageFreightRate.container_type == request['container_type'],
    HaulageFreightRate.commodity == request['commodity'], 
    HaulageFreightRate.haulage_type == request['haulage_type'],
    HaulageFreightRate.shipping_line_id == request['shipping_line_id'] ,
    HaulageFreightRate.importer_exporter_id == request['importer_exporter_id'],
    HaulageFreightRate.is_line_items_error_messages_present == request.get('is_line_items_error_messages_present')
    )
    
    if 'origin_location_id' in request:
        freight_objects = freight_objects.where(HaulageFreightRate.origin_location_id == request['origin_location_id'])
    else:
        freight_objects = freight_objects.where(HaulageFreightRate.origin_main_location_id == None)
        
    if 'destination_location_id' in request:
        freight_objects = freight_objects.where(HaulageFreightRate.destination_location_id == request['destination_location_id'])
    else:
        freight_objects = freight_objects.where(HaulageFreightRate.destination_location_id == None)
    
    if 'importer_exporter_id' in request:
        freight_objects = freight_objects.where(HaulageFreightRate.importer_exporter_id == request['importer_exporter_id'])
    else:
        freight_objects = freight_objects.where(HaulageFreightRate.importer_exporter_id == None)

    freight_objects = freight_objects.execute()

    for freight in freight_objects:
        freight.set_platform_price()   
        freight.save()