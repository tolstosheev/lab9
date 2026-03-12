import json
import signal
import subprocess
import sys
import time
from pathlib import Path
import pytest
import requests

TEST_DIR = Path(__file__).parent
for path in ["python_only", "python_rust", "python_go"]:
    sys.path.insert(0, str(TEST_DIR / path))

GO_SERVER_URL = "http://localhost:8080"

def assert_matrix_approx(actual, expected, rel=1e-7):
    assert len(actual) == len(expected), f"Разное кол-во строк: {len(actual)} != {len(expected)}"
    for r_act, r_exp in zip(actual, expected):
        assert len(r_act) == len(r_exp), "Разное кол-во столбцов в строке"
        assert r_act == pytest.approx(r_exp, rel=rel)

def get_expected_heavy(n: int) -> float:
    if n <= 0: return 0.0
    a = [[float(i + j) for j in range(n)] for i in range(n)]
    b = [[float(i * j + 1) for j in range(n)] for i in range(n)]

    res = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                res[i][j] += a[i][k] * b[k][j]
    
    return sum(sum(row) for row in res)

@pytest.fixture(scope="session")
def go_server():

    go_dir = TEST_DIR / "python_go"

    process = subprocess.Popen(
        ["go", "run", "main.go"],
        cwd=str(go_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    
    for _ in range(20):
        try:
            if requests.get(f"{GO_SERVER_URL}/health", timeout=1).status_code == 200:
                break
        except:
            time.sleep(0.5)
    else:
        process.kill()
        pytest.fail("Go server failed to start")
    
    yield True
    
    if sys.platform == "win32":
        process.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        process.terminate()

@pytest.fixture
def python_mod():
    from python_only.matrix_ops import matrix_multiply, matrix_transpose, compute_heavy
    return {"multiply": matrix_multiply, "transpose": matrix_transpose, "heavy": compute_heavy}

@pytest.fixture
def rust_mod():
    try:
        import matrix_ops_rust
        return {
            "multiply": getattr(matrix_ops_rust, "matrix_multiply", None),
            "transpose": getattr(matrix_ops_rust, "matrix_transpose", None),
            "heavy": getattr(matrix_ops_rust, "compute_heavy", None),
        }
    except ImportError:
        pytest.skip("Rust module not built")

@pytest.fixture
def go_mod(go_server):
    from python_go.matrix_ops import compute_heavy
    
    def multiply(a, b):
        r = requests.post(f"{GO_SERVER_URL}/multiply", json={"a": a, "b": b}, timeout=5)
        r.raise_for_status()
        return r.json()["result"]

    return {"heavy": compute_heavy, "multiply": multiply}

class TestMatrixMultiply:
    @pytest.mark.parametrize("impl_name", ["python_mod", "rust_mod"])
    def test_square(self, request, impl_name):
        mod = request.getfixturevalue(impl_name)
        if not mod.get("multiply"): pytest.skip(f"Multiply not implemented in {impl_name}")
        
        a = [[1.0, 2.0], [3.0, 4.0]]
        b = [[5.0, 6.0], [7.0, 8.0]]
        expected = [[19.0, 22.0], [43.0, 50.0]]
        assert_matrix_approx(mod["multiply"](a, b), expected)

    def test_incompatible_dims(self, python_mod):
        with pytest.raises(ValueError):
            python_mod["multiply"]([[1, 2]], [[1, 2, 3]])

class TestMatrixTranspose:
    def test_basic(self, python_mod):
        m = [[1.0, 2.0], [3.0, 4.0]]
        expected = [[1.0, 3.0], [2.0, 4.0]]
        assert_matrix_approx(python_mod["transpose"](m), expected)

class TestComputeHeavy:
    @pytest.mark.parametrize("n", [0, 1, 5, 10])
    @pytest.mark.parametrize("impl_name", ["python_mod", "rust_mod", "go_mod"])
    def test_correctness(self, request, impl_name, n):
        mod = request.getfixturevalue(impl_name)
        if not mod.get("heavy"): pytest.skip(f"Heavy not implemented in {impl_name}")
        
        result = mod["heavy"](n)
        assert result == pytest.approx(get_expected_heavy(n), rel=1e-6)


class TestPerformance:
    @pytest.mark.parametrize("size", [50, 100])
    def test_benchmark(self, python_mod, rust_mod, go_mod, size):
        report = {}
        for name, mod in [("Python", python_mod), ("Rust", rust_mod), ("Go", go_mod)]:
            if not mod.get("heavy"): continue
            
            start = time.perf_counter()
            mod["heavy"](size)
            duration = time.perf_counter() - start
            report[name] = duration

        print(f"\nResults for {size}x{size}:")
        for lang, t in report.items():
            print(f"  {lang}: {t:.4f}s")

        with open(TEST_DIR / "benchmark_results.json", "a") as f:
            f.write(json.dumps({"size": size, "data": report}) + "\n")