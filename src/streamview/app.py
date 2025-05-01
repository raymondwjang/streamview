import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from streamview.config import load_config  # isort:skip
from streamview.socket_manager import ConnectionManager  # isort:skip
from streamview.runner import Runner  # isort:skip

frontend_dir = Path(__file__).parents[2] / "frontend"
templates = Jinja2Templates(directory=frontend_dir / "templates")

config = load_config()
runner = Runner()


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    runner.setup()

    # Start the streamers in the background
    # You'll need to modify runner.run_streamers to not block the event loop
    # or run it in a background task
    asyncio.create_task(runner.run_streamers(manager))

    yield


app = FastAPI(lifespan=lifespan)

app.mount(path="/dist", app=StaticFiles(directory=frontend_dir / "dist"), name="dist")


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
    # Keep the connection alive
    try:
        # You might need to implement some kind of waiting mechanism here
        # to keep the connection open until the client disconnects
        while True:
            # Wait for messages from the client if needed
            await websocket.receive_text()
            # Process the received data if needed
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(websocket)


@app.get("/stream/{filename}")
async def stream(filename: str):
    """Serve HLS stream files"""
    stream_path = runner.temp_dir / filename
    if stream_path.exists():
        return FileResponse(str(stream_path))
    return {"AppStreamError": "Stream not found"}
