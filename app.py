import html
import time

import streamlit as st

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design tokens + CSS ──────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap');

:root {
    --bg: #EDF0F5;
    --surface: #FFFFFF;
    --ink: #0F1B3D;
    --muted: #5B6785;
    --line: #D3DAE8;
    --accent: #2F4BFF;
    --accent-dark: #2339D1;
    --accent-soft: #E8ECFF;
    --mark: #FFE45C;
    --danger: #C62F3A;
}

/* ── Base ── */
html, body, .stApp, [class*="css"] {
    font-family: 'Bricolage Grotesque', system-ui, sans-serif;
    color: var(--ink);
}
.stApp {
    background-color: var(--bg);
    background-image:
        linear-gradient(rgba(15,27,61,.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(15,27,61,.045) 1px, transparent 1px);
    background-size: 32px 32px;
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 1.8rem 2.5rem 5rem; max-width: 1180px; }
.stMarkdown, .stMarkdown p, .stMarkdown li { color: var(--ink); }

/* ── Masthead + hero ── */
.brand {
    display: flex; align-items: center; gap: .6rem;
    font-weight: 700; font-size: 1.1rem; letter-spacing: -.01em;
}
.brand-mark {
    width: 22px; height: 22px; border-radius: 7px;
    background: var(--accent); position: relative;
}
.brand-mark::after {
    content: ""; position: absolute; right: 4px; bottom: 4px;
    width: 8px; height: 8px; border-radius: 50%; background: var(--mark);
}
.hero { padding: 3rem 0 1.8rem; }
.hero h1 {
    font-size: clamp(2.3rem, 4.8vw, 3.7rem);
    font-weight: 700; line-height: 1.04; letter-spacing: -.03em;
    margin: 0 0 1rem; padding: 0; max-width: 16ch; color: var(--ink);
}
.hero p {
    font-size: 1.08rem; line-height: 1.6; color: var(--muted);
    max-width: 52ch; margin: 0;
}

/* ── Search form ── */
[data-testid="stForm"] {
    background: var(--surface);
    border: 1.5px solid var(--line);
    border-radius: 18px;
    padding: .8rem;
    box-shadow: 0 1px 0 rgba(15,27,61,.04), 0 18px 36px -22px rgba(15,27,61,.3);
    transition: border-color .15s, box-shadow .15s;
}
[data-testid="stForm"]:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 4px var(--accent-soft), 0 18px 36px -22px rgba(15,27,61,.3);
}
.stTextInput [data-baseweb="input"],
.stTextInput [data-baseweb="base-input"] {
    background: transparent !important;
    border: none !important;
}
.stTextInput input {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-size: 1.15rem !important;
    height: 3.2rem;
    padding: 0 1rem !important;
    color: var(--ink) !important;
    background: transparent !important;
}
.stTextInput input::placeholder { color: #8A94AE !important; }
[data-testid="stFormSubmitButton"] button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    height: 3.2rem;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: background .15s, transform .1s;
}
[data-testid="stFormSubmitButton"] button p { color: #fff !important; }
[data-testid="stFormSubmitButton"] button:hover { background: var(--accent-dark) !important; }
[data-testid="stFormSubmitButton"] button:active { transform: scale(.98); }
[data-testid="stFormSubmitButton"] button:focus-visible {
    outline: 3px solid var(--mark) !important; outline-offset: 2px;
}

/* ── Example chips ── */
.try-label { color: var(--muted); font-size: .88rem; padding-top: .35rem; }
.st-key-chips button {
    background: transparent !important;
    border: 1px solid var(--line) !important;
    border-radius: 999px !important;
    min-height: 0 !important;
    padding: .2rem .85rem !important;
    transition: border-color .15s, color .15s;
}
.st-key-chips button p { color: var(--muted); font-size: .85rem; }
.st-key-chips button:hover { border-color: var(--accent) !important; }
.st-key-chips button:hover p { color: var(--accent); }

/* ── Pipeline stepper ── */
.stepper {
    display: grid; grid-template-columns: repeat(4, 1fr);
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1.4rem 1.5rem;
    margin: 2rem 0 2.5rem;
}
.stage { position: relative; display: flex; flex-direction: column; gap: .8rem; padding-right: 1rem; }
.stage:not(:last-child)::after {
    content: ""; position: absolute; top: 16px; left: 46px; right: 10px;
    height: 2px; background: var(--line);
}
.node {
    position: relative; z-index: 1;
    width: 34px; height: 34px; border-radius: 50%;
    display: grid; place-items: center;
    font-weight: 700; font-size: .9rem;
    background: var(--bg); color: var(--muted);
    border: 2px solid var(--line);
}
.stage-title { font-weight: 700; font-size: 1rem; }
.stage-desc { font-size: .85rem; line-height: 1.4; color: var(--muted); margin-top: .15rem; }
.stage-meta { font-size: .8rem; margin-top: .45rem; min-height: 1.1rem; color: var(--muted); }

.stage.done .node { background: var(--accent); border-color: var(--accent); color: #fff; }
.stage.done:not(:last-child)::after { background: var(--accent); }
.stage.done .stage-meta { color: var(--accent); font-weight: 600; }

.stage.running .node {
    background: var(--mark); border-color: var(--ink); color: var(--ink);
    animation: pulse 1.4s ease-out infinite;
}
.stage.running .stage-meta { color: var(--ink); font-weight: 600; }

.stage.failed .node { background: var(--danger); border-color: var(--danger); color: #fff; }
.stage.failed .stage-meta { color: var(--danger); font-weight: 600; }

@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(255,228,92,.95); }
    100% { box-shadow: 0 0 0 12px rgba(255,228,92,0); }
}
@media (prefers-reduced-motion: reduce) {
    .stage.running .node { animation: none; }
}
@media (max-width: 760px) {
    .block-container { padding: 1.2rem 1.1rem 4rem; }
    .stepper { grid-template-columns: 1fr; gap: 1.3rem; }
    .stage { flex-direction: row; align-items: flex-start; gap: 1rem; }
    .stage:not(:last-child)::after { display: none; }
}

/* ── Empty state ── */
.empty {
    border: 1.5px dashed var(--line); border-radius: 16px;
    padding: 2.2rem 1.5rem; text-align: center; color: var(--muted);
    font-size: .98rem;
}

/* ── Report ── */
.report-head h2 {
    font-size: 1.75rem; font-weight: 700; letter-spacing: -.02em;
    margin: 0; padding: 0; color: var(--ink);
}
.report-meta { display: flex; gap: 1.3rem; margin: .45rem 0 1.2rem; font-size: .9rem; color: var(--muted); }

.st-key-report_card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 2.2rem 2.6rem;
}
.st-key-report_card .stMarkdown p,
.st-key-report_card .stMarkdown li {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.14rem; line-height: 1.75; max-width: 68ch;
}
.st-key-report_card .stMarkdown h1,
.st-key-report_card .stMarkdown h2,
.st-key-report_card .stMarkdown h3,
.st-key-report_card .stMarkdown h4 {
    font-family: 'Bricolage Grotesque', sans-serif;
    letter-spacing: -.015em; color: var(--ink);
}
.st-key-report_card .stMarkdown h1 { font-size: 1.9rem; }
.st-key-report_card .stMarkdown h2 { font-size: 1.45rem; margin-top: 1.8rem; }
.st-key-report_card .stMarkdown h3 { font-size: 1.15rem; }
.st-key-report_card .stMarkdown a { color: var(--accent); }

