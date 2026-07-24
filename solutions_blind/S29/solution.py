def climb_stairs(n):
    prev, curr = 1, 1
    for _ in range(n - 1):
        prev, curr = curr, prev + curr
    return curr
