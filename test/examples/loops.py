def sum_to_n(n: int) -> int:
    total: int = 0
    for i in range(n):
        total = total + i
    return total

def countdown(start: int) -> int:
    count: int = start
    while count > 0:
        count = count - 1
    return count
