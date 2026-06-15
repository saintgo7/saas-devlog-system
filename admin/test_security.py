# 상태 변경 POST 엔드포인트의 CSRF/cross-origin 방어 회귀 테스트
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))
import server  # noqa: E402

client = TestClient(server.app)

# 명령을 실제로 실행하지 않도록 존재하지 않는 슬러그를 쓴다.
# 핸들러는 경로 확인에서 404를 반환하므로 subprocess.Popen 까지 가지 않는다.
BOGUS_SLUG = "__nonexistent_test_slug__"
STATE_CHANGING = [
    f"/api/projects/{BOGUS_SLUG}/open-folder",
    f"/api/projects/{BOGUS_SLUG}/open-terminal",
    f"/api/projects/{BOGUS_SLUG}/open-vscode",
    f"/api/projects/{BOGUS_SLUG}/open-cursor",
    "/api/sync",
]


def test_bind_is_loopback_only():
    assert server.HOST == "127.0.0.1"


def test_cors_allowlist_no_wildcard():
    assert "*" not in server.ALLOWED_ORIGINS
    assert all(o.startswith("http://127.0.0.1") or o.startswith("http://localhost")
               for o in server.ALLOWED_ORIGINS)


@pytest.mark.parametrize("path", STATE_CHANGING)
def test_foreign_origin_post_rejected(path):
    res = client.post(path, headers={"origin": "http://evil.example.com"})
    assert res.status_code == 403, f"{path} should reject foreign origin"


@pytest.mark.parametrize("path", STATE_CHANGING)
def test_allowed_origin_passes_guard(path):
    # 허용 출처는 origin 가드를 통과해야 한다 (이후 404/200 등 핸들러 응답).
    res = client.post(path, headers={"origin": server.ALLOWED_ORIGINS[0]})
    assert res.status_code != 403, f"{path} should pass for allowed origin"


@pytest.mark.parametrize("path", STATE_CHANGING)
def test_no_origin_passes_guard(path):
    # 동일 출처 프론트엔드 fetch 는 origin 가드를 통과해야 한다.
    res = client.post(path)
    assert res.status_code != 403, f"{path} should pass when no origin header"


def test_read_endpoint_unaffected():
    # 읽기 전용 GET 은 가드 영향을 받지 않는다.
    res = client.get("/api/projects", headers={"origin": "http://evil.example.com"})
    assert res.status_code == 200
