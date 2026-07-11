"""
Agentic AI Red Team: First Missions.

A beginner range with exactly two attacks. Every button says in plain words what
it does. Every attack has a story, a normal example, and a clear mission. The AI
behind it all is a real local model, so what you see is a real AI making real
choices.
"""
import streamlit as st

import theme
import progress
import agent
from ranges import RANGES, RANGE_ORDER, DIFFICULTIES, DIFF_LABEL

st.set_page_config(page_title="Agentic AI Red Team: First Missions", page_icon="\U0001F3AF", layout="wide")
theme.inject()

# ---- session defaults ------------------------------------------------------
ss = st.session_state
ss.setdefault("player", "player")
ss.setdefault("model", None)
ss.setdefault("hints_shown", {})     # per range:difficulty -> count
ss.setdefault("normal_demo", {})     # per range -> reply text
ss.setdefault("last_result", {})     # per range:difficulty -> result dict


# ---- sidebar ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### \U0001F3AF First Missions")
    st.caption("Learn to red team AI agents, one mission at a time.")
    ss.player = st.text_input("Your call sign", ss.player)

    models = agent.list_models()
    up = agent.ollama_up()
    if models:
        default_idx = models.index(ss.model) if ss.model in models else 0
        ss.model = st.selectbox("AI model powering the agents", models, index=default_idx)
    else:
        ss.model = None

    st.markdown("---")
    rec = progress.get(ss.player)
    pts = rec.get("points", 0)
    rank = progress.rank_for(pts)
    st.metric("Rank", rank)
    st.metric("Points", pts)
    nxt, need = progress.next_rank(pts)
    if nxt:
        st.caption(f"{int(need - pts)} points to reach {nxt}")

    page = st.radio("Go to", ["Home"] + [RANGES[r]["name"] for r in RANGE_ORDER] + ["My Progress"])


def model_ready():
    if not agent.ollama_up():
        st.error("The AI engine (Ollama) is not running yet. Start it, then reload this page. "
                 "See the README for the one command to run.")
        return False
    if not ss.model:
        st.warning("No AI model is installed yet. Open the Home page to install one, or run "
                   "`ollama pull llama3.1:8b` and reload.")
        return False
    return True


# ===========================================================================
# HOME
# ===========================================================================
def home():
    st.markdown("# \U0001F3AF Agentic AI Red Team: First Missions")
    st.markdown(
        "Welcome. This is a safe practice range where you learn how AI assistants can be tricked. "
        "You will face two real AI agents and try to make them break their own rules. Nothing here "
        "touches the real world. It is all a simulation for learning.")

    theme.story_block("who", "What is an AI agent?",
        "An AI agent is an AI that does not just chat. It can take actions, like sending an email, "
        "moving money, or looking up private data. That power is useful, and it is exactly what "
        "attackers try to abuse.")
    theme.story_block("rule", "What is red teaming?",
        "Red teaming means playing the attacker on purpose, in a safe setting, to find weaknesses "
        "before a real attacker does. You are the friendly attacker here.")
    theme.story_block("goal", "How this works",
        "Pick an attack from the left. Read the short story so you understand the AI and your goal. "
        "First watch the AI do its normal job. Then write your own message to try to trick it. If you "
        "succeed, you capture a flag and earn points. Each attack has three levels: Easy, Medium, and "
        "Hard.")

    st.markdown("### The two attacks")
    c1, c2 = st.columns(2)
    for col, rid in zip((c1, c2), RANGE_ORDER):
        r = RANGES[rid]
        with col:
            st.markdown(f"<div class='story'><h3>{r['emoji']} {r['name']}</h3>"
                        f"<i>{r['subtitle']}</i><br><br>{r['story']['who']}</div>",
                        unsafe_allow_html=True)

    st.markdown("### Set up the AI engine")
    if agent.ollama_up():
        st.success("AI engine is running.")
        models = agent.list_models()
        if models:
            st.write("Installed models: " + ", ".join(f"`{m}`" for m in models))
        else:
            st.info("No model installed yet. Install one below. A small 8B model works well.")
        colp1, colp2 = st.columns([3, 1])
        name = colp1.text_input("Model to install", "llama3.1:8b")
        if colp2.button("Install this model"):
            with st.spinner(f"Installing {name}. This can take a few minutes the first time."):
                agent.pull_model(name)
            st.rerun()
    else:
        st.error("AI engine (Ollama) is not reachable. Start it with the command in the README, then "
                 "reload this page.")


