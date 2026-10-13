import os
from datetime import datetime, timedelta, timezone

import jwt

from app.auth_dependencies import SECRET_KEY, ALGORITHM

assert SECRET_KEY, "Secret key is missing"

now = datetime.now(timezone.utc)

valid_payload = {
    "sub": "1",
    "business_id": 1,
    "iat": now,
    "exp": now + timedelta(minutes=5),
}

valid_token = jwt.encode(
    valid_payload,
    SECRET_KEY,
    algorithm=ALGORITHM,
)

decoded = jwt.decode(
    valid_token,
    SECRET_KEY,
    algorithms=[ALGORITHM],
)

assert decoded["sub"] == "1"
assert decoded["business_id"] == 1

try:
    jwt.decode(
        valid_token + "invalid",
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )
    raise AssertionError("Invalid token was unexpectedly accepted")
except jwt.InvalidTokenError:
    pass

print("Valid JWT accepted; tampered JWT rejected")