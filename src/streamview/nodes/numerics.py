import time
import random
from fastapi import WebSocket
from dataclasses import dataclass


@dataclass
class MetricStreamer:
    websocket: WebSocket

    async def process(self):
        await self.websocket.send_json({"time": time.time(), "value": random.randint(0, 100)})
