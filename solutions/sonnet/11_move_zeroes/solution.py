def move_zeroes(nums):
    result = [num for num in nums if num != 0]
    result.extend([0] * (len(nums) - len(result)))
    return result
