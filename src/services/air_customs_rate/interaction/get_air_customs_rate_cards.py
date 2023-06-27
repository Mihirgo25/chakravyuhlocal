# import  sentry_sdk, traceback
# from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
# from fastapi.encoders import jsonable_encoder

# def get_air_customs_rate_cards(request):
#     try:
#         query = initialize_air_customs_rate_query(request)
#         air_customs_rates = jsonable_encoder(list(query.dicts()))





# def initialize_air_customs_rate_query(request):
#     query = AirCustomsRate.select(
#         AirCustomsRate.line_items,
#         AirCustomsRate.service_provider_id,
#         AirCustomsRate.importer_exporter_id,
#     ).where(
#         AirCustomsRate.airport_id == request.get('airport_id'),
#         AirCustomsRate.trade_type == request.get('trade_type'),
#         AirCustomsRate.rate_not_available_entry == False,
#         AirCustomsRate.is_line_items_error_messages_present== False
#         (AirCustomsRate.importer_exporter_id == request.get('importer_exporter_id') | (AirCustomsRate.importer_exporter_id.is_null(True)))
#     )

#     return query