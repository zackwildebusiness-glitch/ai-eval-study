# Task: decode_string

Implement a function with this exact signature in `solution.py`:

```python
def decode_string(s):
    ...
```

**Spec:** Given an encoded string `s` in the form `k[encoded_substring]`, decode it. The
`k` is a positive integer (possibly multiple digits) meaning the `encoded_substring` inside
the matching square brackets is repeated `k` times. Encodings may be **nested**, e.g.
`"3[a2[c]]"` decodes to `"accaccacc"`. The input may also contain plain (non-encoded)
characters mixed in.

**Constraints:**
- `k` is always a positive integer and may have more than one digit (e.g. `"10[a]"`).
- Brackets are always well-formed and properly nested.
- Do not use `eval`.