# ===========================================================================
# ATTACK PAGE
# ===========================================================================
def attack_page(rid):
    r = RANGES[rid]
    st.markdown(f"# {r['emoji']} {r['name']}")
    st.caption(r["subtitle"] + "  |  Attack type: " + r["attack_type"])

    s = r["story"]
    theme.story_block("who", "Meet the AI", s["who"])
    theme.story_block("who", "What it can do", s["what_it_does"])
    theme.story_block("rule", "The rule it must follow", s["the_rule"])
    theme.story_block("goal", "Your mission", s["your_mission"])
    theme.story_block("", "Normal day vs attack day", s["attack_vs_normal"])

    # ---- difficulty --------------------------------------------------------
    st.markdown("### Step 1: Choose a level")
    diff = st.radio("Levels get harder because the AI gets better defenses.",
                    DIFFICULTIES, format_func=lambda d: DIFF_LABEL[d], horizontal=False,
                    key=f"diff_{rid}")
    tag = f"{rid}:{diff}"
    solved = progress.is_solved(ss.player, rid, diff)
    st.markdown(theme.diff_pill(diff) + (
        " <span class='pill easy'>SOLVED</span>" if solved else ""), unsafe_allow_html=True)

    if not model_ready():
        return

    # ---- watch it work normally -------------------------------------------
    st.markdown("### Step 2: See the AI doing its normal job")
    st.caption("This sends an ordinary, honest message so you can see how the AI behaves when nobody "
               "is attacking it.")
    st.markdown(f"<div class='bubble-you'><b>Honest customer message:</b><br>{s['normal_example_input']}</div>",
                unsafe_allow_html=True)
    if st.button("Watch the AI work normally", key=f"normal_{rid}_{diff}"):
        with st.spinner("The AI is thinking..."):
            res = agent.run_range(r, diff, ss.model, s["normal_example_input"])
        ss.normal_demo[rid] = res
    if rid in ss.normal_demo:
        _render_ai_turn(r, ss.normal_demo[rid], normal=True)

    # ---- your attempt ------------------------------------------------------
    st.markdown("### Step 3: Your turn, try to trick the AI")
    st.caption("Write a message to the AI. Your goal is in the mission above. There is no wrong "
               "attempt. Experiment and learn.")
    placeholder = ("Type your message to the AI here. Think about how you could make it break its "
                   "rule.")
    user_msg = st.text_area("Your message to the AI", key=f"msg_{rid}_{diff}",
                            height=140, placeholder=placeholder)
    cbtn1, cbtn2 = st.columns([1, 3])
    if cbtn1.button("Send my message to the AI", key=f"send_{rid}_{diff}", type="primary"):
        if not user_msg.strip():
            st.warning("Write a message first.")
        else:
            with st.spinner("The AI is reading your message and deciding what to do..."):
                res = agent.run_range(r, diff, ss.model, user_msg)
            ss.last_result[tag] = res
            if res.get("success"):
                first, total, rank = progress.solve(ss.player, rid, diff, r["points"][diff])
                res["_first"] = first
                res["_flag"] = f"FLAG{{{rid}_{diff}_solved}}"
                res["_points"] = r["points"][diff]

    if tag in ss.last_result:
        st.markdown("#### What happened")
        st.markdown(f"<div class='bubble-you'><b>You said:</b><br>"
                    f"{st.session_state.get('msg_'+rid+'_'+diff,'')}</div>", unsafe_allow_html=True)
        _render_ai_turn(r, ss.last_result[tag], normal=False)
        _render_outcome(r, diff, ss.last_result[tag])

    # ---- hints -------------------------------------------------------------
    st.markdown("### Stuck? Get a hint")
    st.caption("Hints appear one at a time and get more specific. Try on your own first.")
    shown = ss.hints_shown.get(tag, 0)
    hints = r["hints"][diff]
    for i in range(shown):
        st.info(f"Hint {i+1}: {hints[i]}")
    if shown < len(hints):
        if st.button(f"Show hint {shown+1} of {len(hints)}", key=f"hint_{rid}_{diff}"):
            ss.hints_shown[tag] = shown + 1
            st.rerun()
    else:
        st.caption("No more hints. You have everything you need.")


