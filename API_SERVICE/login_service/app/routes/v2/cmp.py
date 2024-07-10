import json
import logging
import requests

from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter
from starlette.responses import JSONResponse

from login_service.app.common.const import json_headers
from login_service.app.common.config import settings

logger = logging.getLogger()
router = APIRouter()


class UserInfoWrap(BaseModel):
    class UserInfo(BaseModel):
        user_id: str
        email: str
        name: str
        project_id: Optional[str]

    data: UserInfo


@router.get("/cmp/v2/projectList")
async def get_project_list() -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        params = {
            "page": 0,
            "size": 200
        }
        res = requests.get(
            url=f"{url}/orgs/manage/all",
            params=params,
            verify=False
        )
        data = res.json()
        logger.info(data)
        project_list = data["items"]
        admin_header = get_admin_header()
        for project in project_list :
            project_id = project["id"]
            project["detail"] = get_project_detail(admin_header, project_id)

        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": project_list}
        )
    except Exception as e:
        return result_error(e)


@router.get("/cmp/v2/projectUser")
async def get_project_user() -> JSONResponse:
    try:
        admin_header = get_admin_header()
        url = settings.CMP_INFO.CMP_API_BASE_URL

        params = {
            "token": admin_header["X-HEADER-TOKEN"],
            "page": 0,
            "size": 200
        }
        res = requests.get(
            url=f"{url}/users",
            params=params,
            verify=False
        )
        logger.info(res.json())
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": res.json()["content"]}
        )
    except Exception as e:
        return result_error(e)


@router.post("/cmp/v2/createUser")
async def create_project_user(params: UserInfoWrap) -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        param = params.data

        payload = {
            "userId": param.user_id,
            "email": param.email,
            "name": param.name,
            "userRole": "USER"
        }
        res = requests.post(
            url=f"{url}/users",
            headers=json_headers,
            data=json.dumps(payload),
            verify=False
        )
        logger.info(res)
        status_code = res.status_code
        if status_code == 200 :
            return JSONResponse(
                status_code=200,
                content={"result": 1, "errorMessage": "", "data": "success"}
            )
        else:
            return JSONResponse(
                status_code=200,
                content={"result": 0, "errorMessage": "Already Create User"}
            )
    except Exception as e:
        return result_error(e)


@router.post("/cmp/v2/registerUser")
async def register_project_user(params: UserInfoWrap) -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        admin_header = get_admin_header()
        admin_header.update(json_headers)
        param = params.data
        project_id = param.project_id

        payload = [{
            "userId": param.user_id,
            "email": param.email,
            "name": param.name,
            "userRole": "USER"
        }]

        res = requests.post(
            url=f"{url}/orgs/{project_id}/orgUserAdd/multi",
            headers=admin_header,
            data=json.dumps(payload),
            verify=False
        )
        status_code = res.status_code
        if status_code == 200 :
            return JSONResponse(
                status_code=200,
                content={"result": 1, "errorMessage": "", "data": "success"}
            )
        else:
            return JSONResponse(
                status_code=200,
                content={"result": 0, "errorMessage": "Already Register User"}
            )
    except Exception as e:
        return result_error(e)


@router.post("/cmp/v2/registerProjectOwner")
async def register_project_owner(params: UserInfoWrap) -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        admin_header = get_admin_header()
        admin_header.update(json_headers)
        param = params.data

        payload = [{
            "userId": param.user_id,
            "email": param.email,
            "name": param.name,
            "role": "OWNER"
        }]

        res = requests.post(
            url=f"{url}/users/createAdmin",
            headers=admin_header,
            data=json.dumps(payload),
            verify=False
        )
        logger.info(res)
        status_code = res.status_code
        if status_code == 200:
            return JSONResponse(
                status_code=200,
                content={"result": 1, "errorMessage": "", "data": "success"}
            )
        else:
            return JSONResponse(
                status_code=200,
                content={"result": 0, "errorMessage": "Server Error"}
            )
    except Exception as e:
        return result_error(e)


@router.get("/cmp/v2/getProjectOwner")
async def get_project_owner() -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        params = {
            "size": 100,
            "page": 0
        }

        res = requests.get(
            url=f"{url}/users/adminList",
            params=params,
            verify=False
        )
        logger.info(res)
        logger.info(res.json())
        status_code = res.status_code
        if status_code == 200:
            return JSONResponse(
                status_code=200,
                content={"result": 1, "errorMessage": "", "data": res.json()["items"]}
            )
        else:
            return JSONResponse(
                status_code=200,
                content={"result": 0, "errorMessage": "Server Error"}
            )
    except Exception as e:
        return result_error(e)


def get_project_detail(admin_header: dict, project_id: str) -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        res = requests.get(
            url=f"{url}/orgs/{project_id}/users",
            headers=admin_header,
            verify=False
        )
        logger.info(res.json())
        return res.json()["items"]
    except Exception as e:
        return result_error(e)


def get_admin_header():
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        params = {
            "email": settings.CMP_INFO.CMP_ID,
            "password": settings.CMP_INFO.CMP_PASS
        }
        res = requests.post(
            url=f"{url}/adminLogin",
            params=params,
            verify=False
        )
        logger.info(res.json())
        access_token = res.json()["access_token"]
        header = {'X-HEADER-TOKEN': access_token}
        return header
    except Exception as e:
        raise e


def result_error(e):
    logger.error(e, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"result": 0, "errorMessage": str(e)}
    )
