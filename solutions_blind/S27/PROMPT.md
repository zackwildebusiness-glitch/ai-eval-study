# Task: simplify_path

Implement a function with this exact signature in `solution.py`:

```python
def simplify_path(path):
    ...
```

**Spec:** Given a string `path` representing an absolute Unix-style file path (starts with
`/`), return the simplified canonical path.

**Rules:**
- Consecutive slashes (`//`, `///`, ...) count as a single slash.
- A single period `.` refers to the current directory and is dropped.
- A double period `..` refers to the parent directory: pop the last directory off the result
  (if there is one; if already at root, `..` is a no-op).
- The returned path must start with a single `/`, use single slashes between directories,
  and must NOT end with a trailing slash unless the result is the root `"/"`.

**Constraints:**
- `path` is a valid absolute path (starts with `/`).
- Directory/file names may contain letters, digits, `.`, and other characters, and should be
  kept as-is (only the literal `.` and `..` segments are special).
