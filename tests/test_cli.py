import json
from sayhuman.cli import main, build_parser, run
from sayhuman.provider import ProviderError
import pytest


def test_cli_help_and_list(capsys):
    assert main(["list"]) == 0
    assert "Quantization" in capsys.readouterr().out
    assert main(["explain", "RAG", "--format", "json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert "does not eliminate" in result["caveat"]


def test_cli_unknown_returns_2(capsys):
    assert main(["explain", "nonexistent-system"]) == 2
    assert "--llm" in capsys.readouterr().err


def test_cli_stdin(monkeypatch):
    import io, sys
    monkeypatch.setattr(sys, "stdin", io.StringIO("touch base"))
    arg = build_parser().parse_args(["decode", "--stdin", "--format", "json"])
    result = json.loads(run(arg))
    assert result["matches"][0]["phrase"] == "touch base"


def test_cli_rejects_empty_and_oversized(capsys):
    assert main(["encode", ""]) == 2
    assert main(["encode", "x" * 50001]) == 2
    assert "50,000" in capsys.readouterr().err


def test_llm_prompt_contains_all_gold_stories(monkeypatch):
    from sayhuman import cli
    from sayhuman.content import gold_examples
    captured = {}
    def fake_generate(system, user):
        captured["system"] = system
        captured["user"] = user
        return "A tested fake response"
    monkeypatch.setattr(cli, "generate", fake_generate)
    assert main(["explain", "new term", "--llm", "--audience", "cfo"]) == 0
    assert all(e["metaphor_translation"] in captured["system"] for e in gold_examples())
    assert "Audience: cfo" in captured["user"]
    assert "<untrusted_input>" in captured["user"]


def test_json_llm_wrapper(monkeypatch, capsys):
    from sayhuman import cli
    monkeypatch.setattr(cli, "generate", lambda *a: "not structured json")
    assert main(["decode", "Hello", "--llm", "--format", "json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["source"] == "configured-remote-llm"
    assert isinstance(result["result"], str)


def test_provider_failure_exit(monkeypatch, capsys):
    from sayhuman import cli
    def error(*args):
        raise ProviderError("No model configured")
    monkeypatch.setattr(cli, "generate", error)
    assert main(["explain", "Hi", "--llm"]) == 2
    assert "No model configured" in capsys.readouterr().err
