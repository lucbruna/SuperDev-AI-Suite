# Memory Engine

The Memory Engine powers all memory operations in the SuperDev AI Suite.

## Overview

Manages conversation context, agent history, permanent knowledge, temporary memory,
embeddings, vectors, caching, learning, context retrieval, intelligent forgetting,
and consolidation.

## Components

| Module | Responsibility |
|---|---|
| `MemoryEngine` | Top-level orchestrator |
| `MemoryManager` | Lifecycle and CRUD operations |
| `MemoryService` | External-facing facade |
| `MemoryFactory` | Component construction |
| `MemoryRepository` | Data access layer |
| `MemoryCache` | TTL/LRU caching |
| `MemorySecurity` | Encryption and audit |
| `MemoryPermissions` | Role-based access control |
| `MemoryValidator` | Integrity checks |
| `MemoryOptimizer` | Dedup, compression, pruning |
| `MemoryScheduler` | Background maintenance |
| `MemoryCheckpoint` | Execution state saves |
| `MemorySnapshot` | Point-in-time captures |
| `MemoryBackup` / `MemoryRestore` | Backup and recovery |
| `MemoryProfiler` | Performance profiling |
| `MemoryStatistics` | Usage analytics |
| `MemoryContext` | Conversation/agent context |
| `MemoryState` | Lifecycle state machine |

## Memory Types

- **LOCAL**: Ephemeral per-operation
- **SESSION**: Per-conversation context
- **AGENT**: Per-agent history
- **GLOBAL**: Platform-wide shared
- **PERSISTENT**: Permanent storage

## Quick Start

```python
from ai.memory import MemoryEngine, MemoryConfig

engine = MemoryEngine(config=MemoryConfig.defaults())
engine.start()

await engine.remember("user_pref", {"theme": "dark"})
data = await engine.recall("user_pref")
```
