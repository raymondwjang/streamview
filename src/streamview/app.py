from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from streamview.config import load_config
from streamview.runner import Runner
from streamview.socket_manager import ConnectionManager

frontend_dir = Path(__file__).parents[2] / "frontend"
templates = Jinja2Templates(directory=frontend_dir / "templates")

config = load_config()
runner = Runner()


manager = ConnectionManager()


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
        "index.html", {"request": request, "config": config}
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connection and run streamers"""
    await manager.connect(websocket)
    await runner.run_streamers(
        manager
    )  # --> this shouldn't be here. runner should just be running, and websocket (manager) simply connects to it.


@app.get("/stream/{filename}")
async def stream(filename: str):
    """Serve HLS stream files"""
    stream_path = runner.temp_dir / filename
    if stream_path.exists():
        return FileResponse(str(stream_path))
    return {"AppStreamError": "Stream not found"}
