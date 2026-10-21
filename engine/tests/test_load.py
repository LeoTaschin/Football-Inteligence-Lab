import json

import pytest

from pnsm import load


class FakeResponse:
    def __init__(self, payload):
        self.content = json.dumps(payload).encode()

    def raise_for_status(self):
        pass


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, timeout):
        self.calls.append(url)
        return FakeResponse(self.payload)


def test_fetch_downloads_once_then_reads_cache(tmp_path):
    session = FakeSession([{"match_id": 1}])

    first = load.fetch_json("matches/43/272.json", tmp_path, session)
    second = load.fetch_json("matches/43/272.json", tmp_path, session)

    assert first == second == [{"match_id": 1}]
    assert session.calls == [f"{load.BASE_URL}/matches/43/272.json"]
    assert (tmp_path / "matches/43/272.json").exists()
    assert not list(tmp_path.rglob("*.part"))


def test_cached_file_never_hits_network(tmp_path):
    cached = tmp_path / "events/1.json"
    cached.parent.mkdir()
    cached.write_text('[{"id": "a"}]', encoding="utf-8")

    class NoNetwork:
        def get(self, *args, **kwargs):
            raise AssertionError("network used for a cached file")

    assert load.fetch_json("events/1.json", tmp_path, NoNetwork()) == [{"id": "a"}]


def test_find_match_unknown_id(tmp_path):
    (tmp_path / "matches/43").mkdir(parents=True)
    (tmp_path / "matches/43/272.json").write_text('[{"match_id": 1}]', encoding="utf-8")

    with pytest.raises(KeyError):
        load.find_match(2, 43, 272, tmp_path)
