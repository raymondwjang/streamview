import random
from dataclasses import dataclass
from logging import getLogger

from fastapi import WebSocketDisconnect

from streamview.app import ConnectionManager

logger = getLogger(__file__)


@dataclass
class MetricStreamer:
    manager: ConnectionManager

    async def process(self, idx: int):
        try:
            for websocket in self.manager.active_connections:
                await self.manager.send_json(
                    {"index": idx, "value": int(random.random() * 10000) / 100},
                    websocket,
                )
        # https://fastapi.tiangolo.com/reference/websockets/#fastapi.WebSocket.send
        except WebSocketDisconnect:
            self.manager.disconnect(websocket)
            pass
