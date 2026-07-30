/**
 * Normal load test — ramp to 10 VUs, hold, ramp down.
 * Tests authenticated and unauthenticated endpoints under expected traffic.
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { BASE_URL, API_TOKEN, defaultThresholds } from './config.js';

export const options = {
  stages: [
    { duration: '60s', target: 10 },   // ramp up
    { duration: '120s', target: 10 },  // sustained load
    { duration: '30s', target: 0 },    // ramp down
  ],
  thresholds: defaultThresholds,
};

function authHeaders() {
  return API_TOKEN
    ? { headers: { Authorization: `Bearer ${API_TOKEN}` } }
    : {};
}

export default function () {
  group('Public — GET /health', () => {
    const res = http.get(`${BASE_URL}/health`);
    check(res, { '/health → 200': (r) => r.status === 200 });
  });

  group('Public — GET /health/alive', () => {
    const res = http.get(`${BASE_URL}/health/alive`);
    check(res, { '/health/alive → 200': (r) => r.status === 200 });
  });

  if (API_TOKEN) {
    group('Authenticated — GET /api/v1/users/me', () => {
      const res = http.get(`${BASE_URL}/api/v1/users/me`, authHeaders());
      check(res, {
        '/api/v1/users/me → 200': (r) => r.status === 200,
      });
    });

    group('Authenticated — GET /api/v1/projects', () => {
      const res = http.get(`${BASE_URL}/api/v1/projects`, authHeaders());
      check(res, {
        '/api/v1/projects → 200': (r) => r.status === 200,
      });
    });
  }

  sleep(Math.random() * 2 + 1); // 1-3s think time
}

export function handleSummary(data) {
  const checks = data.root_group?.checks ?? [];
  const passed = checks.filter(c => c.fails === 0).length;
  const failed = checks.filter(c => c.fails > 0).length;
  console.log(`\n===== LOAD TEST SUMMARY =====`);
  console.log(`VUs (max)     : ${data.metrics.vus_max?.values?.value ?? 'N/A'}`);
  console.log(`Checks passed : ${passed}`);
  console.log(`Checks failed : ${failed}`);
  console.log(`Avg response  : ${data.metrics.http_req_duration?.values?.avg?.toFixed(2)} ms`);
  console.log(`P95 response  : ${data.metrics.http_req_duration?.values?.['p(95)']?.toFixed(2)} ms`);
  console.log(`P99 response  : ${data.metrics.http_req_duration?.values?.['p(99)']?.toFixed(2)} ms`);
  console.log(`Error rate    : ${((data.metrics.http_req_failed?.values?.rate ?? 0) * 100).toFixed(2)}%`);
  console.log(`==============================\n`);
  return {};
}
