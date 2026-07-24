def max_subarray(nums):
    best = nums[0]
    current = nums[0]
    for num in nums[1:]:
        current = max(num, current + num)
        best = max(best, current)
    return best
