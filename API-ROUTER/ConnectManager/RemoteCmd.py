import paramiko
from fastapi.logger import logger


class RemoteCmd:
    def __init__(self, ip: str, port: int, id: str, password: str) -> None:
        self.ssh = self.remote_connect(ip, port, id, password)

    def remote_connect(self, ip: str, port: int, id: str, password: str) -> paramiko.SSHClient:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=id, password=password)
        return ssh

    def cmd_exec(self, cmd: str) -> str:
        _, stdout, _ = self.ssh.exec_command(cmd)
        lines = stdout.readlines()
        resultData = ''.join(lines)

        return resultData

    def __del__(self):
        self.ssh.close()
