def compare_version(v1, v2):
    parts1 = v1.split('.')
    parts2 = v2.split('.')

    for n1_str, n2_str in zip(parts1, parts2):
        n1 = int(n1_str)
        n2 = int(n2_str)

        if n1 < n2:
            return -1
        elif n1 > n2:
            return 1

    return 0
