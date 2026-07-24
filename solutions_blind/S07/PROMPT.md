# Task: binary_search

Implement a function with this exact signature in `solution.py`:

```python
def binary_search(arr, target):
    ...
```

**Spec:** Given a list of integers `arr` sorted in ascending order and an integer `target`,
return the index of `target` in `arr` if it is present. If `target` is not present, return `-1`.

**Constraints:**
- `arr` is sorted ascending and may contain duplicates; if `target` occurs more than once,
  returning the index of any matching occurrence is acceptable.
- Aim for O(log n) time.
- An empty `arr` returns `-1`.
