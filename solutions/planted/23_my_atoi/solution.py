def my_atoi(s):
    INT_MIN = -2147483648
    INT_MAX = 2147483647

    i = 0
    n = len(s)

    # 1. Skip leading spaces.
    while i < n and s[i] == ' ':
        i += 1

    # 2. Optional single sign.
    sign = 1
    if i < n and (s[i] == '+' or s[i] == '-'):
        if s[i] == '-':
            sign = -1
        i += 1

    # 3. Read consecutive digits.
    digits_start = i
    value = 0
    while i < n and '0' <= s[i] <= '9':
        value = value * 10 + (ord(s[i]) - ord('0'))
        i += 1

    # 4. No digits read -> 0.
    if i == digits_start:
        return 0

    value *= sign

    # 5. Clamp to 32-bit signed range.
    if value > INT_MAX:
        return INT_MAX
    return value
