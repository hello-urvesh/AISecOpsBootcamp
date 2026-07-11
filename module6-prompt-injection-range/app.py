"""Prompt Injection Range Streamlit entry point.

Run with:
    streamlit run app.py

This build intentionally contains only the two direct prompt injection and
jailbreak labs. The RAG lab and its dependencies have been removed.
"""
from __future__ import annotations

from typing import Callable

import streamlit as st

from core.config import APP_ICON, APP_TITLE
from core.theme import apply_cyber_theme, render_status
from labs.lab1_concierge import page as lab1_page
from labs.lab2_slowboil import page as lab2_page


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_cyber_theme()


LABS: dict[str, Callable[[], None]] = {
    "01  The Leaky Concierge": lab1_page.render,
    "02  The Slow Boil": lab2_page.render,
}


def _render_app_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            '<div class="cyber-brand">'
            '<div class="cyber-brand__eyebrow">Offensive AI Range</div>'
            f'<div class="cyber-brand__title">{APP_TITLE}</div>'
            '<div class="cyber-brand__meta">LOCAL LAB ENVIRONMENT / TWO LAB BUILD</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.divider()
        selected = st.radio(
            "Select lab",
            list(LABS.keys()),
            index=0,
            key="app_lab_selector",
        )
        st.divider()
    return selected


def main() -> None:
    selected = _render_app_sidebar()
    render_status()
    LABS[selected]()


if __name__ == "__main__":
    main()
