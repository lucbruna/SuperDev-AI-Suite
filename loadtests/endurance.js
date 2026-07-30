/**
 * Endurance (soak) test — 20 VUs sustained for 10 minutes.
 * Monitors for memory leaks, connection pool exhaustion, and slow degradation.
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { BASE_URL, defaultThresholds } from './config.js';

export const options = {
  stages: [
    { duration: '60s', target: 20 },   // ramp up
    { duration: '480s', target: 20 },  // sustained (8 min)
    { duration: '60s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<600', 'p(99)<1200'],
    http_req_failed: ['rate<0.02'],
  },
};

export default function () {
  group('Health — sustained', () => {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      '/health → 200': (r) => r.status === 200,
      '/health < 1s': (r) => r.timings.duration < 1000,
    });
  });

  group('Liveness — sustained', () => {
    const res = http.get(`${BASE_URL}/health/alive`);
    check(res, {
      '/health/alive → 200': (r) => r.status === 200,
    });
  });

  group('Readiness — sustained', () => {
    const res = http.get(`${BASE_URL}/health/ready`);
    check(res, {
      '/health/ready → 200': (r) => r.status === 200,
    });
  });

  sleep(Math.random() * 2 + 1); // 1-3s think time
}

export function handleSummary(data) {
  const checks = data.root_group?.checks ?? [];
  const passed = checks.filter(c => c.fails === 0).length;
  const failed = checks.filter(c => c.fails > 0).length;
  console.log(`\n===== ENDURANCE TEST SUMMARY =====`);
  console.log(`Duration     : 10 minutes`);
  console.log(`VUs (max)    : ${data.metrics.vus_max?.values?.value ?? 'N/A'}`);
  console.log(`Checks passed: ${passed}`);
  console.log(`Checks failed: ${failed}`);
  console.log(`Avg response : ${data.metrics.http_req_duration?.values?.avg?.toFixed(2)} ms`);
  console.log(`P95 response : ${data.metrics.http_req_duration?.values?.['p(95)']?.toFixed(2)} ms`);
  console.log(`P99 response : ${data.metrics.http_req_duration?.values?.['p(99)']?.toFixed(2)} ms`);
  console.log(`Error rate   : ${((data.metrics.http_req_failed?.values?.rate ?? 0) * 100).toFixed(2)}%`);
  console.log(`Total requests: ${data.metrics.http_reqs?.values?.count ?? 'N/A'}`);
  console.log(`====================================\n`);
  return {};
}
