from fastapi import Depends, FastAPI

from .dependencies import get_schwab_token

app = FastAPI(dependencies=[Depends(get_schwab_token)])

@app.get("/")
async def root():
    return {"a": "b"}
