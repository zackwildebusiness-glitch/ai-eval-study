def move_zeroes(nums):
    non_zero = [n for n in nums if n != 0]
    zero_count = len(nums) - len(non_zero)
    return non_zero + [0] * zero_count
