def roman_to_int(s):
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        val = values[ch]
        if i + 1 < len(s) and val < values[s[i + 1]]:
            total -= val
        else:
            total += val
    return total
