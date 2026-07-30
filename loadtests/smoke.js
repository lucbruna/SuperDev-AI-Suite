/**
 * Smoke test — single VU, 30 seconds.
 * Validates that the API is reachable and basic endpoints respond correctly.
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, defaultThresholds } from './config.js';

export const options = {
  vus: 1,
  duration: '30s',
  thresholds: defaultThresholds,
};

export default function () {
  group('Health endpoints', () => {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'GET /health → 200': (r) => r.status === 200,
      'GET /health → JSON body': (r) => {
        try { JSON.parse(r.body); return true; } catch { return false; }
      },
      'GET /health → status=healthy': (r) => JSON.parse(r.body).data?.status === 'healthy',
    });
  });

  group('Liveness probe', () => {
    const res = http.get(`${BASE_URL}/health/alive`);
    check(res, {
      'GET /health/alive → 200': (r) => r.status === 200,
    });
  });

  group('Readiness probe', () => {
    const res = http.get(`${BASE_URL}/health/ready`);
    check(res, {
      'GET /health/ready → 200': (r) => r.status === 200,
    });
  });

  group('API docs', () => {
    const res = http.get(`${BASE_URL}/docs`);
    check(res, {
      'GET /docs → 200': (r) => r.status === 200,
    });
  });

  sleep(1);
}

export function handleSummary(data) {
  const checks = data.root_group?.checks ?? [];
  const passed = checks.filter(c => c.fails === 0).length;
  const failed = checks.filter(c => c.fails > 0).length;
  console.log(`\n===== SMOKE TEST SUMMARY =====`);
  console.log(`Checks passed : ${passed}`);
  console.log(`Checks failed : ${failed}`);
  console.log(`Avg response  : ${data.metrics.http_req_duration?.values?.avg?.toFixed(2)} ms`);
  console.log(`P95 response  : ${data.metrics.http_req_duration?.values?.['p(95)']?.toFixed(2)} ms`);
  console.log(`Error rate    : ${((data.metrics.http_req_failed?.values?.rate ?? 0) * 100).toFixed(2)}%`);
  console.log(`================================\n`);
  return {};
}
