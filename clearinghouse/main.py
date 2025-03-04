import os

from fastapi import FastAPI

from .dependencies import SchwabService, LocalSchwabService, EnvSettings
from .routers import orders, status

# Global instance to be shared across all routers
env_settings = EnvSettings()
schwab_service = SchwabService(env_settings) if not env_settings.schwab_local_mode else LocalSchwabService()

def get_global_schwab_service() -> SchwabService:
    return schwab_service

app = FastAPI()
app.include_router(orders.create_order_endpoints(get_global_schwab_service()))
app.include_router(status.create_status_endpoints(get_global_schwab_service()))

@app.get("/")
async def root():
    # TODO: return something useful here
    return {"status": "healthy"}