/* ── Reviewer notes ── */
.st-key-critic_card {
    background: var(--accent-soft);
    border: 1px solid #C9D2FF;
    border-radius: 18px;
    padding: 1.6rem 1.7rem;
}
.st-key-critic_card .stMarkdown p,
.st-key-critic_card .stMarkdown li { font-size: .95rem; line-height: 1.65; }
.card-title { font-weight: 700; font-size: 1.05rem; margin-bottom: .7rem; }

/* ── Download + expanders ── */
.stDownloadButton button {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: border-color .15s;
}
.stDownloadButton button p { color: var(--ink); }
.stDownloadButton button:hover { border-color: var(--accent) !important; }

[data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--line) !important;
    border-radius: 14px !important;
    margin-top: .8rem;
}
[data-testid="stExpander"] summary p { font-weight: 600; color: var(--ink); }
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ── Pipeline definition ──────────────────────────────────────────────────────
STAGES = [
    {"key": "search", "title": "Search", "desc": "Finds recent sources on the web"},
    {"key": "reader", "title": "Read", "desc": "Opens the best source and pulls out detail"},
    {"key": "writer", "title": "Write", "desc": "Drafts the full report"},
    {"key": "critic", "title": "Review", "desc": "Scores the draft and flags gaps"},
]


def run_search(topic, res):
    agent = build_search_agent()
    out = agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    return out["messages"][-1].content


def run_reader(topic, res):
    agent = build_reader_agent()
    out = agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{res['search'][:800]}"
        )]
    })
    return out["messages"][-1].content


def run_writer(topic, res):
    research = (
        f"SEARCH RESULTS:\n{res['search']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{res['reader']}"
    )
    return writer_chain.invoke({"topic": topic, "research": research})


def run_critic(topic, res):
    return critic_chain.invoke({"report": res["writer"]})


RUNNERS = {"search": run_search, "reader": run_reader, "writer": run_writer, "critic": run_critic}


# ── Helpers ──────────────────────────────────────────────────────────────────
def compute_states(results, running=None, failed=None):
    states = {}
    for stage in STAGES:
        k = stage["key"]
        if k in results:
            states[k] = "done"
        elif k == running:
            states[k] = "running"
        elif k == failed:
            states[k] = "failed"
        else:
            states[k] = "waiting"
    return states


