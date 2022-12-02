from fastapi.logger import logger
from typing import Union
import asyncssh

from ServiceUtils.crypto import AESCipher
from ServiceUtils.exceptions import InvalidUserInfo
from ApiService.ApiServiceConfig import config
from .schemas import LdapUserInfo


async def ldap_auth(id: str, pwd: str) -> bool:
    output = await run_cmd(
        config.ldap_info["host"],
        int(config.ldap_info["port"]),
        config.ldap_info["user"],
        config.ldap_info["password"],
        f"AUTH {id} {pwd}",
    )
    output = output.split(" ", 1)
    if output[0] == "false":
        raise InvalidUserInfo(output[1])
    return True


async def ldap_info(id: str) -> LdapUserInfo:
    output = await run_cmd(
        config.ldap_info["host"],
        int(config.ldap_info["port"]),
        config.ldap_info["user"],
        config.ldap_info["password"],
        f"UINFO {id}",
    )
    if type(output) == str:
        raise InvalidUserInfo(output.split(" ", 1)[1])
    return LdapUserInfo(**output)


async def run_cmd(host: str, port: int, username: str, password: str, cmd: str) -> Union[str, dict]:
    logger.info("remote call :: " + cmd)
    # async with asyncssh.connect(host=host, port=port,
    #                             username=username, password=password, known_hosts=None) as conn:
    #     logger.info(f'Run Cmd : {cmd}')
    #     result = await conn.run(cmd, check=True)
    #     logger.info(f'Command Result : {result.stdout}')
    # return result.stdout
    import random

    if "AUTH" in cmd:
        return random.choice(
            [
                "true",
                "false [SYS_FAIL] AuthenticationException: [comment: 인증에 실패했습니다., data 0005",
            ]
        )
    elif "UINFO" in cmd:
        try:
            return {
                "12345678": {
                    "userName": "홍길동",
                    "deptCD": 481253,
                    "mobile": "010-6290-5249",
                    "deptName": "",
                    "agencyCD": 481226,
                    "agencyName": "",
                    "positionCD": "",
                    "positionName": "AI/BigData사업본부...",
                    "companyName": "KT협력사",
                    "email": "9132824@ktfriends.com",
                },
                "11181059": {
                    "userName": "고길동",
                    "deptCD": 481253,
                    "mobile": "010-6290-5249",
                    "deptName": "",
                    "agencyCD": 481226,
                    "agencyName": "",
                    "positionCD": "",
                    "positionName": "AI/BigData사업본부...",
                    "companyName": "KT협력사",
                    "email": "9132824@ktfriends.com",
                },
                "11181344": {
                    "userName": "나길동",
                    "deptCD": 481253,
                    "mobile": "010-6290-5249",
                    "deptName": "",
                    "agencyCD": 481226,
                    "agencyName": "",
                    "positionCD": "",
                    "positionName": "AI/BigData사업본부...",
                    "companyName": "KT협력사",
                    "email": "9132824@ktfriends.com",
                },
            }[cmd.split(" ")[1]]
        except Exception:
            return "false CredentialException: [comment: 존재하지 않는 사용자 계정입니다., data 0001]"


def knime_encrypt(data: str, key: str):
    return AESCipher(key).encrypt(data).decode()
