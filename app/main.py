from __future__ import annotations

import asyncio
import math
import os
import random
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .monitor import DoorMonitor

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
API_KEY = os.getenv("DOORSENSE_API_KEY", "doorsense-local-demo")
monitor = DoorMonitor()
subscribers: set[WebSocket] = set()
simulator_enabled = True


class SimulateRequest(BaseModel):
    distance_cm: float = Field(ge=-1, le=500)


async def broadcast(payload: dict[str, object]) -> None:
    disconnected: list[WebSocket] = []
    for websocket in subscribers:
        try:
            await websocket.send_json(payload)
        except Exception:
            disconnected.append(websocket)
    for websocket in disconnected:
        subscribers.discard(websocket)


async def simulator_loop() -> None:
    tick = 0
    while True:
        if simulator_enabled:
            # Smoothly moves between closed, ajar, and open states for a useful local demo.
            distance = 25 + 22 * math.sin(tick / 9) + random.uniform(-1.4, 1.4)
            reading = monitor.update(max(4.0, distance), source="simulator")
            await broadcast({"type": "reading", **reading.to_dict(), "summary": monitor.snapshot()})
            tick += 1
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(simulator_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="DoorSense API", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def require_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="A valid X-API-Key header is required.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "doorsense"}


@app.get("/api/status")
def status() -> dict[str, object]:
    return monitor.snapshot()


@app.get("/api/events")
def events() -> list[dict[str, object]]:
    return monitor.events()


@app.post("/api/simulate", dependencies=[Depends(require_api_key)])
async def simulate(payload: SimulateRequest) -> dict[str, object]:
    reading = monitor.update(payload.distance_cm, source="manual")
    message = {"type": "reading", **reading.to_dict(), "summary": monitor.snapshot()}
    await broadcast(message)
    return message


@app.post("/api/events/{event_id}/acknowledge", dependencies=[Depends(require_api_key)])
def acknowledge(event_id: int) -> dict[str, object]:
    if not monitor.acknowledge(event_id):
        raise HTTPException(status_code=404, detail="Event not found.")
    return {"acknowledged": True, "event_id": event_id}


@app.websocket("/ws")
async def websocket_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    subscribers.add(websocket)
    try:
        await websocket.send_json({"type": "snapshot", **monitor.snapshot()})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        subscribers.discard(websocket)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
