from database_connector import AuthenticationDatabaseConnector, CarServicesDatabase
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from car_service_contracts.auth_service_contracts import CarServicesContracts
from car_service_contracts.models import Service
from global_helpers import setup_logger
from fastapi.responses import JSONResponse
from bson import json_util
import json

class JwtSettings(BaseModel):
    authjwt_secret_key: str = "secret"

@AuthJWT.load_config
def get_auth_settings():
    return JwtSettings()

class CarServicesProvider:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.app = FastAPI()
        self.app.exception_handler(AuthJWTException)(self.authjwt_exception_handler)

        # Register routes
        self.app.post(f'/{CarServicesContracts.SERVICE_URI}')(self.add_service)
        self.app.get(f'/{CarServicesContracts.SERVICES_URI}')(self.get_services)
        self.app.delete(f'/{CarServicesContracts.SERVICE_URI}')(self.delete_service)
        self.app.put(f'/{CarServicesContracts.SERVICE_URI}')(self.update_service)

    def authjwt_exception_handler(self, request: Request, exc: AuthJWTException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    def get_server(self):
        return self.app

    def add_service(self, service: Service, Authorize: AuthJWT = Depends()):
        # Check if the user is an admin
        if not AuthenticationDatabaseConnector().is_admin(Authorize.get_jwt_subject()):
            raise HTTPException(status_code=401, detail="Unauthorized")
        # Add the service
        service_id = CarServicesDatabase().add_service(service)
        services_json = json_util.dumps(service_id)
        return {"service_id": json.loads(services_json), "message": "Service added", "success": True}

    def get_services(self):
        services = CarServicesDatabase().get_services()
        services_json = json_util.dumps(services)
        return {"services": json.loads(services_json), "success": True}

    def delete_service(self, service_id: str, Authorize: AuthJWT = Depends()):
        # Check if the user is an admin
        if not AuthenticationDatabaseConnector().is_admin(Authorize.get_jwt_subject()):
            raise HTTPException(status_code=401, detail="Unauthorized")
        # Delete the service
        CarServicesDatabase().delete_service(service_id)
        return {"message": "Service deleted", "success": True}

    def update_service(self, service_id: str, service: Service, Authorize: AuthJWT = Depends()):
        # Check if the user is an admin
        if not AuthenticationDatabaseConnector().is_admin(Authorize.get_jwt_subject()):
            raise HTTPException(status_code=401, detail="Unauthorized")
        # Update the service
        CarServicesDatabase().update_service(service_id, service)
        return {"message": "Service updated", "success": True}

app = CarServicesProvider().get_server()