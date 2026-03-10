import pytest
import requests
import subprocess
import time
import os

BASE_URL = "http://localhost:8080"


@pytest.fixture(scope="module")
def server():
    cwd = os.path.dirname(__file__)
    
    subprocess.run(
        ["go", "build", "-o", "server.exe", "main.go"],
        check=True,
        cwd=cwd
    )

    server_path = os.path.join(cwd, "server.exe")
    process = subprocess.Popen([server_path], cwd=cwd)

    time.sleep(1)

    yield

    process.terminate()
    process.wait()


class TestStatusEndpoint:
    def test_get_returns_ok(self, server):
        response = requests.get(BASE_URL)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_post_returns_method_not_allowed(self, server):
        response = requests.post(BASE_URL, json={"test": "data"})

        assert response.status_code == 405

    def test_put_returns_method_not_allowed(self, server):
        response = requests.put(BASE_URL, json={"test": "data"})

        assert response.status_code == 405

    def test_delete_returns_method_not_allowed(self, server):
        response = requests.delete(BASE_URL)

        assert response.status_code == 405

    def test_patch_returns_method_not_allowed(self, server):
        response = requests.patch(BASE_URL, json={"test": "data"})

        assert response.status_code == 405

    def test_response_content_type_is_json(self, server):
        response = requests.get(BASE_URL)

        assert "application/json" in response.headers.get("Content-Type", "")
