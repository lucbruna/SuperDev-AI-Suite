# Frequently Asked Questions

## 1. What is SuperDev AI Suite?

SuperDev AI Suite is an enterprise-grade, AI-powered development platform that provides intelligent code generation, multi-agent orchestration, visual workflow building, and cloud-native runtime execution capabilities.

## 2. What programming languages are supported?

SuperDev supports Python and TypeScript/JavaScript as first-class languages. Through our runtime engine, we also support Go, Rust, and Java for code execution. The platform itself is built with Python (FastAPI) for the backend and Next.js (React) for the frontend.

## 3. Do I need a GPU to run SuperDev?

No. SuperDev connects to LLM providers (OpenAI, Anthropic) via API, which run on their infrastructure. For local models via Ollama, a GPU is recommended but not required. The platform itself runs on standard CPU-based infrastructure.

## 4. Can I use my own LLM provider?

Yes. SuperDev has a provider-agnostic LLM gateway that supports OpenAI, Anthropic, Ollama, and custom providers. You can configure multiple providers and route requests based on model capabilities, cost, or latency requirements.

## 5. Is SuperDev open source?

Yes, SuperDev AI Suite is open source under the MIT License. You can use it for personal, commercial, or enterprise projects. The source code is available on GitHub.

## 6. How do I add authentication to my deployment?

SuperDev comes with built-in JWT-based authentication. For production deployments, we recommend configuring SSO via SAML or OIDC. You can also integrate with Auth0, Okta, or any OAuth2 provider through the authentication middleware.

## 7. Can I extend SuperDev with custom functionality?

Yes. SuperDev features a hot-reload plugin system. You can create custom plugins using our SDK (Python and TypeScript) that integrate with the platform's event system, tool registry, and UI extension points.

## 8. How does the workflow engine work?

The workflow engine uses a DAG (directed acyclic graph) model where each step is a node with defined inputs, outputs, and dependencies. Workflows can be created visually using the React Flow editor or programmatically via YAML/JSON definitions.

## 9. What databases are supported?

PostgreSQL is the primary database (with pgvector extension for vector search). Redis is used for caching, session management, and message queuing. Object storage (S3, MinIO, or local filesystem) is used for file and artifact storage.

## 10. How do I contribute to the project?

See our [CONTRIBUTING.md](CONTRIBUTING.md) guide. We welcome contributions of all kinds: bug fixes, features, documentation, and tests. Please read our code of conduct before contributing.

## 11. What is the difference between an Agent and a Workflow?

Agents are AI-driven autonomous units that use LLMs to make decisions and interact with tools. Workflows are predefined DAGs of sequential or parallel steps. Agents can be used within workflows as steps, and workflows can be triggered by agents.

## 12. How do I report a security vulnerability?

Please email security@superdev.ai with details of the vulnerability. Do not create public GitHub issues for security concerns. See our [SECURITY.md](SECURITY.md) for more details.

## 13. What is the runtime engine?

The runtime engine provides sandboxed environments for executing untrusted code safely. It supports multiple programming languages, enforces resource limits, manages timeouts, and provides network isolation. Each execution runs in an isolated container.

## 14. Can I deploy SuperDev on-premises?

Yes. SuperDev is designed for on-premises deployment. We provide Docker Compose for small deployments and Kubernetes manifests for production-scale deployments. The platform has no external dependencies on cloud services (except LLM provider APIs).

## 15. How does caching work?

SuperDev uses Redis for multi-level caching: response caching for LLM calls, session caching for user sessions, query result caching for database queries, and rate limit counters. Cache invalidation follows a publish/subscribe pattern for distributed consistency.
