def decode_string(s):
    stack = []  # each entry: [prev_string_parts, repeat_count]
    current = []
    num = 0

    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((current, num))
            current = []
            num = 0
        elif ch == "]":
            prev_current, k = stack.pop()
            current = prev_current + current * k
        else:
            current.append(ch)

    return "".join(current)
