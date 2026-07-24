def my_atoi(s):
    INT_MIN = -2147483648
    INT_MAX = 2147483647

    i = 0
    n = len(s)

    # Step 1: skip leading whitespace
    while i < n and s[i] == ' ':
        i += 1

    if i >= n:
        return 0

    # Step 2: optional sign
    sign = 1
    if s[i] == '+' or s[i] == '-':
        if s[i] == '-':
            sign = -1
        i += 1

    # Step 3: consecutive digits
    start = i
    while i < n and s[i].isdigit():
        i += 1

    digits = s[start:i]

    # Step 4: no digits -> 0
    if digits == '':
        return 0

    result = sign * int(digits)

    # Step 5: clamp to 32-bit signed range
    if result < INT_MIN:
        return INT_MIN
    if result > INT_MAX:
        return INT_MAX

    return result
