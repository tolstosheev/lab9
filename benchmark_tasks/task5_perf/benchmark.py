import subprocess
import sys
import time
import statistics
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent / "python_only"))
sys.path.insert(0, str(Path(__file__).parent / "python_rust"))
sys.path.insert(0, str(Path(__file__).parent / "python_go"))


def benchmark_function(func: Callable, n: int, iterations: int = 3) -> dict:
    times = []
    results = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(n)
        end = time.perf_counter()
        times.append(end - start)
        results.append(result)

    assert all(abs(r - results[0]) < abs(results[0]) * 0.001 for r in results), \
        f"Inconsistent results: {results}"
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "result": results[0]
    }


def run_benchmark(matrix_size: int, iterations: int = 3) -> dict:
    results = {}

    print(f"\n[1/3] Benchmarking Pure Python (matrix size: {matrix_size}x{matrix_size})...")
    from python_only.matrix_ops import compute_heavy as python_compute
    results["Python"] = benchmark_function(python_compute, matrix_size, iterations)
    print(f"  Mean time: {results['Python']['mean']:.4f}s")

    print(f"\n[2/3] Benchmarking Python+Rust (matrix size: {matrix_size}x{matrix_size})...")
    try:
        import matrix_ops_rust
        results["Python+Rust"] = benchmark_function(rust_compute, matrix_size, iterations)
        print(f"  Mean time: {results['Python+Rust']['mean']:.4f}s")
    except ImportError as e:
        print(f"  ERROR: Rust extension not built. Run: cd python_rust && maturin develop")
        print(f"  Error: {e}")
        results["Python+Rust"] = None

    print(f"\n[3/3] Benchmarking Python+Go (matrix size: {matrix_size}x{matrix_size})...")
    try:
        from python_go.matrix_ops import compute_heavy as go_compute, check_health

        if not check_health():
            print("  ERROR: Go service is not running. Start it with: cd python_go && go run main.go")
            results["Python+Go"] = None
        else:
            results["Python+Go"] = benchmark_function(go_compute, matrix_size, iterations)
            print(f"  Mean time: {results['Python+Go']['mean']:.4f}s")
    except ImportError as e:
        print(f"  ERROR: Could not import Go client. Install requests: pip install requests")
        print(f"  Error: {e}")
        results["Python+Go"] = None
    
    return results


def print_report(results: dict, matrix_size: int) -> None:
    print("\n" + "=" * 70)
    print("BENCHMARK REPORT")
    print("=" * 70)
    print(f"Matrix Size: {matrix_size}x{matrix_size}")
    print("=" * 70)

    python_time = results.get("Python", {}).get("mean") if results.get("Python") else None
    
    print(f"\n{'Implementation':<20} {'Mean (s)':<12} {'Speedup':<10} {'Status':<10}")
    print("-" * 70)
    
    for name, data in results.items():
        if data is None:
            print(f"{name:<20} {'N/A':<12} {'N/A':<10} {'FAILED':<10}")
        else:
            mean_time = data["mean"]
            if python_time and python_time > 0:
                speedup = f"{python_time / mean_time:.2f}x"
            else:
                speedup = "N/A"
            print(f"{name:<20} {mean_time:<12.4f} {speedup:<10} {'OK':<10}")
    
    print("=" * 70)

    for name, data in results.items():
        if data:
            print(f"\n{name} Details:")
            print(f"  Min: {data['min']:.4f}s, Max: {data['max']:.4f}s")
            print(f"  Std Dev: {data['stdev']:.4f}s")
            print(f"  Result: {data['result']:.2f}")
    
    print("\n" + "=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark matrix operations")
    parser.add_argument("--size", type=int, default=100, help="Matrix size (n x n)")
    parser.add_argument("--iterations", type=int, default=3, help="Number of iterations")
    args = parser.parse_args()
    
    print(f"Starting benchmarks with matrix size {args.size}x{args.size}")
    print(f"Running {args.iterations} iterations per implementation...")
    
    results = run_benchmark(args.size, args.iterations)
    print_report(results, args.size)

    report_path = Path(__file__).parent / "benchmark_results.txt"
    with open(report_path, "w") as f:
        f.write(f"Benchmark Results (Matrix Size: {args.size}x{args.size})\n")
        f.write(f"Iterations: {args.iterations}\n\n")
        for name, data in results.items():
            if data:
                f.write(f"{name}: {data['mean']:.4f}s (mean)\n")
            else:
                f.write(f"{name}: FAILED\n")
    
    print(f"\nResults saved to: {report_path}")


if __name__ == "__main__":
    main()
