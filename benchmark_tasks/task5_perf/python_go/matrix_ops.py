import requests


GO_SERVICE_URL = "http://localhost:8080"


def compute_heavy(n: int) -> float:
    response = requests.post(
        f"{GO_SERVICE_URL}/compute",
        json={"n": n},
        headers={"Content-Type": "application/json"},
        timeout=300
    )
    response.raise_for_status()
    return response.json()["result"]


def check_health() -> bool:
    try:
        response = requests.get(f"{GO_SERVICE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
