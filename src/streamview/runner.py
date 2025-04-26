import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import mkdtemp

import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from streamview.nodes import FrameStreamer, MetricStreamer


@dataclass
class Runner:
    width: int = 480
    height: int = 320
    frame_rate: int = 30
    temp_dir: Path | None = None
    templates: Jinja2Templates | None = None

    def setup(self):
        """Initialize static files and templates"""
        frontend_dir = Path(__file__).parent / "frontend"
        self.templates = Jinja2Templates(directory=frontend_dir)

        self.temp_dir = Path(mkdtemp())
        self.temp_dir.mkdir(exist_ok=True, parents=True)

    def frame(self) -> np.ndarray:
        """Generate a single frame"""
        t = time.time()
        frame = np.ones((self.width, self.height), dtype=np.uint8) * int(
            255 * (np.sin(t) + 1) / 2
        )
        return frame

    async def run_streamers(self, websocket: WebSocket):
        """Run both frame and metric streamers"""
        # Initialize streamers (nodes)
        frame_streamer = FrameStreamer(
            temp_dir=self.temp_dir,
            width=self.width,
            height=self.height,
            frame_rate=self.frame_rate,
        )
        metric_streamer = MetricStreamer(websocket)

        idx = 0
        try:
            while True:
                frame = self.frame()
                frame_streamer.process(frame)

                # Stream metric
                await metric_streamer.process(idx)

                # Control frame rate
                await asyncio.sleep(1 / self.frame_rate)
                idx += 1
        except Exception as e:
            print(f"RunnerError: {e}")
        finally:
            frame_streamer.close()


# Create a runner instance
runner = Runner()


@asynccontextmanager
async def lifespan(app: FastAPI):
    runner.setup()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get(request: Request):
    """Serve the dashboard page"""
    if runner.templates is None:
        raise RuntimeError("Templates not set up")
    return runner.templates.TemplateResponse("index.html", {"request": request})


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
