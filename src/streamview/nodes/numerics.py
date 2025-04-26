import random
from fastapi import WebSocket
from dataclasses import dataclass


@dataclass
class MetricStreamer:
    websocket: WebSocket

    async def process(self, idx: int):
        await self.websocket.send_json(
            {"index": idx, "value": int(random.random() * 10000) / 100}
        )
