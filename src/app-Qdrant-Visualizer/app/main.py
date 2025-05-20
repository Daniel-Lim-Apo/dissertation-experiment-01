from app.dash_app import create_dash_app
import uvicorn
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

app = FastAPI()
dash_app = create_dash_app()
app.mount("/", WSGIMiddleware(dash_app))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
