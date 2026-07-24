def excel_column_number(s):
    result = 0
    for ch in s:
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result
