/**
 * Shared configuration for all k6 load testing scripts.
 * Override via environment variables: BASE_URL, API_TOKEN.
 */
export const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
export const API_TOKEN = __ENV.API_TOKEN || '';

/** Standard thresholds applied to all load profiles. */
export const defaultThresholds = {
  http_req_duration: ['p(95)<500', 'p(99)<1000'],
  http_req_failed: ['rate<0.01'],
};

/** Aggressive thresholds for stress / spike tests. */
export const stressThresholds = {
  http_req_duration: ['p(95)<1000', 'p(99)<2000'],
  http_req_failed: ['rate<0.05'],
};
