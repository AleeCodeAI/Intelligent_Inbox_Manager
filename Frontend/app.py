import streamlit as st

# ------------------------------
# Custom CSS for sidebar animations and styling
# ------------------------------
st.markdown("""
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #252525 100%);
    }

    /* AleeCodeAI branding */
    .brand-link {
        display: block;
        text-align: center;
        padding: 1.5rem 1rem;
        margin-bottom: 2rem;
        text-decoration: none;
        color: #f0f0f0; /* readable text */
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #5555aa 0%, #663366 100%);
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(50,50,80,0.3); /* softer glow */
    }

    .brand-link:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 2px 6px rgba(50,50,80,0.4);
        background: linear-gradient(135deg, #663366 0%, #5555aa 100%);
        color: #eee;
    }

    /* Navigation items animation */
    [data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }

    [data-testid="stSidebarNav"] > ul {
        padding: 0;
    }

    [data-testid="stSidebarNav"] li {
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }

    [data-testid="stSidebarNav"] li:hover {
        transform: translateX(3px);
    }

    [data-testid="stSidebarNav"] a {
        border-radius: 8px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        color: #ddd; /* readable sidebar links */
    }

    [data-testid="stSidebarNav"] a::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transition: left 0.5s ease;
    }

    [data-testid="stSidebarNav"] a:hover::before {
        left: 100%;
    }

    [data-testid="stSidebarNav"] a:hover {
        background-color: rgba(80,80,120,0.2);
        transform: scale(1.01);
    }

    /* Active page styling */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(90deg, #444488 0%, #553355 100%);
        box-shadow: 0 1px 4px rgba(50,50,80,0.5);
        color: #eee;
    }

    /* Pulse animation for active page */
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 1px 4px rgba(50,50,80,0.5);
        }
        50% {
            box-shadow: 0 1px 8px rgba(50,50,80,0.6);
        }
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] {
        animation: pulse 2s ease-in-out infinite;
    }

    /* Smooth fade-in for sidebar content */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    [data-testid="stSidebarNav"] li {
        animation: fadeIn 0.5s ease-out backwards;
    }

    [data-testid="stSidebarNav"] li:nth-child(1) { animation-delay: 0.1s; }
    [data-testid="stSidebarNav"] li:nth-child(2) { animation-delay: 0.2s; }
    [data-testid="stSidebarNav"] li:nth-child(3) { animation-delay: 0.3s; }
    [data-testid="stSidebarNav"] li:nth-child(4) { animation-delay: 0.4s; }
    [data-testid="stSidebarNav"] li:nth-child(5) { animation-delay: 0.5s; }
    [data-testid="stSidebarNav"] li:nth-child(6) { animation-delay: 0.6s; }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# AleeCodeAI branding in sidebar
# ------------------------------
with st.sidebar:
    st.markdown("""
        <a href="https://github.com/AleeCodeAI" target="_blank" class="brand-link">
            AleeCodeAI
        </a>
    """, unsafe_allow_html=True)

# ------------------------------
# Pages setup (your original code)
# ------------------------------
home = st.Page(
    page="pages/home.py",
    title="Home Page",
    default=True
)

dashboard = st.Page(
    page="pages/dashboard.py",
    title="Dashboard Analysis"
)

basic = st.Page(
    page="pages/basic.py",
    title="Basic Emails"
)

appointment = st.Page(
    page="pages/appointment.py",
    title="Appointment Emails"
)

priority = st.Page(
    page="pages/priority.py",
    title="Priority Emails"
)

nonbusiness = st.Page(
    page="pages/nonbusiness.py",
    title="Non-Business Emails"
)

pg = st.navigation(pages=[home, dashboard, basic, appointment, priority, nonbusiness])
pg.run()
