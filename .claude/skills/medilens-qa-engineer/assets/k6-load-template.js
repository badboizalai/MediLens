// tests/perf/read-api.js — run: k6 run -e BASE=https://staging.api.medilens.app -e TOKEN=... tests/perf/read-api.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    steady: { executor: 'ramping-arrival-rate', startRate: 5, timeUnit: '1s', preAllocatedVUs: 50, maxVUs: 200,
              stages: [{ target: 50, duration: '3m' }, { target: 50, duration: '10m' }, { target: 0, duration: '1m' }] },
    peak:   { executor: 'constant-arrival-rate', rate: 200, timeUnit: '1s', duration: '5m', preAllocatedVUs: 200, maxVUs: 400, startTime: '15m' },
  },
  thresholds: {
    'http_req_duration{endpoint:findings}': ['p(95)<300', 'p(99)<1000'],
    'http_req_duration{endpoint:unit_config}': ['p(95)<150'],
    http_req_failed: ['rate<0.005'],
  },
};

const headers = { Authorization: `Bearer ${__ENV.TOKEN}` };   // synthetic load-test user only

export default function () {
  const r1 = http.get(`${__ENV.BASE}/api/v1/findings?unit=dental`, { headers, tags: { endpoint: 'findings' } });
  check(r1, { 'findings 200': (r) => r.status === 200 });
  const r2 = http.get(`${__ENV.BASE}/api/v1/units/dental/config`, { headers, tags: { endpoint: 'unit_config' } });
  check(r2, { 'config 200': (r) => r.status === 200 });
  sleep(0.2);
}
