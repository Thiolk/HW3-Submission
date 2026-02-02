import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    expected_load: {
      executor: 'constant-vus',
      vus: 10,          // adjust to your “expected load”
      duration: '30s',  // single short run
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],     // <1% errors
    http_req_duration: ['p(95)<300'],   // p95 < 300ms
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost';

export default function () {
  // Health check
  let r = http.get(`${BASE_URL}/health`);
  check(r, { 'health 200': (res) => res.status === 200 });

  // Create a task
  const desc = `perf-${__VU}-${__ITER}-load_test`;
  r = http.post(`${BASE_URL}/`, { description: desc });
  check(r, { 'create 200/302': (res) => res.status === 200 || res.status === 302 });
}