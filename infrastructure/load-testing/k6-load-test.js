// k6 Load Test - SuperDev API
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const verificationLatency = new Trend('verification_latency');
const workflowLatency = new Trend('workflow_latency');
const kbQueryLatency = new Trend('kb_query_latency');
const totalRequests = new Counter('total_requests');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up
    { duration: '5m', target: 50 },   // Normal load
    { duration: '2m', target: 100 },  // Stress
    { duration: '5m', target: 100 },  // Sustained stress
    { duration: '2m', target: 200 },  // Peak
    { duration: '5m', target: 200 },  // Sustained peak
    { duration: '2m', target: 50 },   // Cool down
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 95th percentile < 2s
    http_req_failed: ['rate<0.01'],     // Error rate < 1%
    errors: ['rate<0.05'],              // Custom error rate < 5%
    verification_latency: ['p(95)<30000'], // Verification < 30s
    workflow_latency: ['p(95)<60000'],     // Workflow < 60s
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.superdev.example.com';
const API_KEY = __ENV.API_KEY || 'test-key';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_KEY}`,
  'X-Request-ID': 'k6-test',
};

function getAuthHeaders() {
  return {
    ...headers,
    'Authorization': `Bearer ${API_KEY}`,
  };
}

export default function () {
  // 1. Health check
  const health = http.get(`${BASE_URL}/health`, { headers: getAuthHeaders() });
  check(health, {
    'health check status 200': (r) => r.status === 200,
  });
  totalRequests.add(1);
  errorRate.add(health.status !== 200);

  // 2. Chat completion
  const chatPayload = {
    messages: [
      { role: 'user', content: 'Create a REST API endpoint for user authentication in FastAPI' },
    ],
    model: 'gpt-4o-mini',
    temperature: 0.3,
    max_tokens: 2000,
  };

  const chatStart = new Date();
  const chat = http.post(`${BASE_URL}/api/v1/chat/completions`, JSON.stringify(chatPayload), {
    headers: getAuthHeaders(),
  });
  const chatDuration = new Date() - chatStart;
  
  check(chat, {
    'chat status 200': (r) => r.status === 200,
    'chat has content': (r) => JSON.parse(r.body).choices?.[0]?.message?.content?.length > 0,
  });
  totalRequests.add(1);
  errorRate.add(chat.status !== 200);

  // 3. Verification loop
  const verifyPayload = {
    task_description: 'Create a FastAPI user authentication endpoint with JWT tokens',
    language: 'python',
    requirements: [
      'Use JWT for authentication',
      'Include password hashing with bcrypt',
      'Add rate limiting',
      'Include input validation',
    ],
    max_iterations: 3,
  };

  const verifyStart = new Date();
  const verify = http.post(`${BASE_URL}/api/v1/verify`, JSON.stringify(verifyPayload), {
    headers: getAuthHeaders(),
  });
  const verifyDuration = new Date() - verifyStart;
  
  check(verify, {
    'verify status 200': (r) => r.status === 200,
    'verify has final_code': (r) => {
      const body = JSON.parse(r.body);
      return body.final_code && body.final_code.length > 0;
    },
    'verify success': (r) => {
      const body = JSON.parse(r.body);
      return body.success === true;
    },
  });
  verificationLatency.add(verificationDuration);
  totalRequests.add(1);
  errorRate.add(verify.status !== 200 || JSON.parse(verify.body).success !== true);

  // 4. Workflow execution
  const workflowPayload = {
    name: 'Deploy microservice',
    steps: [
      { name: 'build', type: 'shell', config: { command: 'docker build -t myservice .' } },
      { name: 'test', type: 'shell', config: { command: 'pytest tests/' } },
      { name: 'deploy', type: 'shell', config: { command: 'kubectl apply -f k8s/' } },
    ],
  };

  const workflowStart = new Date();
  const workflow = http.post(`${BASE_URL}/api/v1/workflows`, JSON.stringify(workflowPayload), {
    headers: getAuthHeaders(),
  });
  const workflowDuration = new Date() - workflowStart;
  
  check(workflow, {
    'workflow status 201': (r) => r.status === 201,
    'workflow has run_id': (r) => JSON.parse(r.body).run_id !== undefined,
  });
  workflowLatency.add(workflowDuration);
  totalRequests.add(1);
  errorRate.add(workflow.status !== 201);

  // 5. Knowledge base search
  const searchPayload = {
    query: 'FastAPI authentication JWT',
    top_k: 5,
  };

  const kbStart = new Date();
  const search = http.post(`${BASE_URL}/api/v1/knowledge/search`, JSON.stringify(searchPayload), {
    headers: getAuthHeaders(),
  });
  const kbDuration = new Date() - kbStart;
  
  check(search, {
    'search status 200': (r) => r.status === 200,
    'search has results': (r) => JSON.parse(r.body).results?.length > 0,
  });
  kbQueryLatency.add(kbDuration);
  totalRequests.add(1);
  errorRate.add(search.status !== 200);

  // 6. Code execution
  const execPayload = {
    code: `
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
`,
    language: 'python',
  };

  const exec = http.post(`${BASE_URL}/api/v1/verify/execute`, JSON.stringify(execPayload), {
    headers: getAuthHeaders(),
  });
  
  check(exec, {
    'exec status 200': (r) => r.status === 200,
    'exec has output': (r) => JSON.parse(r.body).output?.includes('55'),
  });
  totalRequests.add(1);
  errorRate.add(exec.status !== 200);

  // 6. Knowledge base ingestion
  const ingestPayload = {
    repo_url: 'https://github.com/tiangolo/fastapi',
    file_patterns: ['*.py', '*.md'],
  };

  const ingest = http.post(`${BASE_URL}/api/v1/knowledge/ingest-repo`, JSON.stringify(ingestPayload), {
    headers: getAuthHeaders(),
  });
  
  check(ingest, {
    'ingest status 202': (r) => r.status === 202,
  });
  totalRequests.add(1);
  errorRate.add(ingest.status !== 202);

  sleep(1);
}

// Handle summary
export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'summary.json': JSON.stringify(data, null, 2),
  };
}

function textSummary(data, options) {
  const colors = {
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m',
  };
  
  let output = '\n' + '='.repeat(60) + '\n';
  output += 'K6 Load Test Summary - SuperDev API\n';
  output += '='.repeat(60) + '\n\n';
  
  // HTTP metrics
  output += `${colors.blue}HTTP Requests:${colors.reset}\n`;
  output += `  Total: ${data.metrics.http_reqs?.values?.count || 0}\n`;
  output += `  Failed: ${data.metrics.http_req_failed?.values?.passes || 0} (${(data.metrics.http_req_failed?.values?.rate * 100).toFixed(2)}%)\n`;
  output += `  Duration (avg): ${(data.metrics.http_req_duration?.values?.avg || 0).toFixed(2)}ms\n`;
  output += `  Duration (p95): ${(data.metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2)}ms\n\n`;
  
  // Custom metrics
  output += `${colors.blue}Custom Metrics:${colors.reset}\n`;
  output += `  Verification Latency (avg): ${(data.metrics.verification_latency?.values?.avg || 0).toFixed(2)}ms\n`;
  output += `  Verification Latency (p95): ${(data.metrics.verification_latency?.values?.['p(95)'] || 0).toFixed(2)}ms\n`;
  output += `  Workflow Latency (avg): ${(data.metrics.workflow_latency?.values?.avg || 0).toFixed(2)}ms\n`;
  output += `  KB Query Latency (avg): ${(data.metrics.kb_query_latency?.values?.avg || 0).toFixed(2)}ms\n`;
  output += `  Error Rate: ${(data.metrics.errors?.values?.rate * 100).toFixed(2)}%\n\n`;
  
  // Thresholds
  output += `${colors.blue}Thresholds:${colors.reset}\n`;
  const thresholds = options.thresholds || {};
  for (const [metric, threshold] of Object.entries(thresholds)) {
    const passed = checkThreshold(data, metric, threshold);
    output += `  ${passed ? colors.green + '✓' : colors.red + '✗'} ${metric}: ${threshold}\n`;
  }
  
  return output;
}

function checkThreshold(data, metric, threshold) {
  // Simplified threshold checking
  const value = getMetricValue(data, metric);
  if (threshold.includes('p(95)')) {
    const target = parseFloat(threshold.match(/p\(95\)<(\d+)/)[1]);
    return value <= target;
  }
  if (threshold.includes('rate<')) {
    const target = parseFloat(threshold.match(/rate<(\d+\.?\d*)/)[1]);
    return value <= target;
  }
  return true;
}

function getMetricValue(data, metric) {
  const m = data.metrics[metric];
  if (!m) return 0;
  if (metric.includes('latency')) {
    return m.values?.['p(95)'] || m.values?.avg || 0;
  }
  if (metric === 'http_req_duration') {
    return m.values?.['p(95)'] || 0;
  }
  if (metric === 'http_req_failed') {
    return m.values?.rate || 0;
  }
  if (metric === 'errors') {
    return m.values?.rate || 0;
  }
  return 0;
}