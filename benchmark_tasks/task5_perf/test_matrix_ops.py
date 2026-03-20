import json
import os
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
    assert len(actual) == len(expected)
    for r_act, r_exp in zip(actual, expected):
        assert r_act == pytest.approx(r_exp, rel=rel)

def get_expected_heavy(n: int) -> float:
    if n <= 0: return 0.0

    a = [[float(i + j) for j in range(n)] for i in range(n)]
    b = [[float(i * j + 1) for j in range(n)] for i in range(n)]
    res = [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
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
    max_attempts = int(os.environ.get("GO_SERVER_TIMEOUT", "20"))
    for _ in range(max_attempts):
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
    from python_only import matrix_ops
    return {"multiply": matrix_ops.matrix_multiply, "transpose": matrix_ops.matrix_transpose, "heavy": matrix_ops.compute_heavy}

@pytest.fixture
def rust_mod():
    try:
        import matrix_ops_rust
        return {"multiply": matrix_ops_rust.matrix_multiply, "transpose": matrix_ops_rust.matrix_transpose, "heavy": matrix_ops_rust.compute_heavy}
    except ImportError:
        pytest.skip("Rust module not found")

@pytest.fixture
def go_mod(go_server):
    from python_go.matrix_ops import compute_heavy, check_health
    if not check_health(): pytest.skip("Go server offline")
    
    def multiply(a, b):
        resp = requests.post(f"{GO_SERVER_URL}/multiply", json={"a": a, "b": b})
        return resp.json()["result"] if resp.status_code == 200 else []

    def transpose(m):
        resp = requests.post(f"{GO_SERVER_URL}/transpose", json={"matrix": m})
        return resp.json()["result"] if resp.status_code == 200 else []

    return {"multiply": multiply, "transpose": transpose, "heavy": compute_heavy}


class TestCorrectness:
    @pytest.mark.parametrize("n", [0, 1, 5])
    @pytest.mark.parametrize("impl", ["python_mod", "rust_mod", "go_mod"])
    def test_heavy(self, request, impl, n):
        mod = request.getfixturevalue(impl)
        assert mod["heavy"](n) == pytest.approx(get_expected_heavy(n), rel=1e-6)

    @pytest.mark.parametrize("impl", ["python_mod", "rust_mod", "go_mod"])
    def test_multiply_square(self, request, impl):
        mod = request.getfixturevalue(impl)
        a = [[1.0, 2.0], [3.0, 4.0]]
        b = [[5.0, 6.0], [7.0, 8.0]]
        expected = [[19.0, 22.0], [43.0, 50.0]]
        assert_matrix_approx(mod["multiply"](a, b), expected)

class TestEdgeCases:
    def test_python_empty(self, python_mod):
        
        assert python_mod["multiply"]([], []) == []
        assert python_mod["transpose"]([]) == []

class TestPerformance:
    def test_benchmark_all(self, python_mod, rust_mod, go_mod):
        size = 50
        results = {}
        start_time = time.perf_counter()
        for name, mod in [("Python", python_mod), ("Rust", rust_mod), ("Go", go_mod)]:
            start = time.perf_counter()
            mod["heavy"](size)
            elapsed = time.perf_counter() - start
            results[name] = {"time": elapsed, "timestamp": time.time()}
        
        total_time = time.perf_counter() - start_time
        
        print(f"\nBenchmark ({size}x{size}):")
        for lang, data in results.items():
            print(f"  {lang}: {data['time']:.4f}s")
        print(f"  Total: {total_time:.4f}s")
        
        with open(TEST_DIR / "performance_metrics.json", "w") as f:
            json.dump({
                "benchmark_results": results,
                "total_time": total_time,
                "matrix_size": size,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])