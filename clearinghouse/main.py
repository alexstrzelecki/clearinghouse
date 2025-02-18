from fastapi import FastAPI

from .dependencies import SchwabService
from .routers import orders, admin, status

# Global instance to be shared across all routers
schwab_service = SchwabService()
app = FastAPI()
app.include_router(orders.create_order_endpoints(schwab_service))
app.include_router(admin.create_admin_endpoints(schwab_service))
app.include_router(status.create_status_endpoints(schwab_service))

@app.get("/")
async def root():
    return {"healthy": True}
