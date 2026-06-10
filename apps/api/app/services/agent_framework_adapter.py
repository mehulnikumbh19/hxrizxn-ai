from __future__ import annotations


class MicrosoftAgentFrameworkAdapter:
    """Thin runtime probe for Microsoft Agent Framework availability.

    The MVP keeps deterministic orchestration for repeatable demos, while this adapter is
    the integration point for replacing local agent callables with MAF workflow nodes.
    """

    def __init__(self) -> None:
        try:
            import agent_framework  # type: ignore
        except Exception:  # pragma: no cover - depends on optional installed runtime
            self.available = False
            self.version = None
        else:
            self.available = True
            self.version = getattr(agent_framework, "__version__", "installed")

    def metadata(self) -> dict[str, str | bool | None]:
        return {
            "framework": "Microsoft Agent Framework",
            "package": "agent-framework",
            "available": self.available,
            "version": self.version,
            "orchestration_mode": "deterministic-workflow-compatible",
        }

