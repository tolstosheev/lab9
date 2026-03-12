def matrix_multiply(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    if not a or not b or len(a) == 0:
        return []
    
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    
    if cols_a != rows_b:
        raise ValueError("Incompatible matrix dimensions")
    
    result = [[0.0] * cols_b for _ in range(rows_a)]
    
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    
    return result

def matrix_transpose(matrix: list[list[float]]) -> list[list[float]]:
    if not matrix or len(matrix) == 0:
        return []
    
    rows, cols = len(matrix), len(matrix[0])
    return [[matrix[i][j] for i in range(rows)] for j in range(cols)]


def compute_heavy(n: int) -> float:
    a = [[float(i + j) for j in range(n)] for i in range(n)]
    b = [[float(i * j + 1) for j in range(n)] for i in range(n)]

    product = matrix_multiply(a, b)

    transposed = matrix_transpose(product)

    total = sum(sum(row) for row in transposed)
    
    return total
