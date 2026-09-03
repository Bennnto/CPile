def swap(a: list[int], i: int, j: int) -> None:
    temp: int = a[i]
    a[i] = a[j]
    a[j] = temp
