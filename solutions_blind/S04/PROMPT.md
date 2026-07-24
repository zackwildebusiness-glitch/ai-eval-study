# Task: valid_ipv4

Implement a function with this exact signature in `solution.py`:

```python
def valid_ipv4(s):
    ...
```

**Spec:** Given a string `s`, return `True` if it is a valid dotted-decimal IPv4 address,
otherwise `False`.

**Rules for validity:**
- The string must split into exactly 4 parts on `.`.
- Each part must consist only of decimal digits (no signs, no whitespace, non-empty).
- Each part's integer value must be in the range `0`-`255`.
- No part may have a leading zero unless the part is exactly `"0"` (e.g. `"01"` is invalid,
  `"0"` is valid).

**Constraints:**
- Return a `bool` (`True`/`False`).
- Any deviation from the rules above (wrong part count, non-digit characters, out-of-range
  value, leading zeros, trailing/extra dots) must return `False`.
