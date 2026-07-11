"""Reusable Streamlit components shared across labs.

Lab 1 keeps its original inline UI helpers. Lab 2 and later should pull from
this module so common Streamlit patterns and Ollama error handling are not
reimplemented in every lab.
"""
from __future__ import annotations

import time
from typing import Any

import streamlit as st

from core.config import DEFAULT_MODEL
from core.conversation import Conversation
from core.logging import JSONLLogger
from core.ollama_client import (
    GenerationParams,
    OllamaConnectionError,
    OllamaModelError,
    OllamaService,
)


@st.cache_resource(show_spinner=False)
def get_ollama_service() -> OllamaService:
    """Return one cached Ollama service per Streamlit server process."""
    return OllamaService()


def render_model_picker(
    svc: OllamaService,
    label: str = "Model",
    key: str = "model",
    default: str = DEFAULT_MODEL,
    container: Any = None,
) -> str | None:
    """Render a selectbox of installed Ollama models.

    Returns None if Ollama is unreachable or no local models are installed.
    """
    target = container if container is not None else st
    try:
        models = svc.list_models()
    except OllamaConnectionError as e:
        target.error(str(e))
        return None

    if not models:
        target.error(
            "No Ollama models found locally. Pull one with: "
            "`ollama pull llama3.1:8b`"
        )
        return None

    default_idx = models.index(default) if default in models else 0
    return target.selectbox(label, models, index=default_idx, key=key)


def render_generation_params(
    key_prefix: str = "params",
    expanded: bool = False,
    container: Any = None,
) -> GenerationParams:
    """Render common generation knobs and return GenerationParams."""
    target = container if container is not None else st
    with target.expander("Generation parameters", expanded=expanded):
        temp = st.slider(
            "Temperature", 0.0, 2.0, 0.7, 0.1, key=f"{key_prefix}_temp"
        )
        top_p = st.slider(
            "Top-p", 0.0, 1.0, 0.9, 0.05, key=f"{key_prefix}_top_p"
        )
        num_ctx = st.select_slider(
            "Context window",
            options=[2048, 4096, 8192, 16384],
            value=4096,
            key=f"{key_prefix}_ctx",
        )
        seed_str = st.text_input(
            "Seed (optional, integer)", value="", key=f"{key_prefix}_seed"
        )
        seed = int(seed_str) if seed_str.strip().lstrip("-").isdigit() else None
    return GenerationParams(
        temperature=temp,
        top_p=top_p,
        num_ctx=num_ctx,
        seed=seed,
    )


def stream_chat_into_placeholder(
    svc: OllamaService,
    model: str,
    messages: list[dict[str, str]],
    params: GenerationParams,
    placeholder: Any,
) -> tuple[str, int, str | None]:
    """Stream tokens into an st.empty placeholder.

    Returns (text, latency_ms, error). Never raises.
    """
    accumulated = ""
    error: str | None = None
    start = time.perf_counter()
    try:
        for chunk in svc.chat_stream(model, messages, params):
            accumulated += chunk
            placeholder.markdown(accumulated + " ▌")
        placeholder.markdown(accumulated if accumulated else "_(empty response)_")
    except OllamaConnectionError as e:
        error = f"Ollama connection error: {e}"
        placeholder.error(error)
    except OllamaModelError as e:
        error = str(e)
        placeholder.error(error)
    except Exception as e:
        error = f"Unexpected error: {e}"
        placeholder.error(error)
    latency_ms = int((time.perf_counter() - start) * 1000)
    return accumulated, latency_ms, error


def chat_complete_blocking(
    svc: OllamaService,
    model: str,
    messages: list[dict[str, str]],
    params: GenerationParams,
) -> tuple[str, int, str | None]:
    """Run a full chat call and return text, latency_ms, error."""
    accumulated = ""
    error: str | None = None
    start = time.perf_counter()
    try:
        for chunk in svc.chat_stream(model, messages, params):
            accumulated += chunk
    except OllamaConnectionError as e:
        error = f"Ollama connection error: {e}"
    except OllamaModelError as e:
        error = str(e)
    except Exception as e:
        error = f"Unexpected error: {e}"
    latency_ms = int((time.perf_counter() - start) * 1000)
    return accumulated, latency_ms, error


def render_conversation(
    conv: Conversation,
    hide_system: bool = True,
    empty_msg: str = "No messages yet.",
) -> None:
    """Render a Conversation as Streamlit chat messages."""
    msgs = conv.visible_messages() if hide_system else conv.messages
    if not msgs:
        st.info(empty_msg)
        return
    for msg in msgs:
        with st.chat_message(msg.role):
            st.markdown(msg.content)


def render_message_array(messages: list[dict[str, str]]) -> None:
    """Render a raw message list, including the system role."""
    if not messages:
        st.info("Empty message array.")
        return
    for m in messages:
        role = m.get("role", "?")
        content = m.get("content", "")
        chat_role = role if role in {"system", "user", "assistant"} else "user"
        with st.chat_message(chat_role):
            st.markdown(f"**[{role}]**\n\n{content}")


def render_telemetry_panel(
    logger: JSONLLogger,
    success_field: str = "jailbroken",
    limit: int = 50,
    extra_summary_metrics: list[tuple[str, Any]] | None = None,
) -> None:
    """Render a reusable telemetry panel for a lab."""
    events = logger.read_all()
    success_count = sum(1 for e in events if e.get(success_field))

    metrics = [
        ("Events logged", len(events)),
        ("Successes", success_count),
    ]
    if extra_summary_metrics:
        metrics.extend(extra_summary_metrics)

    cols = st.columns(max(1, len(metrics)))
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)

    if not events:
        st.caption("No events logged yet.")
        return

    st.markdown(f"**Most recent {min(len(events), limit)} events** (newest first)")
    for e in reversed(events[-limit:]):
        is_success = bool(e.get(success_field))
        badge = "🚨" if is_success else "."
        ts = e.get("ts", "")
        mode = e.get("mode") or e.get("template") or "?"
        model = e.get("target_model") or e.get("model") or "?"
        latency = e.get("latency_ms", "?")
        verdict = e.get("verdict", "")

        with st.container(border=True):
            st.markdown(
                f"{badge} `{ts}` . mode `{mode}` . target `{model}` . "
                f"verdict `{verdict}` . latency `{latency}` ms"
            )
            t_event, t_payload, t_response = st.tabs(
                ["Event", "Last user input", "Last response"]
            )
            with t_event:
                st.json(e)
            with t_payload:
                st.code(e.get("user_input", "") or "(none)", language="text")
            with t_response:
                st.code(e.get("assistant_output", "") or "(none)", language="text")
