"""Outbox relay: publish unpublished events at-least-once to EventBridge."""
import asyncio
import json

import boto3
from sqlalchemy import text

BATCH = 100
SELECT = text("""
    SELECT id, event_type, payload, created_at
    FROM outbox
    WHERE published_at IS NULL
    ORDER BY created_at
    LIMIT :n
    FOR UPDATE SKIP LOCKED
""")
MARK = text("UPDATE outbox SET published_at = now() WHERE id = ANY(:ids)")


async def relay_once(session_factory, bus_name: str) -> int:
    events = boto3.client("events")
    async with session_factory() as s, s.begin():
        rows = (await s.execute(SELECT, {"n": BATCH})).all()
        if not rows:
            return 0
        entries = [{
            "Source": "medilens.api",
            "DetailType": r.event_type,
            "Detail": json.dumps({"eventId": str(r.id), "occurredAt": r.created_at.isoformat(), **r.payload}),
            "EventBusName": bus_name,
        } for r in rows]
        for i in range(0, len(entries), 10):                     # PutEvents max 10 entries
            resp = events.put_events(Entries=entries[i:i + 10])
            if resp.get("FailedEntryCount"):
                raise RuntimeError("partial publish failure; transaction rolls back, retry next loop")
        await s.execute(MARK, {"ids": [r.id for r in rows]})
        return len(rows)


async def run(session_factory, bus_name: str, idle_sleep: float = 2.0):
    while True:
        n = await relay_once(session_factory, bus_name)
        if n == 0:
            await asyncio.sleep(idle_sleep)
