from datetime import datetime, timedelta

import jwt


def create_access_token(data: dict = None, expires_delta: int = 60, secret_key=None, algorithm=None, exclude_list=[]):
    to_encode = data.copy()
    for k in exclude_list:
        to_encode.pop(k)
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt
