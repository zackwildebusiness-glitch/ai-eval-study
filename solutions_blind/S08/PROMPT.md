# Task: excel_column_title

Implement a function with this exact signature in `solution.py`:

```python
def excel_column_title(n):
    ...
```

**Spec:** Given a positive integer `n`, return the corresponding Excel spreadsheet column
title, e.g. `1 -> "A"`, `26 -> "Z"`, `27 -> "AA"`, `28 -> "AB"`, `703 -> "AAA"`.

**Constraints:**
- This is bijective base-26 (letters A-Z stand for 1-26, not 0-25), so there is no digit for
  zero — handle the borrow/carry accordingly.
- `n >= 1`.
- Return an uppercase string using only letters `A`-`Z`.
