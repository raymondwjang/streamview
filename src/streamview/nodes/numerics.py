import random
from dataclasses import dataclass
from logging import getLogger
from fastapi import WebSocket, WebSocketDisconnect

logger = getLogger(__file__)


@dataclass
class MetricStreamer:
    websocket: WebSocket

    async def process(self, idx: int):
        try:
            await self.websocket.send_json(
                {"index": idx, "value": int(random.random() * 10000) / 100}
            )
        # https://fastapi.tiangolo.com/reference/websockets/#fastapi.WebSocket.send
        except Exception as e:
            print(e)
            pass
