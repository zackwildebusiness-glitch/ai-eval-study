def decode_string(s):
    # Stack holds (accumulated_string_before_bracket, repeat_count) frames.
    stack = []
    current = ""
    num = 0
    for ch in s:
        if ch.isdigit():
            num = int(ch)
        elif ch == '[':
            stack.append((current, num))
            current = ""
            num = 0
        elif ch == ']':
            prev, count = stack.pop()
            current = prev + current * count
        else:
            current += ch
    return current
