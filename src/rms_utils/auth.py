import json
from fastapi import Request
import httpx
import json
import sentry_sdk
from configs.env import APP_ENV, DEFAULT_USER_ID
from micro_services.discover_client import get_instance_url


def authorize_token(
    request: Request
):
    authorization_token = request.headers.get('authorization')
    authorization_scope = request.headers.get('authorizationscope')
    authorization_parameters = request.headers.get('authorizationparameters')
    request_body = json.loads(request._body)
    if APP_ENV != "production" or "is_authorization_required" in request.query_params or (request.method == "POST" and "is_authorization_required" in request_body):
        if (request.method == "GET" and not "is_authorization_required" in request.query_params) or (request.method == "POST" and not "is_authorization_required" in request_body):
            return {"status_code": 200, "isAuthorized": True, "setters": { "performed_by_id": request_body.get("performed_by_id") or DEFAULT_USER_ID, "performed_by_type": request_body.get("performed_by_type") or "agent" }}
        return { "status_code": 200, "isAuthorized": False }

    url = get_instance_url('user') + "/verify_request"

    if (
        authorization_token is None
        and authorization_scope is None
        and authorization_parameters is None
    ):
        return {"status_code": 403, "isAuthorized": False}
    else:
        header = {
            "Authorization": authorization_token if authorization_token else "",
            "AuthorizationScope": authorization_scope if authorization_scope else "",
            "AuthorizationParameters": authorization_parameters if authorization_parameters else "",
        }
    try:

        request_api_path = request.scope.get("path")[1:]
    
        actual_resource = request_api_path.split('/')[-1]
    
        data = {"request_api_path": actual_resource}
    
        with httpx.Client() as client:
            response = client.get(url, headers=header, params=data, timeout=10)
            if response.status_code == 200:
                return json.loads(response.content)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return {
                "status_code": response.content,
                "content": f"HTTP Exception for {exc.request.url} -{exc}",
            }
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {"status_code": 403, "isAuthorized": False}
