"""
Language-specific prompts for carbon footprint analysis.
Each prompt is designed to identify inefficiencies specific to the language.
"""

def get_prompt_for_language(language: str, code: str) -> tuple[str, str]:
    """
    Get sophisticated system and user prompts for rigorous sustainability analysis.
    
    Generates language-aware prompts that enforce strict JSON schema compliance
    and guide the AI to identify specific anti-patterns across sustainability metrics.
    
    Args:
        language: Programming language (python, java, javascript, cpp, go, rust, etc.)
        code: Source code to analyze
        
    Returns:
        Tuple of (system_prompt, user_prompt) with strict JSON enforcement
    """
    language = language.lower()
    
    # Comprehensive system prompt establishing AI as expert sustainability auditor
    system_prompt = """You are an Expert Sustainability Auditor specializing in carbon footprint optimization for software systems.

Your mission is to rigorously evaluate source code across these critical sustainability metrics:
1. CPU Efficiency - Algorithmic complexity, inefficient loops, redundant computations
2. Memory Optimization - Memory leaks, excessive allocations, poor data structures
3. Network Usage - Unnecessary API calls, missing caching, inefficient data transfer
4. Storage Patterns - Unoptimized queries, excessive logging, redundant I/O
5. Algorithmic Complexity - Poor algorithm choices, nested iterations, O(n²) or worse
6. Resource Leaks - Unclosed connections, file handles, database cursors
7. Idle Consumption - Blocking operations, polling instead of events, busy waiting
8. Environmental Impact - Overall energy consumption and carbon footprint

CRITICAL REQUIREMENTS:
- You MUST respond with ONLY valid JSON - no markdown, no explanations, no preamble
- Every issue MUST include an integer line number where the problem occurs
- Descriptions and suggestions MUST be single, concise sentences (max 150 characters each)
- Severity levels are STRICTLY: "critical", "high", "medium", or "low" (lowercase only)
- Issue types are STRICTLY: "cpu", "memory", "network", "storage", "algorithm", "resource_leak", "idle", or "other" (lowercase only)

Your analysis should identify specific anti-patterns including:
- Inefficient loops (nested, unbounded, missing break conditions)
- Memory leaks (unclosed resources, circular references, cache bloat)
- Unnecessary API calls (missing caching, redundant requests, no batching)
- Blocking operations (synchronous I/O, thread blocking, missing async)
- Unoptimized queries (N+1 problems, missing indexes, full table scans)
- Redundant computations (repeated calculations, missing memoization)
- Missing caching (repeated expensive operations, no result reuse)
- Poor data structures (wrong collection types, inefficient lookups)
- Excessive logging (verbose logs in hot paths, missing log levels)
- Language-specific inefficiencies (see language-specific guidance below)

Be precise, actionable, and focus on measurable environmental impact."""

    # Language-specific user prompts with anti-pattern focus
    language_specific_prompts = {
        "python": f"""Analyze this Python code for carbon-heavy patterns and sustainability issues.

```python
{code}
```

Python-Specific Focus Areas:
- Inefficient list comprehensions and generator expressions
- Pandas/NumPy operations that could be vectorized
- Missing context managers for file/database operations
- Global interpreter lock (GIL) contention issues
- Inefficient string concatenation in loops
- Missing caching decorators (@lru_cache, @cache)
- Synchronous I/O where async would be better
- Inefficient JSON parsing (missing orjson/ujson)
- Memory-heavy operations without generators
- Missing connection pooling for databases/APIs

You MUST respond with ONLY this exact JSON structure (no markdown, no code blocks):
{{"issues": [{{"type": "cpu|memory|network|storage|algorithm|resource_leak|idle|other", "severity": "critical|high|medium|low", "line": <integer>, "description": "<single concise sentence>", "suggestion": "<single concise sentence>"}}]}}

If no issues found, return: {{"issues": []}}""",

        "javascript": f"""Analyze this JavaScript/TypeScript code for carbon-heavy patterns and sustainability issues.

```javascript
{code}
```

JavaScript-Specific Focus Areas:
- Inefficient array methods (map/filter/reduce chains)
- Missing React.memo, useMemo, useCallback optimizations
- Memory leaks from event listeners and closures
- Unnecessary re-renders in React/Vue components
- Missing debouncing/throttling for frequent events
- Inefficient DOM manipulations (missing virtual DOM)
- Synchronous operations blocking event loop
- Missing lazy loading for components/routes
- Inefficient state management (prop drilling)
- Missing request caching (no SWR/React Query)

You MUST respond with ONLY this exact JSON structure (no markdown, no code blocks):
{{"issues": [{{"type": "cpu|memory|network|storage|algorithm|resource_leak|idle|other", "severity": "critical|high|medium|low", "line": <integer>, "description": "<single concise sentence>", "suggestion": "<single concise sentence>"}}]}}

If no issues found, return: {{"issues": []}}""",

        "java": f"""Analyze this Java code for carbon-heavy patterns and sustainability issues.

```java
{code}
```

Java-Specific Focus Areas:
- Inefficient collection operations and stream usage
- Excessive object creation causing GC pressure
- Missing try-with-resources for AutoCloseable
- Synchronization overhead and thread contention
- Inefficient string operations (missing StringBuilder)
- Missing connection pooling (JDBC, HTTP clients)
- Blocking I/O where NIO would be better
- Inefficient serialization (missing protocol buffers)
- Missing caching (Caffeine, Guava Cache)
- Reflection usage in hot paths

You MUST respond with ONLY this exact JSON structure (no markdown, no code blocks):
{{"issues": [{{"type": "cpu|memory|network|storage|algorithm|resource_leak|idle|other", "severity": "critical|high|medium|low", "line": <integer>, "description": "<single concise sentence>", "suggestion": "<single concise sentence>"}}]}}

If no issues found, return: {{"issues": []}}""",

        "cpp": f"""Analyze this C++ code for carbon-heavy patterns and sustainability issues.

```cpp
{code}
```

C++-Specific Focus Areas:
- Manual memory management issues (missing RAII)
- Inefficient STL container usage
- Missing move semantics and perfect forwarding
- Unnecessary copies (missing const references)
- Cache-unfriendly data structures
- Missing compiler optimizations (const, constexpr)
- Inefficient string operations (missing string_view)
- Thread synchronization overhead
- Missing smart pointers (unique_ptr, shared_ptr)
- Inefficient algorithm choices from STL

You MUST respond with ONLY this exact JSON structure (no markdown, no code blocks):
{{"issues": [{{"type": "cpu|memory|network|storage|algorithm|resource_leak|idle|other", "severity": "critical|high|medium|low", "line": <integer>, "description": "<single concise sentence>", "suggestion": "<single concise sentence>"}}]}}

If no issues found, return: {{"issues": []}}""",

        "go": f"""Analyze this Go code for carbon-heavy patterns and sustainability issues.

```go
{code}
```

Go-Specific Focus Areas:
- Missing defer for resource cleanup
- Goroutine leaks (missing context cancellation)
- Inefficient slice/map operations
- Missing sync.Pool for object reuse
- Blocking operations in goroutines
- Missing buffered channels causing blocking
- Inefficient JSON marshaling (missing easyjson)
- Missing connection pooling
- Inefficient string concatenation (missing strings.Builder)
- Race conditions and mutex contention

You MUST respond with ONLY this exact JSON structure (no markdown, no code blocks):
{{"issues": [{{"type": "cpu|memory|network|storage|algorithm|resource_leak|idle|other", "severity": "critical|high|medium|low", "line": <integer>, "description": "<single concise sentence>", "suggestion": "<single concise sentence>"}}]}}

If no issues found, return: {{"issues": []}}""",

        "rust": f"""Analyze this Rust code for carbon-heavy patterns and sustainability issues.

```rust
{code}
```

Rust-Specific Focus Areas:
- Unnecessary cloning (missing borrowing)
- Inefficient iterator chains
- Missing zero-copy deserialization
- Blocking operations in async contexts
- Inefficient string operations (missing Cow)
- Missing lazy evaluation (lazy_static)
- Inefficient collection usage
- Missing parallel iterators (rayon)
- Unnecessary heap allocations
- Inefficient error handling (missing Result combinators)

You MUST respond with ONLY this exact JSON structure (no markdown, no code blocks):
{{"issues": [{{"type": "cpu|memory|network|storage|algorithm|resource_leak|idle|other", "severity": "critical|high|medium|low", "line": <integer>, "description": "<single concise sentence>", "suggestion": "<single concise sentence>"}}]}}

If no issues found, return: {{"issues": []}}"""
    }
    
    # Get language-specific prompt or use Python as default
    user_prompt = language_specific_prompts.get(
        language,
        language_specific_prompts["python"]
    )
    
    return system_prompt, user_prompt


