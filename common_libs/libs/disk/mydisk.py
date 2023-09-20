from typing import Dict
import logging
import aiohttp
import urllib.parse

logger = logging.getLogger()


class MydiskManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, base_url: str = None) -> None:
        self.base_url = base_url

    def set_url(self, base_url):
        self.base_url = base_url

    async def _request_to_mydisk(self, api_url, method, headers, **kwargs):
        """_summary_

        Args:
            api_url (_type_): _description_
            method (_type_): _description_
            headers (_type_): _description_

        Returns:
            _type_: _description_
        """
        data = urllib.parse.urlencode(kwargs)
        print(data)
        async with aiohttp.ClientSession() as session:
            async with session.request(url=api_url, method=method, headers=headers, data=data) as response:
                try:
                    ret = await response.json()
                except Exception:
                    ret = await response.read()
                return {"status_code": response.status, "data": ret}

    async def generate_admin_token(self, **kwargs) -> Dict:
        """
            관리자계정에 대한 토큰 발급

        Args:
            username (str):
            password (str):
            scope (str): upload profile admin list
            grant_type (str) : password
            client_id (str) :
            client_secret (str)
            curl -X POST -d "username=superuser&password=35ldxxhbd1&scope=upload profile admin list&client_id=86e9aaff5afc7d7828035500e11cb48c&client_secret=lfb5RQK9SH3GcRqGgq0QcLlW5mJf0JDBNkrn1729&redirect_uri=http://mydisk.bigdata-car.kr:8895&grant_type=password"
             http://mydisk.bigdata-car.kr:8895/oauth2/token/

        Returns:
            Dict: _description_
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return await self._request_to_mydisk(
            api_url=f"{self.base_url}/oauth2/token/",
            method="POST",
            headers=headers,
            grant_type="password",
            **kwargs,
        )
    async def user_info_detail(self, token, realm, user_id):
        headers = {"Authorization": "bearer " + token}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/admin/realms/{realm}/users/{user_id}", method="GET", headers=headers
        )


mydisk = MydiskManager()