def stepper_html(states, timings):
    parts = []
    for i, stage in enumerate(STAGES, 1):
        k, state = stage["key"], states[stage["key"]]
        mark = {"done": "✓", "failed": "!"}.get(state, str(i))
        if state == "done" and k in timings:
            meta = f"{timings[k]:.1f}s"
        elif state == "running":
            meta = "Working…"
        elif state == "failed":
            meta = "Stopped"
        else:
            meta = ""
        parts.append(
            f'<div class="stage {state}">'
            f'<div class="node">{mark}</div>'
            f'<div><div class="stage-title">{stage["title"]}</div>'
            f'<div class="stage-desc">{stage["desc"]}</div>'
            f'<div class="stage-meta">{meta}</div></div>'
            f'</div>'
        )
    return '<div class="stepper">' + "".join(parts) + "</div>"


def use_example(text):
    st.session_state.topic_input = text


def run_pipeline(topic, slot):
    results, timings = {}, {}
    failed_key = None
    for stage in STAGES:
        key = stage["key"]
        slot.markdown(
            stepper_html(compute_states(results, running=key), timings),
            unsafe_allow_html=True,
        )
        started = time.time()
        try:
            results[key] = RUNNERS[key](topic, results)
        except Exception as exc:  # surface which step broke and why
            failed_key = key
            st.session_state.error = {
                "key": key,
                "stage": stage["title"],
                "message": str(exc),
            }
            break
        timings[key] = time.time() - started
        st.session_state.results = dict(results)
        st.session_state.timings = dict(timings)
    slot.markdown(
        stepper_html(compute_states(results, failed=failed_key), timings),
        unsafe_allow_html=True,
    )


# ── Session state ────────────────────────────────────────────────────────────
st.session_state.setdefault("results", {})
st.session_state.setdefault("timings", {})
st.session_state.setdefault("error", None)
st.session_state.setdefault("topic_ran", "")


# ── Masthead + hero ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="brand"><span class="brand-mark"></span>ResearchMind</div>
    <div class="hero">
        <h1>Research a topic. Get a reviewed report.</h1>
        <p>Agents search the web, read the best source, write the report, and
        critique it. You can follow each step as it happens.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("research_form", border=False):
    col_in, col_btn = st.columns([5, 1.25], vertical_alignment="center")
    with col_in:
        topic = st.text_input(
            "Research topic",
            placeholder="e.g. Quantum computing breakthroughs in 2025",
            key="topic_input",
            label_visibility="collapsed",
        )
    with col_btn:
        submitted = st.form_submit_button("Run research", use_container_width=True)

with st.container(key="chips"):
    c0, c1, c2, c3, _ = st.columns([0.55, 1.1, 1.35, 1.5, 3])
    c0.markdown('<div class="try-label">Try:</div>', unsafe_allow_html=True)
    for col, ex in zip((c1, c2, c3), ("LLM agents 2025", "CRISPR gene editing", "Fusion energy progress")):
        col.button(ex, key=f"chip_{ex}", on_click=use_example, args=(ex,), use_container_width=True)

if submitted and not topic.strip():
    st.warning("Enter a research topic to get started.")
    submitted = False

if submitted:
    st.session_state.results = {}
    st.session_state.timings = {}
    st.session_state.error = None
    st.session_state.topic_ran = topic.strip()


# ── Pipeline stepper (updates live while running) ────────────────────────────
stepper_slot = st.empty()
err = st.session_state.error
stepper_slot.markdown(
    stepper_html(
        compute_states(st.session_state.results, failed=err["key"] if err else None),
        st.session_state.timings,
    ),
    unsafe_allow_html=True,
)

if submitted:
    run_pipeline(topic.strip(), stepper_slot)
    err = st.session_state.error


# ── Results ──────────────────────────────────────────────────────────────────
results = st.session_state.results
timings = st.session_state.timings

if err:
    st.error(
        f"The {err['stage']} step stopped: {err['message']}  \n"
        "Check your API keys and network connection, then run it again."
    )

if "writer" in results:
    words = len(results["writer"].split())
    total = sum(timings.values())

    head_l, head_r = st.columns([4, 1.2], vertical_alignment="bottom")
    with head_l:
        st.markdown(
            f'<div class="report-head"><h2>{html.escape(st.session_state.topic_ran)}</h2>'
            f'<div class="report-meta"><span>{words:,} words</span>'
            f'<span>Finished in {total:.0f}s</span></div></div>',
            unsafe_allow_html=True,
        )
    with head_r:
        st.download_button(
            "Download report (.md)",
            data=results["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    col_report, col_critic = st.columns([2.3, 1], gap="large")
    with col_report:
        with st.container(key="report_card"):
            st.markdown(results["writer"])
    with col_critic:
        with st.container(key="critic_card"):
            st.markdown('<div class="card-title">Reviewer notes</div>', unsafe_allow_html=True)
            if "critic" in results:
                st.markdown(results["critic"])
            else:
                st.caption("The review didn't finish for this run.")

elif not results and not err:
    st.markdown(
        '<div class="empty">Enter a topic above and run the pipeline. '
        "Your report and the reviewer's notes will appear here.</div>",
        unsafe_allow_html=True,
    )

if "search" in results:
    with st.expander("Search results"):
        st.markdown(results["search"])
if "reader" in results:
    with st.expander("Scraped page content"):
        st.markdown(results["reader"])