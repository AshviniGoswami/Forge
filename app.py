import streamlit as st
import json
from agents.guidelines_researcher import GuidelinesResearcher
from agents.workout_planner import WorkoutPlanner
from agents.nutrition_advisor import NutritionAdvisor
from agents.llm_judge import LLMJudge

st.set_page_config(
    page_title="FORGE - Fitness Plan Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Playfair+Display:wght@700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg:      #0e0d0b;
    --s1:      #141310;
    --s2:      #1d1b17;
    --s3:      #26231d;
    --line:    rgba(255,240,220,0.06);
    --line2:   rgba(255,240,220,0.11);
    --accent:  #e8652a;
    --accent2: #f0a050;
    --hi:      #f2ede6;
    --mid:     #9a9080;
    --lo:      #4a4438;
    --green:   #4ade80;
    --red:     #f87171;
    --amber:   #fbbf24;
}

html, body, [class*="css"], .stApp {
    background-color: var(--bg) !important;
    color: var(--hi) !important;
    font-family: 'Manrope', sans-serif !important;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background: var(--s1) !important;
    border-right: 1px solid var(--line) !important;
}
section[data-testid="stSidebar"] * { color: var(--hi) !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stTextInput > div > div > input,
section[data-testid="stSidebar"] .stMultiSelect > div > div,
section[data-testid="stSidebar"] .stTextArea > div > div > textarea {
    background: var(--s2) !important;
    border: 1px solid var(--line2) !important;
    color: var(--hi) !important;
    border-radius: 8px !important;
    font-family: 'Manrope', sans-serif !important;
}

/* inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextArea > div > div > textarea {
    background: var(--s2) !important;
    border: 1px solid var(--line2) !important;
    color: var(--hi) !important;
    border-radius: 8px !important;
    font-family: 'Manrope', sans-serif !important;
}

/* CTA button */
div[data-testid="stButton"] > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.8rem 2rem !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
div[data-testid="stButton"] > button:hover {
    background: #d4571e !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(232,101,42,0.35) !important;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--line) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--mid) !important;
    border: none !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.7rem 1.4rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--hi) !important;
    border-bottom: 2px solid var(--accent) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 2rem !important;
}

