def excel_column_title(n):
    letters = []
    while n > 0:
        n -= 1
        n, rem = divmod(n, 26)
        letters.append(chr(ord("A") + rem))
    return "".join(reversed(letters))
