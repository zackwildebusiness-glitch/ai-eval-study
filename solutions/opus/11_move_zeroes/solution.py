def move_zeroes(nums):
    non_zero = [num for num in nums if num != 0]
    zero_count = len(nums) - len(non_zero)
    return non_zero + [0] * zero_count
