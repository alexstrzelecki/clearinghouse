from fastapi import FastAPI

from .dependencies import SchwabService, LocalSchwabService, EnvSettings, SafetySettings
from .routers import orders, status


env_settings = None
safety_settings = None
schwab_service = None

def initialize_services():
    global env_settings, safety_settings, schwab_service
    if env_settings is None or safety_settings is None or schwab_service is None:
        env_settings = EnvSettings()
        safety_settings = SafetySettings()
        schwab_service = SchwabService(env_settings) if not env_settings.schwab_local_mode else LocalSchwabService()

def get_global_schwab_service() -> SchwabService:
    if schwab_service is None:
        initialize_services()
    return schwab_service

app = FastAPI()
app.include_router(orders.create_order_endpoints(get_global_schwab_service()))
app.include_router(status.create_status_endpoints(get_global_schwab_service()))

@app.get("/")
async def root():
    # TODO: return something useful here
    return {"status": "healthy"}
