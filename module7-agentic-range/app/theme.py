"""Beginner friendly dark red theme and small UI helpers."""
import streamlit as st

CSS = """
<style>
html, body, [class*="css"] { font-family: 'Inter','Segoe UI',system-ui,sans-serif; }
.stApp { background:
  radial-gradient(1100px 500px at 15% -10%, #23070c 0%, #0b0b0e 55%); color:#eaeaea; }
h1,h2,h3 { color:#fafafa; }
h1 { border-bottom:2px solid #7f1420; padding-bottom:10px; }
.story { background:#15151a; border:1px solid #2a2a31; border-radius:10px;
  padding:16px 18px; margin:10px 0; line-height:1.55; }
.story b { color:#ff6b6b; }
.goal { border-left:4px solid #16a34a; }
.rule { border-left:4px solid #f59e0b; }
.who  { border-left:4px solid #e11d2a; }
.step-num { display:inline-block; width:26px; height:26px; line-height:26px; text-align:center;
  border-radius:50%; background:#7f1420; color:#fff; font-weight:700; margin-right:8px; }
.pill { display:inline-block; padding:3px 12px; border-radius:14px; font-size:12px;
  border:1px solid #333; margin:2px 6px 2px 0; }
.easy { color:#7CFC00; border-color:#2f5d2f; }
.medium { color:#ffcc00; border-color:#6b5a12; }
.hard { color:#ff5a5a; border-color:#7f1420; }
.win { background:#0c1f0c; border:1px solid #16a34a; border-radius:10px; padding:14px; }
.lose { background:#1f0c0c; border:1px solid #7f1420; border-radius:10px; padding:14px; }
.flag { background:#0d0d10; border:1px dashed #16a34a; color:#7CFC00; padding:10px;
  border-radius:8px; font-family:monospace; font-size:15px; }
.stButton>button { background:#7f1420; color:#fff; border:1px solid #e11d2a; border-radius:8px;
  font-weight:600; padding:8px 14px; }
.stButton>button:hover { background:#e11d2a; border-color:#fff; }
.bubble-ai { background:#141821; border:1px solid #2a2f3a; border-radius:12px 12px 12px 2px;
  padding:12px 14px; margin:6px 0; }
.bubble-you { background:#1c1420; border:1px solid #3a2a35; border-radius:12px 12px 2px 12px;
  padding:12px 14px; margin:6px 0; }
</style>
"""

def inject():
    st.markdown(CSS, unsafe_allow_html=True)

def story_block(css_class, title, body):
    st.markdown(f"<div class='story {css_class}'><b>{title}</b><br>{body}</div>",
                unsafe_allow_html=True)

def diff_pill(d):
    return f"<span class='pill {d}'>{d.upper()}</span>"
