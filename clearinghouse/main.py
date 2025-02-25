from fastapi import FastAPI

from .dependencies import SchwabService, EnvSettings
from .routers import orders, status

# Global instance to be shared across all routers
env_settings = EnvSettings()
schwab_service = SchwabService(env_settings)

def get_global_schwab_service() -> SchwabService:
    return schwab_service

app = FastAPI()
app.include_router(orders.create_order_endpoints())
app.include_router(status.create_status_endpoints())

@app.get("/")
async def root():
    return {"status": app.state}
