from datetime import date

def update_haulage_freight_rate_platform_prices(request):
    from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
    freight_objects = HaulageFreightRate.select().where(
    HaulageFreightRate.origin_location_id == request.get['origin_location_id'],
    HaulageFreightRate.destination_location_id == request.get['destination_location_id'],
    HaulageFreightRate.container_size == request.get['container_size'],
    HaulageFreightRate.container_type == request.get['container_type'],
    HaulageFreightRate.commodity == request.get['commodity'], 
    HaulageFreightRate.haulage_type == request.get['haulage_type'],
    HaulageFreightRate.shipping_line_id == request.get['shipping_line_id'] ,
    HaulageFreightRate.importer_exporter_id == request.get['importer_exporter_id'],
    HaulageFreightRate.is_line_items_error_messages_present == request.get('is_line_items_error_messages_present')
    )
    
    if 'origin_location_id' in request:
        freight_objects = freight_objects.where(HaulageFreightRate.origin_location_id == request.get['origin_location_id'])
    else:
        freight_objects = freight_objects.where(HaulageFreightRate.origin_main_location_id == None)
        
    if 'destination_location_id' in request:
        freight_objects = freight_objects.where(HaulageFreightRate.destination_location_id == request.get['destination_location_id'])
    else:
        freight_objects = freight_objects.where(HaulageFreightRate.destination_location_id == None)
    
    if 'importer_exporter_id' in request:
        freight_objects = freight_objects.where(HaulageFreightRate.importer_exporter_id == request.get['importer_exporter_id'])
    else:
        freight_objects = freight_objects.where(HaulageFreightRate.importer_exporter_id == None)

    freight_objects = freight_objects.execute()

    for freight in freight_objects:
        freight.set_platform_price()   
        freight.save()