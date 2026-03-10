import pytest
import json
from run import run_go_program

class TestProcessor:

    @pytest.mark.parametrize("name, age, expected_adult", [
        ("Alice", 25, True),
        ("Bob", 17, False),
        ("Charlie", 18, True),
        ("Baby", 0, False),
        ("Elder", 100, True),
        ("Юникод", 30, True),
    ])
    def test_logic(self, name, age, expected_adult):
        payload = {"name": name, "age": age}
        output = run_go_program(payload)
        
        assert output["name"] == name
        assert output["age"] == age
        assert output["is_adult"] == expected_adult

    def test_invalid_json(self):
        with pytest.raises(RuntimeError):
            run_go_program("это не json")

    def test_wrong_types(self):
        with pytest.raises(RuntimeError):
            run_go_program({"name": "Wrong", "age": "twenty"})

    def test_output_structure(self):
        output = run_go_program({"name": "Test", "age": 30})
        assert "name" in output
        assert "age" in output
        assert "is_adult" in output