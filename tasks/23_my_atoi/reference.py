def my_atoi(s):
    INT_MIN = -2147483648
    INT_MAX = 2147483647

    i = 0
    n = len(s)

    # 1. Skip leading whitespace.
    while i < n and s[i] == " ":
        i += 1

    if i >= n:
        return 0

    # 2. Optional single sign.
    sign = 1
    if s[i] == "+" or s[i] == "-":
        if s[i] == "-":
            sign = -1
        i += 1

    # 3. Consecutive digits.
    start = i
    while i < n and s[i].isdigit():
        i += 1

    if start == i:
        return 0

    value = sign * int(s[start:i])

    # 5. Clamp to 32-bit signed range.
    if value < INT_MIN:
        return INT_MIN
    if value > INT_MAX:
        return INT_MAX
    return value
