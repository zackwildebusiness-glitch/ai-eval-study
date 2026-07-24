# Task: my_atoi

Implement a function with this exact signature in `solution.py`:

```python
def my_atoi(s):
    ...
```

**Spec:** Implement a simplified version of the C `atoi` function. Given a string `s`,
extract the leading integer it represents using these steps, in order:

1. Skip leading whitespace (spaces).
2. Read an optional single `+` or `-` sign.
3. Read consecutive digit characters, stopping at the first non-digit character (or end of
   string). This forms the number's digits (ignore anything after).
4. If no digits were read (regardless of whether a sign was seen), the result is `0`.
5. Clamp the resulting integer to the 32-bit signed integer range
   `[-2147483648, 2147483647]`. If it overflows below the minimum, return `-2147483648`; if
   it overflows above the maximum, return `2147483647`.

**Constraints:**
- Return an `int`.
- If `s` is empty or contains no valid leading integer, return `0`.
- Only ONE optional sign is allowed immediately before the digits; anything else (e.g. a
  sign not immediately followed by digits, or a second sign) means there is no valid number
  after that point.
