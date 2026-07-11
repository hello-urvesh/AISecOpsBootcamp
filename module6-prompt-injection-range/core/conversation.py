"""Typed conversation state for chat-style labs.

The system prompt is treated as immutable once set on construction; reset()
re-installs it as the leading message. This intentionally exposes the full
message array — Lab 2's CCA (Context Compliance Attack) demo will rely on
the fact that locally-hosted chat state is always client-side mutable.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal

Role = Literal["system", "user", "assistant"]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass
class Message:
    role: Role
    content: str
    timestamp: str = field(default_factory=_utc_now_iso)

    def to_ollama(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class Conversation:
    """Ordered message list with a stable system-prompt anchor."""
    system_prompt: str
    messages: list[Message] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.messages or self.messages[0].role != "system":
            self.messages.insert(0, Message(role="system", content=self.system_prompt))

    def add_user(self, content: str) -> None:
        self.messages.append(Message(role="user", content=content))

    def add_assistant(self, content: str) -> None:
        self.messages.append(Message(role="assistant", content=content))

    def to_ollama_format(self) -> list[dict[str, str]]:
        return [m.to_ollama() for m in self.messages]

    def reset(self) -> None:
        """Drop all turns, keep the original system prompt."""
        self.messages = [Message(role="system", content=self.system_prompt)]

    def visible_messages(self) -> list[Message]:
        """Messages a user/attacker should see (everything except the system turn)."""
        return [m for m in self.messages if m.role != "system"]

    def turn_count(self) -> int:
        """Number of user turns sent so far."""
        return sum(1 for m in self.messages if m.role == "user")
