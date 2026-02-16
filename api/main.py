from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from redis import Redis
import os
import json
import time
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="AgentOps Hub API")

# ✅ CORS (so Next.js at :3000 can call FastAPI at :8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

STREAM_KEY = "agent_events"


class CreateRunRequest(BaseModel):
    goal: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/runs")
def create_run(req: CreateRunRequest):
    run_id = str(uuid4())

    event = {
        "run_id": run_id,
        "type": "RUN_STARTED",
        "message": req.goal,  # store goal in message
    }
    redis_client.xadd(STREAM_KEY, event)

    return {"run_id": run_id}


@app.get("/runs/{run_id}/events")
def stream_run_events(run_id: str):
    def event_generator():
        last_id = "0"  # ✅ from beginning (works even after rebuild)
        while True:
            resp = redis_client.xread(streams={STREAM_KEY: last_id}, count=50, block=5000)

            if not resp:
                yield {"event": "heartbeat", "data": "ping"}
                continue

            for _, messages in resp:
                for msg_id, fields in messages:
                    last_id = msg_id

                    if fields.get("run_id") != run_id:
                        continue

                    event_type = fields.get("type", "event")
                    yield {"event": event_type, "data": json.dumps(fields)}

                    if event_type in ("RUN_COMPLETED", "RUN_FAILED"):
                        return

            time.sleep(0.05)

    return EventSourceResponse(event_generator())
