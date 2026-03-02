---
description: Enforce async-first patterns for I/O operations
globs: "**/*.py"
---

# Async Pattern Rules

1. Default to `async def` for any I/O-bound operation (DB, HTTP, file I/O)
2. Use `asyncio.gather()` for concurrent independent operations
3. Use `asyncio.TaskGroup()` (Python 3.11+) for structured concurrency
4. NEVER use `.result` or `.wait()` — async all the way down
5. Use `httpx.AsyncClient` NOT `requests` for HTTP calls
6. Use `async for` with `AsyncIterator` when streaming data
7. Always set timeouts on external calls: `httpx.AsyncClient(timeout=30.0)`
