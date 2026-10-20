import io
import json
from unittest.mock import patch
import pytest
from sayhuman.provider import ProviderConfig, ProviderError, generate, _NoRedirect


def test_config_validation():
    ProviderConfig("key", "model").validate()
    ProviderConfig("key", "model", "http://127.0.0.1:8000/v1").validate()
    with pytest.raises(ProviderError, match="HTTPS"):
        ProviderConfig("key", "model", "http://external.example/v1").validate()
    with pytest.raises(ProviderError, match="credentials"):
        ProviderConfig("key", "model", "https://user:pass@example.com/v1").validate()
    with pytest.raises(ProviderError, match="HTTPS"):
        ProviderConfig("key", "model", "file:///etc/passwd").validate()
    with pytest.raises(ProviderError, match="SAYHUMAN_MODEL"):
        ProviderConfig("key", "").validate()
    with pytest.raises(ProviderError, match="API_KEY"):
        ProviderConfig("", "model").validate()


class MockResponse:
    def __init__(self, data):
        self.buffer = io.BytesIO(data)
    def __enter__(self): return self
    def __exit__(self, *exc): pass
    def read(self, size=-1): return self.buffer.read(size)


class MockOpener:
    def __init__(self, response):
        self.response = response
        self.request = None
    def open(self, request, timeout):
        self.request = request
        assert timeout == 30
        return MockResponse(self.response)


def test_successful_fake_chat_completion():
    op = MockOpener(json.dumps({"choices": [{"message": {"content": "Verified response"}}]}).encode())
    with patch("sayhuman.provider.urllib.request.build_opener", return_value=op):
        assert generate("system", "user", ProviderConfig("secret", "model")) == "Verified response"
    sent = json.loads(op.request.data)
    assert sent["messages"][0]["role"] == "system"
    assert sent["messages"][1]["content"] == "user"
    assert op.request.full_url == "https://api.openai.com/v1/chat/completions"


def test_provider_bad_schema_and_excessive_response():
    with patch("sayhuman.provider.urllib.request.build_opener", return_value=MockOpener(b"{}")):
        with pytest.raises(ProviderError, match="Malformed"):
            generate("system", "user", ProviderConfig("secret", "model"))
    with patch("sayhuman.provider.urllib.request.build_opener", return_value=MockOpener(b"x" * 2_000_001)):
        with pytest.raises(ProviderError, match="2 MB"):
            generate("system", "user", ProviderConfig("secret", "model"))


def test_redirect_rejected():
    with pytest.raises(ProviderError, match="Redirect refused"):
        _NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.example/")
