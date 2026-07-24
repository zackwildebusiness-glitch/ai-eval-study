def length_of_longest_substring(s):
    last_seen = {}
    start = 0
    best = 0

    for i, char in enumerate(s):
        if char in last_seen and last_seen[char] >= start:
            start = last_seen[char] + 1
        last_seen[char] = i
        best = max(best, i - start + 1)

    return best
