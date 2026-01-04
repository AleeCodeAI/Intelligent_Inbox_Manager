import streamlit as st

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Inbox Manager",
    page_icon=None,
    layout="wide"
)

# -------------------------------------------------
# Custom CSS (AI-Style Animations)
# -------------------------------------------------
st.markdown("""
<style>

/* ------------------ Animations ------------------ */

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(16px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 rgba(138, 90, 255, 0.0); }
    50% { box-shadow: 0 0 24px rgba(138, 90, 255, 0.18); }
    100% { box-shadow: 0 0 0 rgba(138, 90, 255, 0.0); }
}

/* ------------------ Base Layout ------------------ */

.stApp {
    background: linear-gradient(
        270deg,
        #160b22,
        #1a0f24,
        #12081d
    );
    background-size: 600% 600%;
    animation: gradientShift 18s ease infinite;
}

.stMarkdown, .stText {
    color: #e6dbf2;
    animation: fadeInUp 0.6s ease-out;
}

h1, h2, h3 {
    color: #d9ccec;
    letter-spacing: 0.4px;
}

/* ------------------ Sections ------------------ */

.section-divider {
    margin: 56px 0;
    border-bottom: 1px solid #2d1b3d;
}

/* ------------------ Cards ------------------ */

.feature-card {
    background: rgba(18, 8, 29, 0.9);
    backdrop-filter: blur(6px);
    padding: 26px;
    border-radius: 16px;
    border: 1px solid #2d1b3d;
    margin-bottom: 22px;
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-6px);
    border-color: #6f4cff;
    animation: pulseGlow 2.5s infinite;
}

/* ------------------ Hero ------------------ */

.hero-subtitle {
    font-size: 1.2rem;
    color: #c4b2e3;
    margin-top: 10px;
    max-width: 620px;
}

/* ------------------ Footer ------------------ */

.footer {
    text-align: center;
    padding: 36px;
    color: #a89bb8;
    font-size: 0.9rem;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Hero Section
# -------------------------------------------------
st.markdown("""
<h1>Intelligent Inbox Manager</h1>
<div class="hero-subtitle">
AI-powered email classification, scheduling, and response automation
</div>
<br>
<p>
A production-grade system designed to reduce email overload by intelligently
prioritizing, routing, and responding to incoming messages while preserving
full human control where it matters.
</p>
""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# -------------------------------------------------
# How It Works
# -------------------------------------------------
st.header("How the System Works")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>Email Classification</h3>
        <p>Incoming emails are automatically routed into structured queues:</p>
        <ul>
            <li>High-priority business communication</li>
            <li>Non-business and personal emails</li>
            <li>General informational messages</li>
            <li>Scheduling and appointment requests</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>AI Content Understanding</h3>
        <ul>
            <li>Context and intent detection</li>
            <li>Entity extraction (dates, times, actions)</li>
            <li>Response intent analysis</li>
            <li>Professional tone alignment</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>Automated Execution</h3>
        <ul>
            <li>Drafting intelligent responses</li>
            <li>Calendar event creation</li>
            <li>Workflow orchestration</li>
            <li>External delivery via webhooks</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>Human Review Layer</h3>
        <ul>
            <li>Manual review of AI-generated drafts</li>
            <li>Editable responses before sending</li>
            <li>Safe handling of sensitive communication</li>
            <li>Manual overrides for edge cases</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# -------------------------------------------------
# Core Capabilities
# -------------------------------------------------
st.header("Core Capabilities")

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
    <div class="feature-card">
        <h3>Calendar Automation</h3>
        <ul>
            <li>Automatic meeting scheduling</li>
            <li>Google Calendar integration</li>
            <li>Conflict detection</li>
            <li>Timezone awareness</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="feature-card">
        <h3>Smart Classification</h3>
        <ul>
            <li>AI-driven prioritization</li>
            <li>Confidence-based routing</li>
            <li>Context-aware decisions</li>
            <li>Robust fallback handling</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="feature-card">
        <h3>Workflow Integration</h3>
        <ul>
            <li>n8n automation pipelines</li>
            <li>Webhook-based execution</li>
            <li>Real-time status tracking</li>
            <li>Error recovery strategies</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# -------------------------------------------------
# Technology Stack
# -------------------------------------------------
st.header("Technology Stack")

t1, t2 = st.columns(2)

with t1:
    st.markdown("""
    <div class="feature-card">
        <h3>Backend & Intelligence</h3>
        <ul>
            <li>FastAPI</li>
            <li>OpenAI language models</li>
            <li>SQLite database</li>
            <li>Pydantic validation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown("""
    <div class="feature-card">
        <h3>Frontend & Integration</h3>
        <ul>
            <li>Streamlit interface</li>
            <li>n8n workflow automation</li>
            <li>Google Calendar API</li>
            <li>Gmail API</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# -------------------------------------------------
# About Developer
# -------------------------------------------------
st.header("About the Developer")

st.markdown("""
<div class="feature-card">
    <h3>Alee</h3>
    <p><strong>Applied AI Engineer</strong></p>
    <p>
    Builder of intelligent automation systems focused on real-world productivity.
    This project emphasizes reliability, system architecture, and applied natural
    language processing rather than experimental prototypes.
    </p>
    <ul>
        <li>Artificial Intelligence & Machine Learning</li>
        <li>AI Automation Systems</li>
        <li>Backend Architecture</li>
        <li>Applied NLP</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("""
<div class="footer">
    <p>Intelligent Inbox Manager</p>
    <p>Built with Streamlit, FastAPI, and OpenAI</p>
    <p>© 2026 Alee</p>
</div>
""", unsafe_allow_html=True)
