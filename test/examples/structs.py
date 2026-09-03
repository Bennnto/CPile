class Vector:
    x: int
    y: int
def dot_product(a: Vector, b: Vector) -> int:
    return a.x * b.x + a.y * b.y
