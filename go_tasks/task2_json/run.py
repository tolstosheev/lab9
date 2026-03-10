import subprocess
import json


def run_go_program(input_data: dict) -> dict:
    input_json = json.dumps(input_data)


    result = subprocess.run(
        ["processor.exe"],
        input=input_json,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Go program failed: {result.stderr}")

    return json.loads(result.stdout)
