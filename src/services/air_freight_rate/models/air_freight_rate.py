from peewee import *
import datetime
from database.db_session import db

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_airport_id=UUIDField(index=True,null=True)
    origin_country_id=UUIDField(null=True)
    origin_trade_id=UUIDField(null=True)
    origin_continent_id=UUIDField(null=True)
    destination_airport_id=UUIDField(index=True,null=True)
    destination_country_id=UUIDField(null=True)
    destination_trade_id=UUIDField(null=True)
    destination_continent_id=UUIDField(null=True)
    commodity=CharField(null=True,index=True)
    origin_airport=BinaryJSONField(null=True)
    destination_airport=BinaryJSONField(null=True)
    airline_id=UUIDField(null=True)
    service_provider_id=UUIDField(null=True)
    importer_exporter_id=UUIDField(null=True)
    min_price=FloatField(null=True)
    currency=CharField(null=True)
    discount_type=CharField(null=True)
    bookings_count=IntegerField(null=True)
    bookings_importer_exporters_count=IntegerField(null=True)
    spot_searches_count=IntegerField(null=True)
    spot_searches_importer_exporters_count=IntegerField(null=True)
    priority_score=IntegerField(null=True)
    priority_score_updated_at=DateTimeField(default=datetime.datetime.now,index=True)
    weight_slabs=BinaryJSONField(null=True)
    is_best_price=BooleanField(null=True)
    origin_local_id=UUIDField(null=True)
    destination_local_id=UUIDField(null=True)
    origin_local=BinaryJSONField(null=True)
    destination_local=BinaryJSONField(null=True)
    surcharge_id=UUIDField(null=True)
    airline=BinaryJSONField(null=True)
    service_provider=BinaryJSONField(null=True)
    warehouse_rate_id=UUIDField(null=True)
    rate_not_available_entry=BooleanField(null=True)
    origin_storage_id=UUIDField(null=True)
    destination_storage_id=UUIDField(null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    operation_type=CharField(null=True)
    validities=BinaryJSONField(null=True)
    last_rate_available_date=DateTimeField(default=datetime.datetime.now,index=True)
    length=IntegerField(null=True)
    breadth=IntegerField(null=True)
    height=IntegerField(null=True)
    maximum_weight=IntegerField(null=True)
    shipment_type=CharField(null=True)
    stacking_type=CharField(null=True)
    commodity_sub_type=CharField(null=True)
    commodity_type=CharField(null=True)
    price_type=CharField(null=True)
    cogo_entity_id=UUIDField(null=True,index=True)
    rate_type=CharField(null=True)
    source=CharField(null=True)
    external_rate_id=UUIDField(null=True)
    flight_uuid=UUIDField(null=True)
    created_at=DateTimeField(default=datetime.datetime.now,index=True)
    updated_at=DateTimeField(default=datetime.datetime.now,index=True)
    sourced_by_id=UUIDField(null=True,index=True)
    procured_by_id=UUIDField(null=True,index=True)

    class Meta:
        table_name='air_freight_temp'
