def multiply_strings(num1, num2):
    if num1 == "0" or num2 == "0":
        return "0"

    n1_len = len(num1)
    n2_len = len(num2)
    result = [0] * (n1_len + n2_len)

    for i in range(n1_len - 1, -1, -1):
        d1 = ord(num1[i]) - ord('0')
        for j in range(n2_len - 1, -1, -1):
            d2 = ord(num2[j]) - ord('0')
            pos_low = i + j + 1
            pos_high = i + j

            total = d1 * d2 + result[pos_low]
            result[pos_low] = total % 10
            result[pos_high] += total // 10

    # Strip leading zeros
    start = 0
    while start < len(result) - 1 and result[start] == 0:
        start += 1

    return ''.join(str(d) for d in result[start:])
