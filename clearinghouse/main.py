from fastapi import FastAPI

from .dependencies import SchwabService, EnvSettings
from .routers import orders, status

# Global instance to be shared across all routers
env_settings = EnvSettings()
schwab_service = SchwabService(env_settings)
app = FastAPI()
app.include_router(orders.create_order_endpoints(schwab_service))
app.include_router(status.create_status_endpoints(schwab_service))

@app.get("/")
async def root():
    return {"healthy": env_settings.schwab_app_key}
