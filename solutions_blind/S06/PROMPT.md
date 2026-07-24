# Task: compare_version

Implement a function with this exact signature in `solution.py`:

```python
def compare_version(v1, v2):
    ...
```

**Spec:** Given two version numbers `v1` and `v2` as dot-separated strings (e.g. `"1.01"`,
`"1.0.0"`), compare them. Each dot-separated segment must be compared as an **integer**, not
as a string (so `"1.01"` and `"1.001"` are equal, since `01 == 001`). If one version has
fewer segments than the other, the missing trailing segments are treated as `0`.

Return:
- `-1` if `v1 < v2`
- `1` if `v1 > v2`
- `0` if `v1 == v2`

**Constraints:**
- Each segment contains only digits (no leading `+`/`-`, no letters).
- Segments may have leading zeros (e.g. `"01"`), which must not affect numeric comparison.
