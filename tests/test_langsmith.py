from backend.services.langsmith_service import LangSmithService


def test_langsmith_is_disabled_without_credentials(monkeypatch):
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    monkeypatch.setenv("LANGSMITH_TRACING", "true")

    assert LangSmithService.run_config("L1", "mock") == {}


def test_langsmith_run_config_includes_graph_metadata(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "test-key")
    monkeypatch.setenv("LANGSMITH_PROJECT", "SecureOps-Test")

    config = LangSmithService.run_config("MANAGER", "ollama")

    assert config["run_name"] == "SecureOps Investigation"
    assert "role:manager" in config["tags"]
    assert config["metadata"]["application"] == "SecureOps-AI"
