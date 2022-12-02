import hashlib
import time
import threading
import random
from fastapi.logger import logger


class OTP:
    otp_db = dict()

    @classmethod
    def get_hash(cls, data) -> str:
        return hashlib.sha256(str(data).encode()).hexdigest()

    @classmethod
    def create(cls):
        return random.randrange(1000000)

    @classmethod
    def add_otp(cls, id: str, otp: int):
        def del_expired_otp(otp_db, id):
            time.sleep(180)
            del otp_db[id]
            logger.info(f"expired otp :: {id}")

        hash = cls.get_hash(otp)
        cls.otp_db[id] = hash
        logger.info(f"otp_store :: {cls.otp_db}")
        threading.Thread(
            daemon=True,
            target=del_expired_otp,
            args=(
                cls.otp_db,
                id,
            ),
        ).start()

    @classmethod
    def check_otp(cls, id: str, otp: int) -> bool:
        hash = cls.get_hash(otp)
        if id in cls.otp_db and cls.otp_db[id] == hash:
            del cls.otp_db[id]
            return True
        return False
