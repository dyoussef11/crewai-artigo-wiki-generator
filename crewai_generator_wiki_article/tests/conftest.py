# tests/conftest.py
import os
import socket
from pathlib import Path

import pytest

# Redireciona o SQLite/memória do CrewAI antes de importar crewai
os.environ["CREWAI_STORAGE_DIR"] = str(Path(__file__).parent / ".crewai-test-storage")
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    """Qualquer tentativa de rede vira erro imediato, não hang nem cobrança."""
    def refuse(*args, **kwargs):
        raise RuntimeError("test tried to use the network")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.chdir(tmp_path)