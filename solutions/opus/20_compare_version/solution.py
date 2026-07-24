def compare_version(v1, v2):
    parts1 = v1.split('.')
    parts2 = v2.split('.')
    length = max(len(parts1), len(parts2))
    for i in range(length):
        a = int(parts1[i]) if i < len(parts1) else 0
        b = int(parts2[i]) if i < len(parts2) else 0
        if a < b:
            return -1
        if a > b:
            return 1
    return 0
