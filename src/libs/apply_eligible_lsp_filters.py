from operator import attrgetter
from playhouse.postgres_ext import ArrayField
from database.rails_db import get_eligible_orgs

def apply_eligible_lsp_filters( query, model, service):
    eligible_lsps = get_eligible_orgs(service)
    key = 'service_provider_id'
    if eligible_lsps:
        query = query.where(attrgetter(key)(model) << eligible_lsps)
    return query
