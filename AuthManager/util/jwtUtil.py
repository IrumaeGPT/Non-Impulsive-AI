from datetime import datetime, timedelta
from jose import JWTError, jwt
import sys
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Request, status

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.abspath(os.path.join(current_directory, "../../episodeManager/.env"))
load_dotenv(dotenv_path=dotenv_path)

SECRET_KEY = os.getenv("secretKey")
ALGORITHM = os.getenv("algorithm")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("expireTime"))
ISSUER = os.getenv("issuer")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is missing"
        )

    try:
        prefix, token = token.split(" ")
        if prefix != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token prefix"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("name")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain username"
            )
            
        issuer = payload.get("iss")
        if not issuer == ISSUER:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰 공급자 불일치지롱"
            )
        return "OK"
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )