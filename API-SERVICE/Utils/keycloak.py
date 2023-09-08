from typing import Any, Dict, List
import logging
import aiohttp
import urllib.parse

logger = logging.getLogger()


class KeycloakManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, base_url: str) -> None:
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

    async def alter_user(self, token, realm, user_id, **kwargs):
        print(f"kwargs :: {kwargs}")
        headers = {"Content-Type": "application/json", "Authorization": "bearer " + token}
        async with aiohttp.ClientSession() as session:
            async with session.request(
                url=f"{self.base_url}/admin/realms/{realm}/users/{user_id}",
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


if __name__ == "__main__":
    import asyncio

    manager = KeycloakManager("http://192.168.101.44:8080")
    d = asyncio.run(manager.generate_admin_token(username="admin", password="zxcv1234!", grant_type="password"))
    print(f"admin_token :: {d}")
    admin_access_token = d.get("data").get("access_token")
    admin_refresh_token = d.get("data").get("refresh_token")
    data = {
        "username": "swyang",
        "firstName": "seokwoo",
        "lastName": "yang",
        "email": "sw@mobigen.com",
        "emailVerified": False,
        "enabled": True,
        "credentials": [{"value": "zxcv1234!"}],
        "attributes": {"phoneNumber": "010-1234-5678", "gender": "male"},
    }
    r = asyncio.run(
        manager.create_user(
            realm="kadap",
            token=admin_access_token,
            **data,
        )
    )
    d = asyncio.run(
        manager.generate_normal_token(
            realm="kadap",
            username="swyang",
            password="zxcv1234!",
            grant_type="password",
            client_id="uyuni",
            client_secret="04esVekOjeJZKLHBkgsCQxpbwda41aKW",
        )
    )
    print(f"normal token :: {d}")
    normal_access_token = d.get("data").get("access_token")
    normal_refresh_token = d.get("data").get("refresh_token")
    r = asyncio.run(
        manager.token_info(
            realm="kadap",
            token=normal_access_token,
            client_id="uyuni",
            client_secret="04esVekOjeJZKLHBkgsCQxpbwda41aKW",
        )
    )
    print(f"token info :: {r}")
    r = asyncio.run(manager.user_info(realm="kadap", token=normal_access_token))
    print(f"user info :: {r}")
    user_id = r.get("data").get("sub")
    r = asyncio.run(manager.user_info_detail(token=admin_access_token, realm="kadap", user_id=user_id))
    print(f"detail :: {r}")
    data = {
        "firstName": "seokwoo",
        "lastName": "yang",
        "email": "sw@mobigen.com",
        "emailVerified": False,
        "credentials": [{"value": "zxcv1234!"}],
        "attributes": {"phoneNumber": "010-1111-1234", "gender": "male"},
    }
    r = asyncio.run(manager.alter_user(token=admin_access_token, realm="kadap", user_id=user_id, **data))
    print(f"alter {r}")
    r = asyncio.run(manager.check_user_session(token=admin_access_token, realm="kadap", user_id=user_id))
    print(f"check :: {r}")
    r = asyncio.run(
        manager.logout(
            realm="kadap",
            grant_type="password",
            refresh_token=normal_refresh_token,
            client_id="uyuni",
            client_secret="04esVekOjeJZKLHBkgsCQxpbwda41aKW",
        )
    )
    print(f"logout :: {r}")
    r = asyncio.run(manager.delete_user(token=admin_access_token, realm="kadap", user_id=user_id))
    print(f"delete :: {r}")
    r = asyncio.run(manager.get_user_list(token=admin_access_token, realm="kadap"))
    print(f"list :: {r}")
