# tests/stub_llm.py
from typing import Any, Optional

from crewai import BaseLLM


class StubLLM(BaseLLM):
    """LLM falso que devolve respostas em fila, na ordem das chamadas."""

    model: str = "stub-model"
    responses: list[Any] = []
    calls: list[dict] = []

    def call(
        self,
        messages: Any,
        tools: Optional[list] = None,
        callbacks: Optional[list] = None,
        available_functions: Optional[dict] = None,
        from_task: Any = None,
        from_agent: Any = None,
        response_model: Any = None,
        **kwargs: Any,
    ) -> Any:
        self.calls.append(
            {
                "messages": messages,
                "tools": tools,
                "response_model": response_model,
                "from_task": from_task,
                "from_agent": from_agent,
            }
        )

        if not self.responses:
            raise RuntimeError("StubLLM: fila de respostas vazia")

        response = self.responses.pop(0)

        # Se a task espera um modelo Pydantic, devolve instância validada
        if response_model is not None and not isinstance(response, response_model):
            if isinstance(response, dict):
                return response_model(**response)
            return response_model.model_validate(response)

        return str(response)

    def supports_function_calling(self) -> bool:
        return True