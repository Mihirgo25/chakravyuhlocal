import json
from fastapi import Request, Header
import httpx
import json
from configs.env import APP_ENV, RUBY_ADDRESS_URL
from micro_services.discover_client import get_instance_url


def authorize_token(
    request: Request,
    authorization_token: str = Header(default=None, convert_underscores=False),
    authorization_scope: str = Header(default=None, convert_underscores=False),
    authorization_parameters: str = Header(default=None, convert_underscores=False),
):      
    if APP_ENV == "development" or "is_authorization_required" in request.query_params:
        return {"status_code": 200, "isAuthorized": False}

    url = "https://api-nirvana1.dev.cogoport.io" + "/verify_request" #get_instance_url('user')

    if (
        authorization_token is None
        and authorization_scope is None
        and authorization_parameters is None
    ):
        header = {
            "Authorization": request.headers.get("authorization"),
            "AuthorizationScope": request.headers.get("authorizationscope"),
            "AuthorizationParameters": request.headers.get("authorizationparameters"),
        }
    else:
        header = {
            "Authorization": authorization_token,
            "AuthorizationScope": authorization_scope,
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
