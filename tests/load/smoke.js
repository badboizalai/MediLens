import http from 'k6/http';
import { check } from 'k6';

export const options = { vus: 5, duration: '30s', thresholds: { http_req_duration: ['p(95)<500'] } };

export default function () {
  const res = http.get(`${__ENV.API_URL || 'http://localhost:8000'}/healthz`);
  check(res, { 'status 200': (r) => r.status === 200 });
}
