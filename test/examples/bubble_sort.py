def bubble_sort(arr: list[int], n: int) -> None:
    for i in range(n):
        for j in range(0, n - 1):
            if arr[j] > arr[j + 1]:
                temp: int = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp

def count_evens(nums: list[int], n: int) -> int:
    total: int = 0
    for i in range(n):
        if nums[i] % 2 == 0:
            total += 1
    return total
