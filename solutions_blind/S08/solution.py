def excel_column_title(n):
    chars = []
    while n > 0:
        # Bijective base-26: shift down by 1 so remainder maps 0->A .. 25->Z.
        n -= 1
        chars.append(chr(ord('A') + n % 26))
        n //= 26
    return ''.join(reversed(chars))
