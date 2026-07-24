def multiply_strings(num1, num2):
    if num1 == "0" or num2 == "0":
        return "0"

    n1, n2 = len(num1), len(num2)
    # result[i] holds a digit-sum column; max length is n1 + n2
    result = [0] * (n1 + n2)

    # Schoolbook multiplication, indexing from the least-significant digit.
    for i in range(n1 - 1, -1, -1):
        d1 = ord(num1[i]) - ord('0')
        for j in range(n2 - 1, -1, -1):
            d2 = ord(num2[j]) - ord('0')
            # Position of this partial product in the result array.
            low = i + j + 1
            high = i + j
            total = d1 * d2 + result[low]
            result[low] = total % 10
            result[high] += total // 10

    # Skip leading zeros in the accumulated result.
    idx = 0
    while idx < len(result) - 1 and result[idx] == 0:
        idx += 1

    return "".join(str(d) for d in result[idx:])
