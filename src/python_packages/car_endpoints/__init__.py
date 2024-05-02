from fastapi.responses import JSONResponse
from global_helpers import setup_logger, DatabaseConnector, DatabaseType
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_jwt_auth import AuthJWT

class User(BaseModel):
    username: str
    password: str

logger = setup_logger()

app = FastAPI()

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.post('/get_token')
def login(user: User, Authorize: AuthJWT = Depends()):
    logger.info(f"Users are {DatabaseConnector(DatabaseType.USER).get_users()}")
    if user.username not in DatabaseConnector(DatabaseType.USER).get_users():
        raise HTTPException(status_code=401,detail="Bad username or password")

    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


@app.get('/user_metadata')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}

@app.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}
