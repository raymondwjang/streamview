from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from streamview.config import CONFIG
from streamview.runner import Runner


frontend_dir = Path(__file__).parent / "frontend"
templates = Jinja2Templates(directory=frontend_dir / "templates")

runner = Runner()


@asynccontextmanager
async def lifespan(app: FastAPI):
    runner.setup()
    yield


app = FastAPI(lifespan=lifespan)

app.mount(
    path="/static", app=StaticFiles(directory=frontend_dir / "static"), name="static"
)


@app.get("/")
async def get(request: Request):
    """Serve the dashboard page"""
    return templates.TemplateResponse(
        "index.html", {"request": request, "config": CONFIG}
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connection and run streamers"""
    await websocket.accept()
    await runner.run_streamers(websocket)


@app.get("/stream/{filename}")
async def stream(filename: str):
    """Serve HLS stream files"""
    stream_path = runner.temp_dir / filename
    if stream_path.exists():
        return FileResponse(str(stream_path))
    return {"error": "Stream not found"}
