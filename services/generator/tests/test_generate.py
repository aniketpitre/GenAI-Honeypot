import json

import httpx

from generator.generate import main, plant_breadcrumbs


def fake_api():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer t"
        key = json.loads(request.content)["external_key"]
        return httpx.Response(201, json={"value": f"https://canary.test/t/{key}"})
    return httpx.MockTransport(handler)


def test_plant_breadcrumbs_appends_lines():
    content = {"/home/sysadmin/todo.txt": "- a\n"}
    n = plant_breadcrumbs(content, [{"file": "/home/sysadmin/todo.txt", "name": "n", "external_key": "k1",
                                     "line": "- see {url}"}], "http://api", "t", transport=fake_api())
    assert n == 1 and content["/home/sysadmin/todo.txt"] == "- a\n- see https://canary.test/t/k1\n"


def test_main_mock_writes_files(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("API_URL", raising=False)
    assert main(["--persona", "persona_config.json", "--output", str(tmp_path)]) == 0
    assert (tmp_path / "home/sysadmin/.bash_history").read_text().startswith("sudo apt")
    assert (tmp_path / "var/log/auth.log").exists()
