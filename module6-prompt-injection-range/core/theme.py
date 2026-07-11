"""Minimal cyber visual theme for the Streamlit lab."""
from __future__ import annotations

import streamlit as st


CYBER_CSS = r"""
<style>
:root {
  --bg: #071019;
  --panel: #0b1723;
  --panel-2: #0e1d2b;
  --line: #1e3445;
  --cyan: #37d6e8;
  --green: #62e6a7;
  --amber: #f0bb62;
  --red: #ff6b7a;
  --text: #e8f1f5;
  --muted: #8ba3b3;
}

.stApp {
  background:
    radial-gradient(circle at 88% 4%, rgba(55, 214, 232, 0.08), transparent 26rem),
    linear-gradient(180deg, #071019 0%, #08121c 100%);
  color: var(--text);
}

[data-testid="stHeader"] { background: rgba(7, 16, 25, 0.78); }
[data-testid="stToolbar"] { right: 1rem; }
[data-testid="stSidebar"] {
  background: #08131e;
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--muted); }

.block-container {
  max-width: 1380px;
  padding-top: 2rem;
  padding-bottom: 4rem;
}

h1, h2, h3, h4 {
  color: var(--text) !important;
  letter-spacing: -0.02em;
}
h2 { border-bottom: 1px solid var(--line); padding-bottom: 0.65rem; }

code, pre, kbd, .stCodeBlock, [data-testid="stMetricValue"] {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace !important;
}

.cyber-brand {
  border: 1px solid var(--line);
  background: linear-gradient(135deg, rgba(55, 214, 232, 0.10), rgba(98, 230, 167, 0.035));
  border-radius: 12px;
  padding: 14px 14px 12px;
  margin-bottom: 0.8rem;
}
.cyber-brand__eyebrow, .cyber-eyebrow {
  color: var(--green);
  font: 700 0.68rem/1.4 "SFMono-Regular", Consolas, monospace;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.cyber-brand__title {
  color: var(--text);
  font-size: 1.05rem;
  font-weight: 750;
  margin: 0.25rem 0;
}
.cyber-brand__meta { color: var(--muted); font-size: 0.76rem; }

.cyber-status {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  color: var(--muted);
  font: 600 0.70rem/1.4 "SFMono-Regular", Consolas, monospace;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 0 0 1.25rem;
}
.cyber-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--green);
  box-shadow: 0 0 12px rgba(98, 230, 167, 0.8);
}

[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(11, 23, 35, 0.76);
  border-color: var(--line) !important;
  border-radius: 10px !important;
}

[data-testid="stMetric"] {
  background: rgba(11, 23, 35, 0.82);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.85rem 1rem;
}
[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] { color: var(--cyan); font-size: 1.55rem; }

.stButton > button, .stDownloadButton > button {
  border: 1px solid #2c6172;
  border-radius: 8px;
  background: #0c2631;
  color: #dffbff;
  font-weight: 700;
  letter-spacing: 0.01em;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--cyan);
  color: #ffffff;
  box-shadow: 0 0 0 2px rgba(55, 214, 232, 0.10);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #117382, #126248);
  border-color: #38cbb0;
}

.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
  background: #091722 !important;
  border-color: var(--line) !important;
  color: var(--text) !important;
  border-radius: 8px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 1px var(--cyan) !important;
}

[data-testid="stExpander"] {
  background: rgba(11, 23, 35, 0.62);
  border-color: var(--line);
  border-radius: 9px;
}
[data-testid="stAlert"] { border-radius: 8px; border: 1px solid var(--line); }

.stTabs [data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { color: var(--muted); background: transparent; }
.stTabs [aria-selected="true"] { color: var(--cyan) !important; }

[data-testid="stChatMessage"] {
  background: rgba(11, 23, 35, 0.7);
  border: 1px solid var(--line);
  border-radius: 10px;
  margin-bottom: 0.65rem;
}

hr { border-color: var(--line) !important; }
a { color: var(--cyan) !important; }

@media (max-width: 780px) {
  .block-container { padding-top: 1.2rem; }
  [data-testid="stMetricValue"] { font-size: 1.2rem; }
}
</style>
"""


def apply_cyber_theme() -> None:
    st.markdown(CYBER_CSS, unsafe_allow_html=True)


def render_status(label: str = "LOCAL ATTACK RANGE") -> None:
    st.markdown(
        f'<div class="cyber-status"><span class="cyber-dot"></span>{label} / TELEMETRY ACTIVE</div>',
        unsafe_allow_html=True,
    )
