import json
from fastapi import Request
import httpx
import json
from configs.env import APP_ENV, DEFAULT_USER_ID
from micro_services.discover_client import get_instance_url


def authorize_token(
    request: Request
):
    authorization_token = request.headers.get('authorization')
    authorization_scope = request.headers.get('authorizationscope')
    authorization_parameters = request.headers.get('authorizationparameters')
    if APP_ENV != "production" or "is_authorization_required" in request.query_params or (request.method == "POST" and "is_authorization_required" in json.loads(request._body)):
        return {"status_code": 200, "isAuthorized": True, "setters": { "performed_by_id": DEFAULT_USER_ID, "performed_by_type": "agent" }}

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

    request_api_path = request.scope.get("path")[1:]

    actual_resource = request_api_path.split('/')[-1]

    data = {"request_api_path": actual_resource}

    with httpx.Client() as client:
        response = client.get(url, headers=header, params=data)
        if response.status_code == 200:
            return json.loads(response.content)
    try:
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return {
            "status_code": response.content,
            "content": f"HTTP Exception for {exc.request.url} -{exc}",
        }