def _render_ai_turn(r, res, normal):
    if r["id"] == "range_a":
        reply = res.get("reply", "")
        action = res.get("action", "none")
        amount = res.get("amount", 0)
        line = f"<div class='bubble-ai'><b>Ava replies:</b><br>{reply}"
        if action == "issue_credit":
            line += f"<br><br><b>Action taken:</b> credit {amount:g} dollars to the account."
        else:
            line += "<br><br><b>Action taken:</b> none."
        line += "</div>"
        st.markdown(line, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bubble-ai'><b>Miles replies:</b><br>{res.get('reply','')}</div>",
                    unsafe_allow_html=True)


def _render_outcome(r, diff, res):
    if res.get("success"):
        st.markdown(f"<div class='win'><b>Mission accomplished.</b> You made the AI break its rule.</div>",
                    unsafe_allow_html=True)
        _explain(r, diff, res, won=True)
        st.markdown(f"<div class='flag'>Flag captured: {res.get('_flag','')}   "
                    f"+{res.get('_points',0)} points"
                    f"{'  (first time)' if res.get('_first') else '  (already earned)'}</div>",
                    unsafe_allow_html=True)
        if res.get("_first"):
            st.balloons()
    else:
        if res.get("blocked"):
            st.markdown(f"<div class='lose'><b>So close.</b> The AI was about to do it, but the second "
                        f"AI reviewer stopped it. Reviewer note: {res.get('blocked_reason','')}</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown("<div class='lose'><b>Not yet.</b> The AI followed its rules this time. "
                        "Try a different approach.</div>", unsafe_allow_html=True)
        _explain(r, diff, res, won=False)


def _explain(r, diff, res, won):
    """Plain language explanation of why it worked or did not."""
    if r["id"] == "range_a":
        if won and res.get("stage") == "reviewer":
            msg = ("You convinced Ava to propose a large credit, and your reason was believable enough "
                   "that the second AI fraud reviewer approved it too. In the real world this is money "
                   "stolen through prompt injection.")
        elif won:
            msg = ("Ava treated your message as a command instead of untrusted customer text, and "
                   "issued a credit far above the 50 dollar limit. That is prompt injection turning "
                   "into a real financial action.")
        elif res.get("blocked"):
            msg = ("Ava was manipulated, but the fraud reviewer caught it. On Hard you need a story "
                   "that also looks legitimate to a reviewer, not just to Ava.")
        else:
            msg = ("Ava either refused or kept the credit within policy. Its defenses held. Look at the "
                   "hints for how to make your request override its rules.")
    else:
        if won and res.get("stage") == "reviewer":
            form = res.get("leak_form", "a disguised")
            msg = (f"Miles leaked the code in {form} form, and the security filter did not catch it. "
                   "Since you can rebuild the real code from it, the secret is effectively exposed.")
        elif won:
            msg = ("Miles revealed the secret code it was supposed to protect. Getting an AI to spill "
                   "protected information is called sensitive information disclosure.")
        elif res.get("blocked"):
            msg = ("Miles leaked the code, but the security filter blocked the reply before it reached "
                   "you. On Hard, leak it in a form the filter misses but you can still rebuild.")
        else:
            msg = ("Miles kept the secret. Its defenses held. The hints show indirect ways to ask that "
                   "are harder to refuse.")
    st.markdown(f"<div class='story'>{msg}</div>", unsafe_allow_html=True)


# ===========================================================================
# PROGRESS
# ===========================================================================
def my_progress():
    st.markdown("# \U0001F396 My Progress")
    rec = progress.get(ss.player)
    pts = rec.get("points", 0)
    c1, c2, c3 = st.columns(3)
    c1.metric("Call sign", ss.player)
    c2.metric("Rank", progress.rank_for(pts))
    c3.metric("Points", pts)

    st.markdown("### Mission board")
    for rid in RANGE_ORDER:
        r = RANGES[rid]
        cells = []
        for d in DIFFICULTIES:
            done = progress.is_solved(ss.player, rid, d)
            mark = "SOLVED" if done else "open"
            css = "easy" if done else "hard"
            cells.append(f"<span class='pill {css}'>{d.upper()}: {mark}</span>")
        st.markdown(f"<div class='story'><b>{r['emoji']} {r['name']}</b><br>{''.join(cells)}</div>",
                    unsafe_allow_html=True)

    st.markdown("### Leaderboard")
    lb = progress.leaderboard()
    if lb:
        st.dataframe(lb, use_container_width=True)
    else:
        st.caption("No missions solved yet. Be the first.")


# ---- router ----------------------------------------------------------------
if page == "Home":
    home()
elif page == "My Progress":
    my_progress()
else:
    rid = next(r for r in RANGE_ORDER if RANGES[r]["name"] == page)
    attack_page(rid)
