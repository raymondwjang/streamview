import random
from dataclasses import dataclass

from fastapi import WebSocket


@dataclass
class MetricStreamer:
    websocket: WebSocket

    async def process(self, idx: int):
        await self.websocket.send_json(
            {"index": idx, "value": int(random.random() * 10000) / 100}
        )
