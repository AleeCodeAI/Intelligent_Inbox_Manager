import streamlit as st
import requests
from datetime import datetime
import time 

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page Configuration
st.set_page_config(
    page_title="Priority Emails Manager",
    page_icon="⚡",
    layout="wide"
)

# =========================
# AI-THEMED ANIMATED CSS
# =========================
st.markdown("""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at top, #241133, #12081b 70%);
}

/* Animated header glow */
@keyframes glow {
    0% { box-shadow: 0 0 15px #6f3cff44; }
    50% { box-shadow: 0 0 30px #9a6cff88; }
    100% { box-shadow: 0 0 15px #6f3cff44; }
}

.ai-header {
    padding: 22px;
    border-radius: 14px;
    background: linear-gradient(135deg, #1f0f2e, #2b1450);
    animation: glow 4s ease-in-out infinite;
    border: 1px solid #3d226a;
}

/* Forms */
[data-testid="stForm"] {
    background: linear-gradient(180deg, #140a20, #0e0617);
    border-radius: 14px;
    padding: 26px;
    border: 1px solid #33204f;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

[data-testid="stForm"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px #00000088;
}

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background-color: #1a0f24;
    color: #e7dbff;
    border: 1px solid #3b245c;
}

/* Disabled */
.stTextInput input:disabled, .stTextArea textarea:disabled {
    background-color: #120920;
    color: #9d8bb8;
}

/* Headers */
h1, h2, h3 {
    color: #e6d9ff;
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, #ffffff, #e6e6e6);
    color: #12081b;
    font-weight: 600;
    border-radius: 10px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stButton button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 20px #ffffff55;
}

/* Expander */
details {
    background-color: #140a20;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #2f1a47;
}

/* Info */
.stAlert {
    background-color: #1a0f24;
    border: 1px solid #2d1b3d;
}

/* Subtle AI pulse line */
@keyframes scan {
    0% { opacity: 0.2; }
    50% { opacity: 0.6; }
    100% { opacity: 0.2; }
}

.ai-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #8b5cf6, transparent);
    animation: scan 3s infinite;
    margin: 25px 0;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="ai-header">
    <h1>Priority Emails — AI-Assisted Manual Queue</h1>
    <p style="color:#cfc3ff;">
        High-priority communications requiring human intelligence & precision handling.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="ai-divider"></div>', unsafe_allow_html=True)

# =========================
# FETCH EMAILS
# =========================
@st.cache_data(ttl=5)
def fetch_emails():
    try:
        r = requests.get(f"{API_BASE_URL}/priority/emails")
        if r.status_code == 200:
            return r.json().get("emails", [])
        return []
    except Exception as e:
        st.error(str(e))
        return []

def delete_email(email_id):
    try:
        r = requests.delete(
            f"{API_BASE_URL}/priority/delete",
            json={"email_id": email_id}
        )
        return r.status_code == 200
    except:
        return False

def send_email(email_id, crafted_email, classification, start=None, end=None):
    payload = {
        "email_id": email_id,
        "crafted_email": crafted_email,
        "classification": classification
    }
    if classification == "APPOINTMENT":
        payload["start"] = start
        payload["end"] = end

    r = requests.post(f"{API_BASE_URL}/priority/send", json=payload)
    return r.status_code == 200, r.json()

emails = fetch_emails()

if not emails:
    st.info("No priority emails found.")
    st.stop()

st.markdown(f"### Total Emails: {len(emails)}")
st.markdown('<div class="ai-divider"></div>', unsafe_allow_html=True)

# =========================
# EMAIL LOOP
# =========================
for i, email in enumerate(emails):
    classification = email.get("classification")
    is_appt = classification == "APPOINTMENT"

    with st.expander(
        f"Email {i+1} — {email.get('from_name')} ({email.get('from_email')})"
    ):
        with st.form(f"form_{i}"):

            st.markdown(f"**From:** [{email.get('from_email')}](mailto:{email.get('from_email')})")

            email_id = email.get("email_id")

            st.text_input("Email ID", email_id, disabled=True)
            st.markdown(f"**Classification:** `{classification}`")

            st.text_area(
                "Original Message",
                email.get("message"),
                disabled=True,
                height=140
            )

            crafted = st.text_area(
                "Response (Editable)",
                placeholder="Write a precise, professional response…",
                height=140
            )

            start_dt = end_dt = None

            if is_appt:
                st.markdown("Appointment Scheduling")
                d = st.date_input("Date")
                c1, c2 = st.columns(2)
                with c1:
                    st_t = st.time_input("Start Time", datetime.strptime("14:00","%H:%M").time())
                with c2:
                    en_t = st.time_input("End Time", datetime.strptime("15:00","%H:%M").time())

                start_dt = datetime.combine(d, st_t).strftime("%Y-%m-%dT%H:%M:%S+05:00")
                end_dt = datetime.combine(d, en_t).strftime("%Y-%m-%dT%H:%M:%S+05:00")

            col1, col2 = st.columns(2)
            del_btn = col1.form_submit_button("Delete")
            send_btn = col2.form_submit_button("Send")

            if del_btn:
                if delete_email(email_id):
                    st.success("Deleted")
                    st.cache_data.clear()
                    st.rerun()

            if send_btn:
                if not crafted.strip():
                    st.error("Response required")
                else:
                    ok, res = send_email(email_id, crafted, classification, start_dt, end_dt)
                    if ok and res.get("status") == "success":
                        st.success("Email sent successfully")
                        st.toast("Priority Email Dispatched")
                        time.sleep(1)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Send failed")

# =========================
# FOOTER
# =========================
st.markdown('<div class="ai-divider"></div>', unsafe_allow_html=True)
st.markdown("""
**Guidelines**
- Handle priority emails carefully  
- Appointment emails create calendar events automatically  
- Responses are sent immediately  
- Deleted emails are permanently removed  
""")
