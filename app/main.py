from fastapi import FastAPI
from .routes import notifications

app = FastAPI()
app.include_router(notifications.router)


@app.get('/')
async def start_fun():
    return {"message": "Successfully connected"}