from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit

def create_audit(request):
    RateSheetAudit.create(
        action_name = request.get('action_name'),
        object_id = request.get('object_id'),
        performed_by_id = request.get('performed_by_id'),
        procured_by_id = request.get('procured_by_id'),
        sourced_by_id = request.get('sourced_by_id'),
        performed_by_type = request.get('performed_by_type') or 'agent',
        data = request.get('data')
    )
