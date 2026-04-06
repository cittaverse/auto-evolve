# DashScope Async API Research for narrative-scorer v0.7.1

**Date**: 2026-03-27
**Author**: Hulk (GEO #72)
**Status**: Research Complete — Ready for Implementation

---

## Executive Summary

This document researches DashScope SDK's async API capabilities to optimize LLM-based narrative scoring performance. Key finding: **async concurrent calls can achieve 4x throughput improvement** while maintaining identical cost.

**Recommendation**: Implement asyncio Direct pattern for v0.7.1, enabling batch scoring with configurable concurrency.

---

## DashScope Async Patterns Overview

The DashScope Python SDK provides **3 distinct async patterns**, each suited to different use cases:

| Pattern | Base Class | Method Signature | Use Case |
|---------|------------|------------------|----------|
| **Task-Based Async** | `BaseAsyncApi` | Synchronous methods | Long-running ops (image/video generation) with status polling |
| **asyncio Direct** | `BaseAioApi` | `async` methods | Immediate async/await for simple API calls |
| **asyncio + Task** | `BaseAsyncAioApi` | `async` methods | Full async/await with task management for complex workflows |

### Pattern Selection for narrative-scorer

**Recommended**: **asyncio Direct** (`BaseAioApi` style)

**Rationale**:
1. narrative-scorer is a **library**, not a long-running service
2. LLM text generation responses are **immediate** (2-3 sec), not long-running like image synthesis (30-60 sec)
3. No need for task polling complexity
4. Simple async/await integration for batch processing

**Not Recommended**: Task-Based Async
- Designed for operations that take minutes (image/video generation)
- Requires polling loop or blocking `wait()` call
- Overkill for LLM text generation

---

## Performance Analysis

### Current State (v0.7.0 — Synchronous)

```python
# Synchronous LLM calls (v0.7.0)
for text in texts:
    result = llm_extractor.extract(text)  # ~2-3 sec per call
    scores.append(result)
# Total: 150 narratives × 2.5 sec = 375 sec (~6.25 minutes)
```

### Target State (v0.7.1 — Async Concurrent)

```python
# Async concurrent calls (v0.7.1)
async with httpx.AsyncClient() as client:
    tasks = [extract_async(text, client) for text in texts]
    results = await asyncio.gather(*tasks)
# Total: 150 narratives / 4 concurrent = ~38 batches × 2.5 sec = 95 sec (~1.6 minutes)
# **4x throughput improvement**
```

### Throughput Comparison

| Batch Size | Sync Time | Async Time (4x) | Async Time (8x) |
|------------|-----------|-----------------|-----------------|
| 5 (benchmark) | ~12.5 sec | ~3 sec | ~2 sec |
| 25 (test suite) | ~62.5 sec | ~16 sec | ~8 sec |
| 150 (pilot RCT) | ~6.25 min | ~1.6 min | ~50 sec |
| 1500 (large study) | ~62.5 min | ~16 min | ~8 min |

**Note**: Cost remains identical (pay per API call, not per second).

---

## Implementation Pattern

### Basic Async Wrapper

```python
import asyncio
import httpx
from typing import Optional

class AsyncLLMFeatureExtractor:
    """Async LLM feature extractor for narrative scoring."""
    
    def __init__(self, api_key: Optional[str] = None, max_concurrency: int = 4):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
    
    async def extract_async(self, text: str, client: httpx.AsyncClient) -> dict:
        """Extract features from a single narrative asynchronously."""
        async with self.semaphore:
            response = await client.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "qwen-turbo",
                    "input": {"messages": [{"role": "user", "content": self._build_prompt(text)}]}
                }
            )
            response.raise_for_status()
            return self._parse_response(response.json())
    
    async def extract_batch_async(self, texts: list[str]) -> list[dict]:
        """Extract features from multiple narratives concurrently."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [self.extract_async(text, client) for text in texts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

### Integration with narrative-scorer

```python
# narrative_scorer/llm_feature_extractor.py
from typing import Optional, Union
import asyncio

class LLMFeatureExtractor:
    """LLM-based feature extractor (supports both sync and async)."""
    
    def __init__(self, api_key: Optional[str] = None, max_concurrency: int = 4):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.max_concurrency = max_concurrency
        self._async_extractor = AsyncLLMFeatureExtractor(api_key, max_concurrency)
    
    def extract(self, text: str) -> dict:
        """Synchronous extraction (v0.7.0 compatibility)."""
        return asyncio.run(self.extract_async(text))
    
    async def extract_async(self, text: str) -> dict:
        """Async extraction for single narrative."""
        async with httpx.AsyncClient() as client:
            return await self._async_extractor.extract_async(text, client)
    
    async def extract_batch_async(self, texts: list[str]) -> list[dict]:
        """Async batch extraction (v0.7.1+)."""
        return await self._async_extractor.extract_batch_async(texts)
```

### Usage Examples

**Single Narrative (Sync)**:
```python
from narrative_scorer import LLMFeatureExtractor

extractor = LLMFeatureExtractor()
features = extractor.extract("今天我去公园散步...")
```

**Single Narrative (Async)**:
```python
import asyncio
from narrative_scorer import LLMFeatureExtractor

async def main():
    extractor = LLMFeatureExtractor()
    features = await extractor.extract_async("今天我去公园散步...")

asyncio.run(main())
```

**Batch Processing (Async)**:
```python
import asyncio
from narrative_scorer import LLMFeatureExtractor

async def score_batch(narratives: list[str]):
    extractor = LLMFeatureExtractor(max_concurrency=8)
    all_features = await extractor.extract_batch_async(narratives)
    return all_features

asyncio.run(score_batch(narratives))
```

---

## Error Handling

### Retry with Exponential Backoff

```python
import asyncio
from httpx import RequestError, TimeoutException

async def extract_with_retry(self, text: str, client: httpx.AsyncClient, max_retries: int = 3) -> dict:
    """Extract with exponential backoff on transient failures."""
    for attempt in range(max_retries):
        try:
            return await self.extract_async(text, client)
        except (RequestError, TimeoutException) as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + (asyncio.random() * 0.1)  # Jitter
            await asyncio.sleep(wait_time)
```

### Handling Partial Failures in Batch

```python
async def extract_batch_async(self, texts: list[str]) -> list[Union[dict, Exception]]:
    """Extract batch, returning exceptions for failed items."""
    async with httpx.AsyncClient() as client:
        tasks = [self.extract_with_retry(text, client) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Usage
results = await extractor.extract_batch_async(narratives)
for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Narrative {i} failed: {result}")
    else:
        process(result)
```

---

## Migration Path

### v0.7.0 (Current — Q1 2026)
- Synchronous LLM calls only
- Simple, debuggable, no API key needed for rule-only fallback

### v0.7.1 (Next — Q2 2026)
- Add `extract_async()` and `extract_batch_async()` methods
- Optional async support (backward compatible)
- Configurable concurrency (default: 4)

### v0.7.2 (Future — Q3 2026)
- High-level `score_batch()` API with auto-concurrency tuning
- Progress callbacks for long batches
- Cost estimation before batch execution

---

## Cost Analysis

**DashScope Pricing** (qwen-turbo):
- Input: ¥0.002 / 1K tokens
- Output: ¥0.006 / 1K tokens
- Average narrative: ~200 input tokens, ~50 output tokens
- **Cost per narrative**: ~¥0.0007 (input) + ~¥0.0003 (output) = **¥0.001**

| Scenario | Narratives | Sync Time | Async Time (4x) | Cost (¥) |
|----------|------------|-----------|-----------------|----------|
| Benchmark validation | 5 | ~12.5 sec | ~3 sec | ¥0.005 |
| Full test suite | 25 | ~62.5 sec | ~16 sec | ¥0.025 |
| Pilot RCT | 150 | ~6.25 min | ~1.6 min | ¥0.15 |
| Large-scale study | 1500 | ~62.5 min | ~16 min | ¥1.50 |

**Key Insight**: Async provides **4x speedup at identical cost**.

---

## Testing Strategy

### Unit Tests (Mock API)

```python
# tests/test_async_extractor.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_extract_batch_async():
    extractor = LLMFeatureExtractor(api_key="test-key")
    
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = {"output": {"text": '{"emotions": ["happy"]}'}}
        
        results = await extractor.extract_batch_async(["text1", "text2"])
        
        assert len(results) == 2
        assert mock_post.call_count == 2
```

### Integration Tests (Live API — Requires DASHSCOPE_API_KEY)

```python
# tests/test_integration_async.py
@pytest.mark.asyncio
@pytest.mark.requires_api_key
async def test_live_async_extraction():
    extractor = LLMFeatureExtractor()
    results = await extractor.extract_batch_async([
        "今天我很开心，因为天气很好。",
        "昨天我很难过，因为下雨了。"
    ])
    
    assert len(results) == 2
    assert all(isinstance(r, dict) for r in results)
```

---

## Best Practices

### 1. Concurrency Limits
- **Default**: 4 concurrent requests (balanced for most use cases)
- **High-throughput**: 8-16 concurrent requests (if API rate limits allow)
- **Conservative**: 2 concurrent requests (if rate-limited)

### 2. Timeout Configuration
```python
# Set timeouts to prevent hanging
async with httpx.AsyncClient(timeout=30.0) as client:
    # ...
```

### 3. Resource Cleanup
```python
# Always use async context managers
async with httpx.AsyncClient() as client:
    # Client automatically closes
```

### 4. Rate Limiting
```python
# Add delays if hitting rate limits
async def extract_with_rate_limit(text: str, delay: float = 0.1):
    await asyncio.sleep(delay)
    return await extract_async(text)
```

---

## References

- **DashScope SDK GitHub**: https://github.com/dashscope/dashscope-sdk-python
- **Async Programming Patterns**: https://deepwiki.com/dashscope/dashscope-sdk-python/11.3-async-programming-patterns
- **HTTPX Async Client**: https://www.python-httpx.org/async/
- **asyncio.gather()**: https://docs.python.org/3/library/asyncio-task.html#asyncio.gather

---

## Next Steps

1. **Implement `AsyncLLMFeatureExtractor`** in `narrative-scorer/llm_feature_extractor.py`
2. **Add unit tests** (mock API) in `narrative-scorer/tests/test_async_extractor.py`
3. **Add integration tests** (live API) in `narrative-scorer/tests/test_integration_async.py`
4. **Update CHANGELOG.md** for v0.7.1 release
5. **Benchmark performance** with 150-narrative pilot dataset

---

*Research completed for GEO #72. Ready for v0.7.1 implementation.*
