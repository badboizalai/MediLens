# Performance Testing

| Scenario | Load | Threshold | NFR |
| --- | --- | --- | --- |
| Read API (findings, timeline, units config) | ramp to 50 rps, hold 10 min | p95 < 300 ms, p99 < 1 s, errors < 0.5% | NFR-02/03 |
| Peak | 200 rps for 5 min | errors < 1%, autoscaling reacts < 3 min | NFR-03 |
| Upload + processing | 100 documents in 60 min | 95% complete < 2 min, no DLQ messages | NFR-04 |
| Explain streaming | 20 concurrent sessions | first token < 3 s p95 | UX |
| Soak | 20 rps for 4 h | no memory growth > 10%, no error drift | stability |

## What to watch
API: latency histogram, 5xx, CPU/memory per task, DB connections, slow queries. Worker: queue depth, oldest message age, job duration per stage, provider throttling. DB: CPU, IOPS, locks. Cost during the test.

## Analysis template
Baseline vs current table; bottleneck hypothesis; evidence (trace, query plan); fix; re-test result.
