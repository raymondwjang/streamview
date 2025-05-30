import random
from dataclasses import dataclass
from logging import getLogger

from fastapi import WebSocketDisconnect

from streamview.socket_manager import ConnectionManager

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
            print(f"Num Connections: {len(self.manager.active_connections)}")
            if websocket in self.manager.active_connections:
                self.manager.disconnect(websocket)
            pass
