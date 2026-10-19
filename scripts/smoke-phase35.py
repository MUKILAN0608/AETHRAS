"""Start isolated local Go/Python services and verify offline review/execution.

Run with an environment containing the AI service dependencies and Go on PATH.
No provider key or external provider request is used. Services are always stopped.
"""
import json
import argparse
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def call(port, path, body=None):
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def wait_health(port):
    for _ in range(150):
        try:
            if call(port, "/health")[0] == 200:
                return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.2)
    raise RuntimeError(f"Service on {port} did not become ready")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", action="store_true", help="Also exercise the Godot main scene against temporary services")
    args = parser.parse_args()
    ai_port, go_port = free_port(), free_port()
    environment = {**os.environ, "AETHRAS_DECISION_ENABLED": "false", "CLOUDFLARE_AUTH_TOKEN": "",
                   "AETHRAS_DECISION_PROVIDER": "cloudflare_clef_flash",
                   "AI_SERVICE_URL": f"http://127.0.0.1:{ai_port}", "GAME_SERVER_PORT": str(go_port)}
    processes = []
    # Build first so terminating the launched server does not leave a go-run child.
    with tempfile.TemporaryDirectory(prefix="aethras-smoke-") as temp:
        executable = Path(temp) / ("server.exe" if os.name == "nt" else "server")
        subprocess.run(["go", "build", "-o", str(executable), "."], cwd=ROOT / "server/game-server", check=True)
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        try:
            processes.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(ai_port)], cwd=ROOT / "ai", env=environment, creationflags=flags))
            processes.append(subprocess.Popen([str(executable)], cwd=ROOT / "server/game-server", env=environment, creationflags=flags))
            wait_health(ai_port)
            wait_health(go_port)
            status, _ = call(go_port, "/api/world/generate", {"scenario_id": "scenario_1", "scenario": "A fortress stands between a living forest and a restless ocean.", "seed": 42})
            assert status == 200
            prompt = "The ocean rises and consumes the fortress."
            status, proposal = call(go_port, "/api/prompt/interpret", {"prompt": prompt, "world_context": {"entities": {}}})
            assert status == 200 and proposal["status"] == "VALID", proposal
            assert proposal["decision"]["status"] == "disabled" and proposal["proposal_id"]
            status, result = call(go_port, "/api/prompt/execute", {"prompt": prompt, "actor": "human", "proposal_id": proposal["proposal_id"]})
            assert status == 200 and result["parsed_action"]["action"] == "FLOOD", result
            assert result["transform"]["world_state"]["environmental_state"]["water_level"] > 0
            assert result["transform"]["affected_ids"] and result["transform"]["events"]
            assert call(go_port, "/api/prompt/execute", {"prompt": prompt, "proposal_id": proposal["proposal_id"]})[0] == 409
            _, rejected = call(go_port, "/api/prompt/interpret", {"prompt": "The invisible moon destroys the ancient city."})
            assert rejected["status"] == "INVALID" and not rejected.get("proposal_id")
            print("PASS: generate -> interpret -> review token -> execute -> world events; replay and critic rejection")
            if args.godot:
                game_environment = {**environment, "GODOT_GAME_SERVER_URL": f"http://127.0.0.1:{go_port}"}
                result = subprocess.run(["godot", "--headless", "--path", str(ROOT / "game/godot"),
                                         "--script", "res://tests/prompt_flow_test.gd"],
                                        env=game_environment, capture_output=True, text=True, timeout=30,
                                        creationflags=flags)
                print(result.stdout)
                if result.returncode != 0 or "SCRIPT ERROR" in result.stderr or "ERROR:" in result.stderr:
                    print(result.stderr)
                    raise RuntimeError("Godot prompt-flow smoke failed")
                # Keep Go running; replace only our temporary AI with a test-only
                # app whose MockTransport deterministically exceeds the deadline.
                processes[0].terminate()
                processes[0].wait(timeout=10)
                test_environment = {**environment, "AETHRAS_TEST_LOG_DIR": str(Path(temp) / "mock-logs")}
                processes.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "tests.mocked_provider_app:app",
                                                  "--host", "127.0.0.1", "--port", str(ai_port)],
                                                 cwd=ROOT / "ai", env=test_environment, creationflags=flags))
                wait_health(ai_port)
                delayed = subprocess.run(["godot", "--headless", "--path", str(ROOT / "game/godot"),
                                          "--script", "res://tests/prompt_flow_test.gd", "--", "--expect-fallback"],
                                         env=game_environment, capture_output=True, text=True, timeout=30,
                                         creationflags=flags)
                print(delayed.stdout)
                if delayed.returncode != 0 or "SCRIPT ERROR" in delayed.stderr or "ERROR:" in delayed.stderr:
                    print(delayed.stderr)
                    raise RuntimeError("Godot delayed-provider smoke failed")
        finally:
            for process in processes:
                if process.poll() is None:
                    process.terminate()
            for process in processes:
                process.wait(timeout=10)


if __name__ == "__main__":
    main()
