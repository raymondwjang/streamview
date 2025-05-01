import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from tempfile import mkdtemp

import numpy as np

from streamview.config import load_config
from streamview.nodes import FrameStreamer, MetricStreamer
from streamview.socket_manager import ConnectionManager

config = load_config()


@dataclass
class Runner:
    width: int = config["video"]["width"]
    height: int = config["video"]["height"]
    frame_rate: int = config["video"]["frameRate"]
    temp_dir: Path | None = None

    def setup(self):
        """Initialize static files and templates"""

        self.temp_dir = Path(mkdtemp())
        self.temp_dir.mkdir(exist_ok=True, parents=True)

    def frame(self) -> np.ndarray:
        """Generate a single frame"""
        t = time.time()
        frame = np.ones((self.width, self.height), dtype=np.uint8) * int(
            255 * (np.sin(t) + 1) / 2
        )
        return frame

    async def run_streamers(self, manager: ConnectionManager):
        """Run both frame and metric streamers"""
        # Initialize streamers (nodes)
        frame_streamer = FrameStreamer(
            temp_dir=self.temp_dir,
            width=self.width,
            height=self.height,
            frame_rate=self.frame_rate,
        )
        metric_streamer = MetricStreamer(manager)

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
