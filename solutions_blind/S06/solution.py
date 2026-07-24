def compare_version(v1, v2):
    parts1 = v1.split('.')
    parts2 = v2.split('.')

    max_len = max(len(parts1), len(parts2))

    for i in range(max_len):
        n1 = int(parts1[i]) if i < len(parts1) else 0
        n2 = int(parts2[i]) if i < len(parts2) else 0

        if n1 < n2:
            return -1
        elif n1 > n2:
            return 1

    return 0
