# Task: valid_parentheses

Implement a function with this exact signature in `solution.py`:

```python
def valid_parentheses(s):
    ...
```

**Spec:** Given a string `s` containing only the characters `(`, `)`, `[`, `]`, `{`, `}`,
return `True` if every opening bracket has a matching closing bracket of the same type,
correctly nested, and `False` otherwise. The empty string returns `True`.

**Constraints:**
- `s` contains only bracket characters (no other characters, no need to filter).
- Brackets must close in the correct order (e.g. `"([)]"` is invalid, `"([])"` is valid).
