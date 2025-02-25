import os

from fastapi import FastAPI

from .dependencies import SchwabService, LocalSchwabService, EnvSettings
from .routers import orders, status

# Global instance to be shared across all routers
is_local_mode = os.environ.get("SCHWAB_RUN_MODE", "").lower() == "local"
env_settings = EnvSettings()
schwab_service = SchwabService(env_settings) if not is_local_mode else LocalSchwabService()

def get_global_schwab_service() -> SchwabService:
    return schwab_service

app = FastAPI()
app.include_router(orders.create_order_endpoints())
app.include_router(status.create_status_endpoints(get_global_schwab_service()))

@app.get("/")
async def root():
    return {"status": app.state}
