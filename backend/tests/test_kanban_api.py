import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from http.client import HTTPConnection
from pathlib import Path
from typing import Optional

import pytest


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def parse_set_cookie(header: str) -> dict[str, str]:
    parts = header.split(";")
    name, value = parts[0].split("=", 1)
    return {name.strip(): value.strip()}


class ApiClient:
    def __init__(self, base_url: str, port: int):
        self.host = "127.0.0.1"
        self.port = port
        self.cookies: dict[str, str] = {}
        self.base_url = base_url

    def request(self, method: str, path: str, body: Optional[dict] = None):
        connection = HTTPConnection(self.host, self.port, timeout=10)
        payload = json.dumps(body).encode() if body is not None else None
        headers = {}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if self.cookies:
            headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.cookies.items())

        connection.request(method, path, body=payload, headers=headers)
        response = connection.getresponse()
        raw = response.read().decode()
        set_cookie = response.getheader("set-cookie")
        if set_cookie:
            self.cookies.update(parse_set_cookie(set_cookie))
        return response.status, raw

    def get(self, path: str):
        return self.request("GET", path)

    def post(self, path: str, json_body: dict):
        return self.request("POST", path, body=json_body)

    def put(self, path: str, json_body: dict):
        return self.request("PUT", path, body=json_body)

    def delete(self, path: str):
        return self.request("DELETE", path)


@pytest.fixture(scope="module")
def server_url():
    temp_dir = Path(tempfile.mkdtemp())
    port = find_free_port()
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{temp_dir / 'database.db'}"
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            conn = HTTPConnection("127.0.0.1", port, timeout=1)
            conn.request("GET", "/api/health")
            resp = conn.getresponse()
            if resp.status == 200:
                break
        except OSError:
            time.sleep(0.2)
    else:
        process.kill()
        shutil.rmtree(temp_dir)
        raise RuntimeError("Server did not start in time")

    yield port

    process.terminate()
    process.wait(timeout=10)
    shutil.rmtree(temp_dir)


@pytest.fixture()
def client(server_url):
    return ApiClient(base_url=f"http://127.0.0.1:{server_url}", port=server_url)


def test_unauthorized_access_returns_401(client):
    status, body = client.get("/api/kanban")
    payload = json.loads(body)

    assert status == 401
    assert payload["detail"] == "Not authenticated"


def test_login_creates_board_and_returns_kanban_state(client):
    status, body = client.post(
        "/api/auth/login",
        json_body={"username": "user", "password": "password"},
    )
    assert status == 200
    assert json.loads(body)["user"] == "user"

    status, body = client.get("/api/kanban")
    assert status == 200
    payload = json.loads(body)
    assert payload["name"] == "My Board"
    assert len(payload["columns"]) == 5


def test_create_update_delete_card(client):
    client.post(
        "/api/auth/login",
        json_body={"username": "user", "password": "password"},
    )

    status, body = client.get("/api/kanban")
    board_data = json.loads(body)
    first_column_id = board_data["columns"][0]["id"]

    status, body = client.post(
        "/api/kanban/cards",
        json_body={"column_id": first_column_id, "title": "New card", "details": "Details"},
    )
    assert status == 201
    card = json.loads(body)
    assert card["title"] == "New card"

    status, body = client.put(
        f"/api/kanban/cards/{card['id']}",
        json_body={"title": "Updated card", "details": "Updated details"},
    )
    assert status == 200
    assert json.loads(body)["title"] == "Updated card"

    status, _ = client.delete(f"/api/kanban/cards/{card['id']}")
    assert status == 204


def test_rename_column(client):
    client.post(
        "/api/auth/login",
        json_body={"username": "user", "password": "password"},
    )

    status, body = client.get("/api/kanban")
    board_data = json.loads(body)
    first_column_id = board_data["columns"][0]["id"]

    status, body = client.put(
        f"/api/kanban/columns/{first_column_id}",
        json_body={"title": "New Backlog"},
    )
    assert status == 200
    assert json.loads(body)["title"] == "New Backlog"
