from fastapi.logger import logger
import asyncssh


async def run_cmd(host: str, port: int, username: str, password: str, cmd: str) -> str:
    # async with asyncssh.connect(host=host, port=port,
    #                             username=username, password=password, known_hosts=None) as conn:
    #     logger.info(f'Run Cmd : {cmd}')
    #     result = await conn.run(cmd, check=True)
    #     logger.info(f'Command Result : {result.stdout}')
    # return result.stdout
    import random

    logger.info("remote call :: " + cmd)
    return random.choice(
        [
            "true",
            "false [SYS_FAIL] AuthenticationException: [comment: 인증에 실패했습니다., data 0005",
        ]
    )
