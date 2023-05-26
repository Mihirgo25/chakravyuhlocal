from peewee import *
from playhouse.fields import PickleField

# class FclCfsRateRequest(Model):
#     # Define your model fields here
#     source = CharField()
#     source_id = CharField()
#     performed_by_id = CharField()
#     performed_by_org_id = CharField()
#     performed_by_type = CharField()
#     preferred_rate = FloatField(null=True)
#     preferred_rate_currency = CharField(null=True)
#     preferred_detention_free_days = IntegerField(null=True)
#     cargo_readiness_date = DateField(null=True)
#     remarks = PickleField(default=[])
#     booking_params = PickleField(default={})
#     container_size = CharField(null=True)
#     commodity = CharField(null=True)
#     country_id = CharField(null=True)
#     port_id = CharField(null=True)
#     trade_type = CharField(null=True)
#     status = CharField(default='active')

#     class Meta:
#         database = db
#         table_name = 'fcl_cfs_rate_request'

# class CreateFclCfsRateRequest:
#     def __init__(self, source, source_id, performed_by_id, performed_by_org_id, performed_by_type, preferred_rate=None,
#                  preferred_rate_currency=None, preferred_detention_free_days=None, cargo_readiness_date=None, remarks=[],
#                  booking_params={}, container_size=None, commodity=None, country_id=None, port_id=None, trade_type=None):
#         self.source = source
#         self.source_id = source_id
#         self.performed_by_id = performed_by_id
#         self.performed_by_org_id = performed_by_org_id
#         self.performed_by_type = performed_by_type
#         self.preferred_rate = preferred_rate
#         self.preferred_rate_currency = preferred_rate_currency
#         self.preferred_detention_free_days = preferred_detention_free_days
#         self.cargo_readiness_date = cargo_readiness_date
#         self.remarks = remarks
#         self.booking_params = booking_params
#         self.container_size = container_size
#         self.commodity = commodity
#         self.country_id = country_id
#         self.port_id = port_id
#         self.trade_type = trade_type


def get_unique_object_params(request):
    return {
        'source': request.source,
        'source_id': request.source_id,
        'performed_by_id': request.performed_by_id,
        'performed_by_type': request.performed_by_type,
        'performed_by_org_id': request.performed_by_org_id
    }

def get_create_params(self):
    return {
        'preferred_rate': self.preferred_rate,
        'preferred_rate_currency': self.preferred_rate_currency,
        'preferred_detention_free_days': self.preferred_detention_free_days,
        'cargo_readiness_date': self.cargo_readiness_date,
        'remarks': self.remarks,
        'booking_params': self.booking_params,
        'container_size': self.container_size,
        'commodity': self.commodity,
        'country_id': self.country_id,
        'port_id': self.port_id,
        'trade_type': self.trade_type,
        'status': 'active'
    }

def create_fcl_cfs_rate_request(request):
    request, created = FclCfsRateRequest.get_or_create(**get_unique_object_params(request))
    request.set_attributes(get_create_params(request))

    if not request.save():
        request.errors = request.errors
        return

    request.create_audit(request)
    request.send_notifications(request)

    return {'id': request.id}







def create_audit(self, request):
    audit_params = {
        'action_name': 'create',
        'performed_by_id': self.performed_by_id,
        'data': self.get_audit_params()
    }
    request.audits.create(**audit_params)

def get_audit_params(self):
    return {k: v for k, v in self.__dict__.items() if k != 'performed_by_id'}

def send_notifications(self, request):
    # Your code here to send notifications to supply agents
    pass

# ######## ---------------------------------------   Usage


# create_request = CreateFclCfsRateRequest(
#     source='source123',
#     source_id='source_id123',
#     performed_by_id='performed_by_id123',
#     performed_by_org_id='performed_by_org_id123',
#     performed_by_type='performed_by_type123',
#     preferred_rate=None,
#     preferred_rate_currency=None,
#     preferred_detention_free_days=None,
#     cargo_readiness_date=None,
#     remarks=[],
#     booking_params={},
#     container_size=None,
#     commodity=None,
#     country_id=None,
#     port_id=None,
#     trade_type=None
# )
# result = create_request.execute()