/* expander */
.streamlit-expanderHeader {
    background: var(--s2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    color: var(--hi) !important;
}
.streamlit-expanderContent {
    background: var(--s1) !important;
    border: 1px solid var(--line) !important;
    border-top: none !important;
}

/* metric */
div[data-testid="metric-container"] {
    background: var(--s2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 1.1rem !important;
}
div[data-testid="metric-container"] label {
    color: var(--mid) !important;
    font-size: 0.72rem !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 400 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: var(--hi) !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

div[data-testid="stStatus"] {
    background: var(--s2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
}
div[data-testid="stAlert"] {
    background: rgba(232,101,42,0.07) !important;
    border: 1px solid rgba(232,101,42,0.2) !important;
    border-radius: 8px !important;
    color: var(--hi) !important;
}

hr { border-color: var(--line) !important; margin: 2rem 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--s3); border-radius: 4px; }

/* ── layout helpers ── */
.page-hero {
    padding: 3.5rem 0 2.5rem;
    border-bottom: 1px solid var(--line);
    margin-bottom: 2.5rem;
}
.wordmark {
    font-family: 'Playfair Display', serif;
    font-size: 4.5rem;
    font-weight: 800;
    color: var(--hi);
    line-height: 1;
    letter-spacing: -2px;
}
.wordmark em { font-style: normal; color: var(--accent); }
.tagline {
    font-family: 'Manrope', sans-serif;
    font-size: 0.82rem;
    color: var(--mid);
    margin-top: 0.75rem;
    letter-spacing: 0.3px;
    font-weight: 400;
}
.chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--s2);
    border: 1px solid var(--line2);
    color: var(--mid);
    font-size: 0.7rem;
    font-family: 'Manrope', sans-serif;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 100px;
    margin-right: 6px;
}
.chip.purple {
    background: rgba(232,101,42,0.12);
    border-color: rgba(232,101,42,0.25);
    color: #f0a050;
}
.notice {
    background: rgba(251,191,36,0.07);
    border: 1px solid rgba(251,191,36,0.18);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    font-size: 0.82rem;
    color: #f0c060;
    margin-bottom: 2rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    line-height: 1.6;
}
.sec-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.sec-heading {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--hi);
    letter-spacing: -0.5px;
    margin: 0 0 1.75rem;
    line-height: 1.1;
}
.kpi {
    background: var(--s2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
}
.kpi-label {
    font-size: 0.72rem;
    color: var(--mid);
    font-weight: 400;
    margin-bottom: 0.45rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--hi);
    line-height: 1;
}
.week-block {
    background: var(--s2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 1.6rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.week-block:hover { border-color: var(--line2); }
.week-ghost-num {
    font-family: 'Playfair Display', serif;
    font-size: 5rem;
    font-weight: 800;
    color: var(--s3);
    line-height: 1;
    float: right;
    letter-spacing: -3px;
    margin-top: -0.5rem;
}
.week-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--hi);
    margin-bottom: 0.2rem;
}
.week-sub {
    font-size: 0.82rem;
    color: var(--mid);
}
.day-grid {
    margin-top: 1.2rem;
    display: grid;
    grid-template-columns: 68px 1fr;
    gap: 0;
}
.day-key {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 1px;
    color: var(--lo);
    text-transform: uppercase;
    padding: 0.7rem 0;
    border-bottom: 1px solid var(--line);
}
.day-val {
    padding: 0.7rem 0;
    border-bottom: 1px solid var(--line);
}
.day-grid > .day-key:nth-last-child(2),
.day-grid > .day-val:last-child {
    border-bottom: none;
}
.muscle-tag {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 0.3rem;
}
.ex-list {
    list-style: none;
    padding: 0;
    margin: 0;
}
.ex-list li {
    font-size: 0.82rem;
    color: var(--mid);
    padding: 1px 0 1px 12px;
    position: relative;
    line-height: 1.5;
}
.ex-list li::before {
    content: '·';
    position: absolute;
    left: 2px;
    color: var(--lo);
    font-size: 1rem;
}
.rest-label {
    font-size: 0.82rem;
    color: var(--lo);
    font-style: italic;
}
.meal-row {
    display: grid;
    grid-template-columns: 160px 1fr;
    gap: 0;
    padding: 1rem 0;
    border-bottom: 1px solid var(--line);
    align-items: start;
}
.meal-row:last-child { border-bottom: none; }
.meal-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.5px;
    color: var(--mid);
    text-transform: uppercase;
    padding-top: 2px;
    line-height: 1.4;
}
.meal-body {
    font-size: 0.87rem;
    color: var(--mid);
    line-height: 1.65;
}
.info-block {
    background: var(--s2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-top: 0.6rem;
}
.info-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 1.5px;
    color: var(--mid);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.tip-item {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.86rem;
    color: var(--mid);
    line-height: 1.5;
}
.tip-item:last-child { border-bottom: none; }
.tip-bullet {
    width: 4px;
    height: 4px;
    background: var(--accent);
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 8px;
    opacity: 0.7;
}
.finding-block {
    background: var(--s2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.6rem;
}
.finding-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 1px;
    color: var(--mid);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.finding-body {
    font-size: 0.87rem;
    color: var(--mid);
    line-height: 1.7;
}
.score-card {
    background: var(--s2);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 2.5rem 1.5rem;
    text-align: center;
}
.score-num {
    font-family: 'Playfair Display', serif;
    font-size: 5.5rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -4px;
}
.score-denom {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: var(--lo);
    margin-top: 0.2rem;
    letter-spacing: 1px;
}
.score-grade {
    font-family: 'Playfair Display', serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 0.75rem;
}
.verdict-block {
    background: var(--s2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    font-size: 0.9rem;
    color: var(--mid);
    line-height: 1.8;
}
.sw-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.45rem 0;
    font-size: 0.85rem;
    color: var(--mid);
    line-height: 1.5;
}
.crit-row {
    display: grid;
    grid-template-columns: 1fr 90px 42px;
    gap: 0.75rem;
    align-items: center;
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--line);
}
.crit-row:last-child { border-bottom: none; }
.crit-name {
    font-size: 0.83rem;
    color: var(--hi);
    font-weight: 400;
}
.crit-bar-track {
    height: 3px;
    background: var(--s3);
    border-radius: 2px;
    overflow: hidden;
}
.crit-bar-fill { height: 100%; border-radius: 2px; }
.crit-score {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    text-align: right;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid var(--line);
    margin: 1.25rem 0 1rem;
}
.sidebar-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--lo);
    margin-bottom: 0.75rem;
}
.warn-block {
    background: rgba(248,113,113,0.07);
    border: 1px solid rgba(248,113,113,0.18);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.83rem;
    color: #fca5a5;
    margin-bottom: 0.5rem;
}
.protocol-block {
    background: var(--s2);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-top: 0.6rem;
}
.protocol-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 1.5px;
    color: var(--lo);
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.protocol-body {
    font-size: 0.84rem;
    color: var(--mid);
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── icons (no colour-overload, just subtle white/grey) ───────
IC_WARN  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f0c060" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
IC_OK    = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
IC_NO    = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
IC_BOLT  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f0a050" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
IC_SRCH  = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9a9080" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>'
IC_DB    = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9a9080" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 5v14M18 5v14M6 9h12M6 15h12M3 8h3M18 8h3M3 16h3M18 16h3"/></svg>'
IC_LF    = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9a9080" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/></svg>'
IC_SC    = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9a9080" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z"/><path d="M7 21h10M12 3v18M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>'


def main():
    # ── sidebar ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="padding:1.25rem 0 0.5rem;">
            <div style="font-family:'Playfair Display',serif;font-size:1.6rem;font-weight:800;letter-spacing:-1px;color:#e8e8f0;">
                Forge<span style="color:#e8652a;">.</span>
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;letter-spacing:1.5px;color:#44445a;text-transform:uppercase;margin-top:3px;">
                Fitness Plan Builder
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="sidebar-divider"><div class="sidebar-label">API Keys</div>', unsafe_allow_html=True)
        gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
        tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...")

        st.markdown('<hr class="sidebar-divider"><div class="sidebar-label">Your Profile</div>', unsafe_allow_html=True)
        fitness_goal = st.selectbox("Primary Goal", [
            "Build Muscle", "Lose Weight", "Build Endurance",
            "Improve Flexibility", "General Fitness"
        ])
        fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
        age = st.slider("Age", 16, 70, 26)

        st.markdown('<hr class="sidebar-divider"><div class="sidebar-label">Training</div>', unsafe_allow_html=True)
        equipment = st.multiselect("Available Equipment", [
            "No Equipment (Bodyweight)", "Dumbbells", "Barbell & Plates",
            "Resistance Bands", "Pull-up Bar", "Kettlebells",
            "Full Gym Access", "Cardio Machines"
        ], default=["No Equipment (Bodyweight)"])
        days_per_week = st.slider("Training Days / Week", 2, 7, 4)

        st.markdown('<hr class="sidebar-divider"><div class="sidebar-label">Nutrition</div>', unsafe_allow_html=True)
        dietary_preference = st.selectbox("Dietary Preference", [
            "No Restriction", "Vegetarian", "Vegan",
            "Keto", "Mediterranean", "High Protein"
        ])
        health_notes = st.text_area("Injuries / Health Notes", placeholder="e.g., lower back pain, knee issues...")

        st.markdown('<hr class="sidebar-divider"><div class="sidebar-label">Display</div>', unsafe_allow_html=True)
        show_judge_details = st.checkbox("Show full judge rubric", value=True)

    # ── hero ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-hero">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:1.25rem;">
            {IC_BOLT}
            <span class="chip purple">AI-Powered</span>
            <span class="chip">4-Week Plan</span>
            <span class="chip">LLM-Judged</span>
        </div>
        <div class="wordmark">For<em>ge</em></div>
        <p class="tagline">Evidence-based fitness &amp; nutrition plans, validated by an independent AI judge.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="notice">
        <div style="flex-shrink:0;margin-top:1px;">{IC_WARN}</div>
        <span><strong>General wellness only not medical advice.</strong> Consult a qualified healthcare professional before starting any new fitness or nutrition program.</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Generate my 4-week plan", use_container_width=True):
        if not gemini_key or not tavily_key:
            st.error("Enter your Gemini and Tavily API keys in the sidebar.")
            return
        if not equipment:
            st.error("Select at least one equipment option.")
            return

        profile = {
            "fitness_goal": fitness_goal, "fitness_level": fitness_level,
            "age": age, "equipment": equipment, "days_per_week": days_per_week,
            "dietary_preference": dietary_preference,
            "health_notes": health_notes or "None"
        }

        researcher  = GuidelinesResearcher(gemini_key, tavily_key)
        wplanner    = WorkoutPlanner(gemini_key)
        nadvisor    = NutritionAdvisor(gemini_key)
        judge       = LLMJudge(gemini_key)

        with st.status("Running agent pipeline…", expanded=True) as ps:
            st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#44445a;">{IC_SRCH} &nbsp;01 / 04 &nbsp;Guidelines Researcher — querying Tavily…</span>', unsafe_allow_html=True)
            guidelines = researcher.research(profile)
            st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#4ade80;">✓ &nbsp;01 / 04 &nbsp;Done — {guidelines.get("sources_count", 3)} sources indexed</span>', unsafe_allow_html=True)

            st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#44445a;">{IC_DB} &nbsp;02 / 04 &nbsp;Workout Planner — building 4-week schedule…</span>', unsafe_allow_html=True)
            workout_plan = wplanner.create_plan(profile, guidelines)
            st.markdown('<span style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#4ade80;">✓ &nbsp;02 / 04 &nbsp;Done</span>', unsafe_allow_html=True)

            st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#44445a;">{IC_LF} &nbsp;03 / 04 &nbsp;Nutrition Advisor — calculating macros…</span>', unsafe_allow_html=True)
            nutrition_plan = nadvisor.create_plan(profile, guidelines)
            st.markdown('<span style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#4ade80;">✓ &nbsp;03 / 04 &nbsp;Done</span>', unsafe_allow_html=True)

            st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#44445a;">{IC_SC} &nbsp;04 / 04 &nbsp;LLM Judge — evaluating scientific soundness…</span>', unsafe_allow_html=True)
            judge_result = judge.evaluate(profile, workout_plan, nutrition_plan, guidelines)
            score = judge_result["overall_score"]
            st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;color:#4ade80;">✓ &nbsp;04 / 04 &nbsp;Done — Score: {score} / 10</span>', unsafe_allow_html=True)
            ps.update(label=f"Complete — Scientific score: {score} / 10", state="complete")

        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3, t4 = st.tabs(["Workout Plan", "Nutrition", "Research", "Judge Report"])
        with t1: render_workout(workout_plan, profile)
        with t2: render_nutrition(nutrition_plan, profile)
        with t3: render_research(guidelines)
        with t4: render_judge(judge_result, show_judge_details)


# ── renderers ─────────────────────────────────────────────────

def render_workout(wp, p):
    st.markdown(f'<div class="sec-eyebrow">Training Program</div><div class="sec-heading">{p["fitness_goal"]}<br>4-Week Protocol</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Fitness Level</div><div class="kpi-value">{p["fitness_level"]}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Training Days</div><div class="kpi-value">{p["days_per_week"]} / week</div></div>', unsafe_allow_html=True)
    with c3:
        eq = p['equipment'][0].split('(')[0].strip() if p['equipment'] else "None"
        st.markdown(f'<div class="kpi"><div class="kpi-label">Equipment</div><div class="kpi-value" style="font-size:1.2rem;">{eq}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if wp.get("overview"):
        st.markdown(f'<p style="color:var(--mid);font-size:0.9rem;line-height:1.75;margin-bottom:1.5rem;max-width:680px;">{wp["overview"]}</p>', unsafe_allow_html=True)

    for wk, wd in wp.get("weeks", {}).items():
        days_html = '<div class="day-grid">'
        for day, workout in wd.get("days", {}).items():
            if workout.get("type") == "Rest":
                content = '<div class="rest-label">Rest / active recovery</div>'
            else:
                exs = "".join([f"<li>{e}</li>" for e in workout.get("exercises", [])])
                content = f'<div class="muscle-tag">{workout.get("muscle_groups","")}</div><ul class="ex-list">{exs}</ul>'
            days_html += f'<div class="day-key">{day[:3]}</div><div class="day-val">{content}</div>'
        days_html += '</div>'

        st.markdown(f"""
        <div class="week-block">
            <div class="week-ghost-num">{wk}</div>
            <div class="week-title">{wd.get('theme', f'Week {wk}')}</div>
            <div class="week-sub">{wd.get('focus', '')}</div>
            {days_html}
        </div>""", unsafe_allow_html=True)

    for label, key in [("Warm-up Protocol", "warm_up"), ("Cool-down Protocol", "cool_down")]:
        if wp.get(key):
            st.markdown(f'<div class="protocol-block"><div class="protocol-label">{label}</div><div class="protocol-body">{wp[key]}</div></div>', unsafe_allow_html=True)


def render_nutrition(np_, p):
    st.markdown(f'<div class="sec-eyebrow">Nutrition Overview</div><div class="sec-heading">{p["dietary_preference"]}<br>Meal Structure</div>', unsafe_allow_html=True)

    macros = np_.get("macros", {})
    c1, c2, c3, c4 = st.columns(4)
    for col, lbl, val in [(c1,"Daily Calories",macros.get("calories","—")),(c2,"Protein",macros.get("protein","—")),(c3,"Carbs",macros.get("carbs","—")),(c4,"Fats",macros.get("fats","—"))]:
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{lbl}</div><div class="kpi-value" style="font-size:1.3rem;">{val}</div></div>', unsafe_allow_html=True)

    if macros.get("rationale"):
        st.markdown(f'<p style="color:var(--lo);font-size:0.8rem;margin:1rem 0 0;font-style:italic;">{macros["rationale"]}</p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-eyebrow">Daily Schedule</div>', unsafe_allow_html=True)

    meals_html = ""
    for meal_name, meal_desc in np_.get("meals", {}).items():
        parts = meal_name.split("(")
        name  = parts[0].strip()
        time  = f"({parts[1]}" if len(parts) > 1 else ""
        meals_html += f'<div class="meal-row"><div class="meal-label">{name}<br><span style="color:var(--lo);">{time}</span></div><div class="meal-body">{meal_desc}</div></div>'

    st.markdown(f'<div style="background:var(--s2);border:1px solid var(--line);border-radius:12px;padding:0.5rem 1.5rem;">{meals_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    hydration = np_.get("hydration", {})
    supps = np_.get("supplements", {})

    with ca:
        if hydration:
            st.markdown(f"""
            <div class="info-block">
                <div class="info-label">Hydration</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;color:var(--hi);margin-bottom:0.35rem;">{hydration.get('daily_target','')}</div>
                <div style="font-size:0.82rem;color:var(--mid);margin-bottom:0.25rem;">{hydration.get('training_days','')}</div>
                <div style="font-size:0.8rem;color:var(--lo);">{hydration.get('tips','')}</div>
            </div>""", unsafe_allow_html=True)

    with cb:
        if supps:
            recs = "".join([f'<div style="font-size:0.82rem;color:var(--mid);padding:5px 0;border-bottom:1px solid var(--line);">{s}</div>' for s in supps.get("recommended",[])])
            st.markdown(f"""
            <div class="info-block">
                <div class="info-label">Supplements</div>
                {recs}
                <div style="font-size:0.72rem;color:var(--lo);margin-top:0.6rem;font-style:italic;">{supps.get('disclaimer','')}</div>
            </div>""", unsafe_allow_html=True)

    if np_.get("tips"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-eyebrow" style="margin-bottom:0.75rem;">Key Principles</div>', unsafe_allow_html=True)
        items = "".join([f'<div class="tip-item"><div class="tip-bullet"></div><span>{t}</span></div>' for t in np_["tips"]])
        st.markdown(f'<div class="info-block">{items}</div>', unsafe_allow_html=True)


def render_research(g):
    st.markdown('<div class="sec-eyebrow">Evidence Base</div><div class="sec-heading">Research Findings</div>', unsafe_allow_html=True)

    for cat, body in g.get("findings", {}).items():
        st.markdown(f'<div class="finding-block"><div class="finding-label">{cat}</div><div class="finding-body">{body}</div></div>', unsafe_allow_html=True)

    if g.get("key_recommendations"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-eyebrow" style="margin-bottom:0.75rem;">Key Recommendations</div>', unsafe_allow_html=True)
        items = "".join([f'<div class="tip-item"><div class="tip-bullet"></div><span>{r}</span></div>' for r in g["key_recommendations"]])
        st.markdown(f'<div class="info-block">{items}</div>', unsafe_allow_html=True)

    if g.get("sources"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-eyebrow" style="margin-bottom:0.75rem;">Sources via Tavily</div>', unsafe_allow_html=True)
        srcs = "".join([f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.67rem;color:var(--lo);padding:0.45rem 0;border-bottom:1px solid var(--line);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{s}</div>' for s in g["sources"]])
        st.markdown(f'<div class="info-block" style="padding:0.5rem 1.2rem;">{srcs}</div>', unsafe_allow_html=True)


def render_judge(jr, show_details):
    st.markdown('<div class="sec-eyebrow">Quality Assurance</div><div class="sec-heading">LLM-as-Judge Evaluation</div>', unsafe_allow_html=True)

    score = jr.get("overall_score", 0)
    sc    = "#4ade80" if score >= 8 else "#fbbf24" if score >= 6 else "#f87171"
    grade = "Excellent" if score >= 8 else "Good" if score >= 6 else "Needs Review"

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div class="score-card">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;letter-spacing:2px;color:var(--lo);text-transform:uppercase;margin-bottom:0.75rem;">Scientific Score</div>
            <div class="score-num" style="color:{sc};">{score}</div>
            <div class="score-denom">out of 10</div>
            <div class="score-grade" style="color:{sc};">{grade}</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;letter-spacing:1px;color:var(--lo);text-transform:uppercase;margin-top:0.6rem;">Weighted 10-criterion rubric</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        if jr.get("verdict"):
            st.markdown(f'<div class="verdict-block">{jr["verdict"]}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        sa, sb = st.columns(2)
        with sa:
            st.markdown('<div class="sec-eyebrow" style="margin-bottom:0.5rem;">Strengths</div>', unsafe_allow_html=True)
            for s in jr.get("strengths", []):
                st.markdown(f'<div class="sw-item"><span style="flex-shrink:0;">{IC_OK}</span><span>{s}</span></div>', unsafe_allow_html=True)
        with sb:
            st.markdown('<div class="sec-eyebrow" style="margin-bottom:0.5rem;">To Improve</div>', unsafe_allow_html=True)
            for w in jr.get("weaknesses", []):
                st.markdown(f'<div class="sw-item"><span style="flex-shrink:0;">{IC_NO}</span><span>{w}</span></div>', unsafe_allow_html=True)

        for warn in jr.get("warnings", []):
            st.markdown(f'<div class="warn-block">{warn}</div>', unsafe_allow_html=True)

    if show_details:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-eyebrow" style="margin-bottom:0.75rem;">Criterion Breakdown</div>', unsafe_allow_html=True)

        rows = ""
        for criterion, data in jr.get("rubric_scores", {}).items():
            s  = data.get("score", 0)
            bc = "#4ade80" if s >= 8 else "#fbbf24" if s >= 6 else "#f87171"
            rows += f"""
            <div class="crit-row">
                <div class="crit-name">{criterion}</div>
                <div class="crit-bar-track"><div class="crit-bar-fill" style="width:{s*10}%;background:{bc};"></div></div>
                <div class="crit-score" style="color:{bc};">{s}/10</div>
            </div>"""

        st.markdown(f'<div class="info-block" style="padding:0.5rem 1.4rem;">{rows}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Full Rubric Definition"):
            rubric = {
                "Progressive Overload Principle": ("1.0×", "Week-over-week intensity / volume must increase. Week 4 measurably harder than Week 1."),
                "Muscle Group Balance": ("1.0×", "Push/pull volumes balanced. Anterior/posterior chain addressed without injury risk."),
                "Rest & Recovery Adequacy": ("1.0×", "48 hr minimum between same muscle groups. 1–2 rest days/week. Deload principles applied."),
                "Macro Distribution Validity": ("1.0×", "Protein 1.6–2.2 g/kg for muscle gain. Caloric target matches goal."),
                "Evidence-Based Exercise Selection": ("1.0×", "All exercises feasible with stated equipment. Compound movements form the base."),
                "Fitness Level Appropriateness": ("1.0×", "Complexity calibrated to stated level. Beginner = basics. Advanced = periodization."),
                "Dietary Preference Compliance": ("1.5× — critical", "Zero tolerance for dietary violations."),
                "Safety & Injury Consideration": ("1.5× — critical", "Health notes reflected in modifications. No contraindicated movements."),
                "Goal Alignment": ("1.0×", "Every recommendation targets the stated primary goal. No contradictory advice."),
                "Completeness & Actionability": ("1.0×", "Immediately actionable. Specific sets / reps / portions. No vague instructions."),
            }
            for crit, (wt, desc) in rubric.items():
                wc = "var(--amber)" if "critical" in wt else "var(--lo)"
                st.markdown(f'<div style="padding:0.7rem 0;border-bottom:1px solid var(--line);"><div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;"><span style="font-size:0.83rem;color:var(--hi);">{crit}</span><span style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:{wc};">{wt}</span></div><div style="font-size:0.79rem;color:var(--lo);">{desc}</div></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
