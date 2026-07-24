def excel_column_number(s):
    result = 0
    for ch in s:
        value = ord(ch) - ord('A') + 1
        result = result * 26 + value

    return result
