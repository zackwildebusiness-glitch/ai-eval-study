def excel_column_title(n):
    result = []
    while n > 0:
        n -= 1
        remainder = n % 26
        result.append(chr(ord('A') + remainder))
        n //= 26

    return ''.join(reversed(result))
