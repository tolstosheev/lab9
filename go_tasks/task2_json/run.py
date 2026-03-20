import subprocess
import os
import json

def build_go_program():
    if os.path.exists('processor.exe'):
        return
    
    result = subprocess.run(
        ["go", "build", "-o", 'processor.exe', "main.go"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    if result.returncode != 0:
        raise RuntimeError(f"Go build failed: {result.stderr}")

def run_go_program(input_data: dict) -> dict:
    build_go_program()

    input_json = json.dumps(input_data)


    result = subprocess.run(
        ["processor.exe"],
        input=input_json,
        capture_output=True,
        text=True,
        encoding='UTF-8'
    )

    if result.returncode != 0:
        raise RuntimeError(f"Go program failed: {result.stderr}")

    return json.loads(result.stdout)
