/**
 * Spike test — sudden jump to 200 VUs to test resilience.
 * Normal → spike → recovery.
 */
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { BASE_URL, stressThresholds } from './config.js';

export const options = {
  stages: [
    { duration: '30s', target: 5 },    // baseline
    { duration: '5s', target: 200 },   // instant spike
    { duration: '30s', target: 200 },  // hold spike
    { duration: '5s', target: 5 },     // instant recovery
    { duration: '60s', target: 5 },    // sustained recovery
  ],
  thresholds: stressThresholds,
};

export default function () {
  group('Health during spike', () => {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      '/health → 200': (r) => r.status === 200,
      '/health < 5s': (r) => r.timings.duration < 5000,
    });
  });

  group('Liveness during spike', () => {
    const res = http.get(`${BASE_URL}/health/alive`);
    check(res, {
      '/health/alive → 200': (r) => r.status === 200,
    });
  });

  sleep(Math.random() * 1 + 0.5); // 0.5-1.5s think time
}

export function handleSummary(data) {
  const checks = data.root_group?.checks ?? [];
  const passed = checks.filter(c => c.fails === 0).length;
  const failed = checks.filter(c => c.fails > 0).length;
  console.log(`\n===== SPIKE TEST SUMMARY =====`);
  console.log(`VUs (max)     : ${data.metrics.vus_max?.values?.value ?? 'N/A'}`);
  console.log(`Checks passed : ${passed}`);
  console.log(`Checks failed : ${failed}`);
  console.log(`Avg response  : ${data.metrics.http_req_duration?.values?.avg?.toFixed(2)} ms`);
  console.log(`P95 response  : ${data.metrics.http_req_duration?.values?.['p(95)']?.toFixed(2)} ms`);
  console.log(`P99 response  : ${data.metrics.http_req_duration?.values?.['p(99)']?.toFixed(2)} ms`);
  console.log(`Error rate    : ${((data.metrics.http_req_failed?.values?.rate ?? 0) * 100).toFixed(2)}%`);
  console.log(`================================\n`);
  return {};
}
