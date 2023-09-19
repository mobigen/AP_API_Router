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

    async def _request_to_keycloak(self, api_url, method, headers, **kwargs):
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
            grant_type (str): refresh_token or password

        Returns:
            Dict: _description_
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/realms/master/protocol/openid-connect/token",
            client_id="admin-cli",
            method="POST",
            headers=headers,
            **kwargs,
        )

    async def generate_normal_token(self, realm, **kwargs) -> Dict:
        """
            일반회원의 토큰 발급

        Args:
            realm (_type_): keycloak 인증 그룹
            grant_type (str): 인증방법('password', 'refresh_token')
            username (str): 계정명
            password (str): 패스워드
            refresh_token (str): 리프레시 토큰
            client_id (str): keycloak client_id
            client_secret (str): keycloak_client_id에 대응하는 secret key

        Returns:
            Dict: _description_
        """

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/realms/{realm}/protocol/openid-connect/token",
            method="POST",
            headers=headers,
            **kwargs,
        )

    async def token_info(self, realm, **kwargs) -> Dict:
        """_summary_

        Args:
            realm (_type_): _description_

        Returns:
            Dict: _description_
        """

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/realms/{realm}/protocol/openid-connect/token/introspect",
            method="POST",
            headers=headers,
            **kwargs,
        )

    async def create_user(self, token, realm, **kwargs):
        headers = {"Content-Type": "application/json", "Authorization": "bearer " + token}
        async with aiohttp.ClientSession() as session:
            async with session.request(
                url=f"{self.base_url}/admin/realms/{realm}/users",
                method="POST",
                headers=headers,
                json=kwargs,
            ) as response:
                return {"status_code": response.status, "data": await response.read()}

    async def delete_user(self, token, realm, user_id):
        headers = {"Authorization": "bearer " + token}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/admin/realms/{realm}/users/{user_id}", method="DELETE", headers=headers
        )

    async def get_user_list(self, token, realm):
        headers = {"Authorization": "bearer " + token}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/admin/realms/{realm}/users", method="GET", headers=headers
        )

    async def user_info(self, token, realm):
        headers = {"Authorization": "bearer " + token}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/realms/{realm}/protocol/openid-connect/userinfo", method="GET", headers=headers
        )

    async def user_info_detail(self, token, realm, user_id):
        headers = {"Authorization": "bearer " + token}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/admin/realms/{realm}/users/{user_id}", method="GET", headers=headers
        )

    async def alter_user(self, token, realm, sub, **kwargs):
        headers = {"Content-Type": "application/json", "Authorization": "bearer " + token}

        async with aiohttp.ClientSession() as session:
            async with session.request(
                url=f"{self.base_url}/admin/realms/{realm}/users/{sub}",
                method="PUT",
                headers=headers,
                json=kwargs,
            ) as response:
                return {"status_code": response.status, "data": await response.read()}

    async def check_user_session(self, token, realm, user_id):
        headers = {"Authorization": "bearer " + token}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/admin/realms/{realm}/users/{user_id}/sessions", method="GET", headers=headers
        )

    async def logout(self, realm, **kwargs):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/realms/{realm}/protocol/openid-connect/logout",
            method="POST",
            headers=headers,
            **kwargs,
        )

    async def refresh_token(self, realm, **kwargs):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/realms/{realm}/protocol/openid-connect/token",
            method="POST",
            headers=headers,
            **kwargs,
        )

    async def get_query(self, token, realm, query):
        headers = {"Authorization": "bearer " + token}
        return await self._request_to_keycloak(
            api_url=f"{self.base_url}/admin/realms/{realm}/users?{query}", method="GET", headers=headers
        )

    async def social_link(self, token, realm, sub, **kwargs):
        headers = {"Content-Type": "application/json", "Authorization": "bearer " + token}
        social_type = kwargs.get("social_type")

        params = {
            "identityProvider": social_type,
            "userId": kwargs.get("social_id"),
            "userName": kwargs.get("social_email")
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                    url=f"{self.base_url}/admin/realms/{realm}/users/{sub}/federated-identity/{social_type}",
                    method="POST",
                    headers=headers,
                    json=params,
            ) as response:
                return {"status_code": response.status, "data": await response.read()}


mydisk = MydiskManager()
