def sum_array(nums: list[int], n: int) -> int:
    total: int = 0
    for i in range(n):
        total = total + nums[i]
    return total
