# Task: merge_intervals

Implement a function with this exact signature in `solution.py`:

```python
def merge_intervals(intervals):
    ...
```

**Spec:** Given a list of intervals `[start, end]` (each a 2-element list of ints, `start <= end`),
merge all overlapping intervals and return the merged list sorted by start value. Two intervals
that only touch at an endpoint (e.g. `[1,3]` and `[3,5]`) count as overlapping and must be merged
into `[1,5]`. An empty input returns `[]`.

**Constraints:**
- Input intervals may be given in any order.
- Return value: list of `[start, end]` lists, sorted ascending by start, with no overlaps
  remaining.
