# Worker Jobs

## Job contract
```json
{"jobId":"uuid","type":"document.ocr","documentId":"uuid","pipelineVersion":"1.3.0","attempt":1,"traceparent":"00-..."}
```
IDs only; the worker loads data from DB/S3 inside the PHI boundary.

## State machine (document)
```
uploaded → validating → rejected
                     ↘ queued → ocr_running → extracting → extracted → in_review → confirmed
any running state → failed (after retries) | needs_manual (cost cap / repeated schema failure)
```
Transitions via `transition(document, to_state)` that checks allowed edges and writes `status_changed_at`; illegal transition → `InvalidState`.

## Reliability rules
- SQS visibility timeout = 2 × max job duration; heartbeat extends visibility for long OCR.
- Idempotency: `INSERT INTO processed_messages(consumer, message_id) ON CONFLICT DO NOTHING RETURNING ...`; if no row returned → already processed → ack and skip.
- Retries: built-in SQS redrive (`maxReceiveCount` 3–5) + in-code backoff for provider calls; DLQ alarm > 0.
- Timeouts per stage (see AI pipeline spec); cancellation-safe writes.
- Poison message → DLQ with reason attribute; runbook to inspect and redrive.

## Outbox relay
Runs every few seconds: select unpublished rows `FOR UPDATE SKIP LOCKED LIMIT 100`, publish (EventBridge PutEvents / SQS SendMessageBatch), mark published; at-least-once; ordering only per aggregate if needed (use SQS FIFO with `MessageGroupId=documentId`).

## Observability
Each job span named `job.<type>` with attributes `document.id`, `pipeline.version`, `attempt`; metrics: duration histogram, failures by reason, queue age (oldest message age) alarm.
