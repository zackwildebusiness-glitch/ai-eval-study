# Task: excel_column_number

Implement a function with this exact signature in `solution.py`:

```python
def excel_column_number(s):
    ...
```

**Spec:** Given a string `s` representing an Excel spreadsheet column title (e.g. `"A"`,
`"AB"`, `"ZZ"`), return the corresponding column number. This is the inverse of the
`excel_column_title` task: `"A" -> 1`, `"Z" -> 26`, `"AA" -> 27`, `"AB" -> 28`.

**Constraints:**
- `s` consists only of uppercase letters `A`-`Z`.
- This is bijective base-26 (letters stand for 1-26, not 0-25).
- Return an `int`.
