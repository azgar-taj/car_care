from fastapi.responses import JSONResponse
from global_helpers import setup_logger, AuthenticationDatabaseConnector
from global_helpers.models import User, UserResponse
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_jwt_auth import AuthJWT

class JwtSettings(BaseModel):
    authjwt_secret_key: str = "secret"


class AuthService:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.app = FastAPI()
        self.app.exception_handler(AuthJWTException)(self.authjwt_exception_handler)

        self.app.post('/get_token')(self.login)
        self.app.get('/user_metadata')(self.user)
        self.app.post('/refresh')(self.refresh)
        self.app.post('/register')(self.register_user)

    @AuthJWT.load_config
    def get_auth_settings():
        return JwtSettings()

    def authjwt_exception_handler(self, request: Request, exc: AuthJWTException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    def get_server(self):
        return self.app

    def login(self, user: User, Authorize: AuthJWT = Depends()):
        if not AuthenticationDatabaseConnector().get_user(user.username):
            raise HTTPException(status_code=401, detail="Bad username or password")
        access_token = Authorize.create_access_token(subject=user.username)
        return {"access_token": access_token}

    def user(self, Authorize: AuthJWT = Depends()):
        try:
            Authorize.jwt_required()
            current_user = Authorize.get_jwt_subject()
        except AuthJWTException:
            current_user = None
        return {"user": current_user}

    def refresh(self, Authorize: AuthJWT = Depends()):
        Authorize.jwt_refresh_token_required()

        current_user = Authorize.get_jwt_subject()
        new_access_token = Authorize.create_access_token(subject=current_user)
        return {"access_token": new_access_token}

    def register_user(self, user: User):
        user_id = None
        try:
            user_id = AuthenticationDatabaseConnector().add_user(user)
            self.logger.info(f'Type of user_id: {type(user_id)}')
            if not user_id:
                return UserResponse(success=False, message="User already exists", userId=user_id, status="active")
            self.logger.info(f"User {user.username} added successfully, user_id: {user_id}")
        except Exception as e:
            return UserResponse(success=False, message="Error adding user", userId=user_id, status="Inactive")
        return UserResponse(success=True, message="User added successfully", userId=user_id, status="Active")

app = AuthService().get_server()