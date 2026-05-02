"""
Language-specific prompts for carbon footprint analysis.
Each prompt is designed to identify inefficiencies specific to the language.
"""

SYSTEM_PROMPT_BASE = """You are a Senior Sustainability Architect analyzing source code for carbon footprint optimization.

Your task is to identify patterns that increase cloud infrastructure energy consumption:
1. Inefficient loops and high cyclomatic complexity
2. Redundant data transfers and API calls
3. Heavy memory allocation patterns
4. Unnecessary computations

Provide a structured analysis with:
- Specific line numbers where issues occur
- Severity level (Critical, High, Medium, Low)
- Estimated impact on energy consumption
- Concrete refactoring suggestions

Be precise and actionable."""

LANGUAGE_PROMPTS = {
    "python": {
        "system": SYSTEM_PROMPT_BASE,
        "user_template": """Analyze this Python code for carbon-heavy patterns:

```python
{code}
```

Focus on:
- Nested loops and list comprehensions that could be optimized
- Inefficient use of pandas/numpy operations
- Redundant API calls or database queries
- Memory leaks from unclosed resources
- Use of inefficient data structures

Provide analysis in this JSON format:
{{
    "issues": [
        {{
            "line": <line_number>,
            "severity": "<Critical|High|Medium|Low>",
            "category": "<loops|memory|network|complexity>",
            "description": "<issue description>",
            "suggestion": "<refactoring suggestion>",
            "impact": "<energy impact description>"
        }}
    ],
    "summary": "<overall assessment>"
}}"""
    },
    
    "java": {
        "system": SYSTEM_PROMPT_BASE,
        "user_template": """Analyze this Java code for carbon-heavy patterns:

```java
{code}
```

Focus on:
- Inefficient collection operations and stream usage
- Unnecessary object creation and garbage collection pressure
- Synchronization overhead and thread management
- Inefficient I/O operations
- Resource leaks (unclosed connections, streams)

Provide analysis in this JSON format:
{{
    "issues": [
        {{
            "line": <line_number>,
            "severity": "<Critical|High|Medium|Low>",
            "category": "<loops|memory|network|complexity>",
            "description": "<issue description>",
            "suggestion": "<refactoring suggestion>",
            "impact": "<energy impact description>"
        }}
    ],
    "summary": "<overall assessment>"
}}"""
    },
    
    "javascript": {
        "system": SYSTEM_PROMPT_BASE,
        "user_template": """Analyze this JavaScript code for carbon-heavy patterns:

```javascript
{code}
```

Focus on:
- Inefficient array operations and loops
- Unnecessary re-renders in React/Vue components
- Memory leaks from event listeners and closures
- Redundant API calls without caching
- Inefficient DOM manipulations

Provide analysis in this JSON format:
{{
    "issues": [
        {{
            "line": <line_number>,
            "severity": "<Critical|High|Medium|Low>",
            "category": "<loops|memory|network|complexity>",
            "description": "<issue description>",
            "suggestion": "<refactoring suggestion>",
            "impact": "<energy impact description>"
        }}
    ],
    "summary": "<overall assessment>"
}}"""
    }
}

def get_prompt_for_language(language: str, code: str) -> tuple[str, str]:
    """
    Get the appropriate system and user prompts for a given language.
    
    Args:
        language: Programming language (python, java, javascript)
        code: Source code to analyze
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    language = language.lower()
    
    if language not in LANGUAGE_PROMPTS:
        # Default to Python prompt for unknown languages
        language = "python"
    
    prompt_config = LANGUAGE_PROMPTS[language]
    system_prompt = prompt_config["system"]
    user_prompt = prompt_config["user_template"].format(code=code)
    
    return system_prompt, user_prompt

# Made with Bob
