def compute_heavy(n: int) -> float:
    from matrix_ops_rust import compute_heavy as rust_compute_heavy
    return rust_compute_heavy(n)
