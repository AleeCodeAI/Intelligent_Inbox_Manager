import streamlit as st
import requests
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page Configuration
st.set_page_config(
    page_title="Non-Business Emails Manager",
    page_icon="📧",
    layout="wide"
)

# 🔮 Custom CSS with animations only
st.markdown("""
<style>

/* ===============================
   GLOBAL PAGE LOAD
================================ */
.stApp {
    background-color: #1a0f24;
    animation: fadeIn 0.9s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ===============================
   FORM / CARD
================================ */
[data-testid="stForm"] {
    background-color: #0f0618;
    padding: 25px;
    border-radius: 14px;
    margin-bottom: 20px;
    border: 1px solid #2d1b3d;
    transition: transform 0.35s ease, box-shadow 0.35s ease;
}

[data-testid="stForm"]:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 18px 45px rgba(155, 92, 255, 0.25);
}

/* ===============================
   EXPANDER ANIMATION
================================ */
details {
    transition: all 0.4s ease;
}

details[open] {
    animation: expandFade 0.5s ease;
}

@keyframes expandFade {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ===============================
   TEXT + HEADERS
================================ */
.stMarkdown, .stText {
    color: #e0d4f0;
}

h1, h2, h3 {
    color: #d4c5e8;
    animation: slideDown 0.6s ease;
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-6px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ===============================
   INPUTS + AI GLOW
================================ */
.stTextInput input,
.stTextArea textarea {
    background-color: #1a0f24;
    color: #e0d4f0;
    border: 1px solid #2d1b3d;
    transition: border 0.25s ease, box-shadow 0.25s ease;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border: 1px solid #9b5cff;
    box-shadow: 0 0 14px rgba(155, 92, 255, 0.45);
}

/* Disabled */
.stTextInput input:disabled,
.stTextArea textarea:disabled {
    background-color: #120920;
    color: #a89bb8;
}

/* ===============================
   BUTTONS
================================ */
.stButton button {
    background-color: #ffffff;
    color: #1a0f24;
    border: none;
    font-weight: 600;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    transition: all 0.25s ease;
}

.stButton button:hover {
    background-color: #e8e8e8;
    transform: scale(1.06);
    box-shadow: 0 0 18px rgba(255, 255, 255, 0.4);
}

/* ===============================
   INFO / ALERT PULSE
================================ */
.stAlert {
    background-color: #1a0f24;
    border: 1px solid #2d1b3d;
    animation: pulseGlow 2.5s infinite ease-in-out;
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 rgba(155, 92, 255, 0); }
    50% { box-shadow: 0 0 18px rgba(155, 92, 255, 0.35); }
    100% { box-shadow: 0 0 0 rgba(155, 92, 255, 0); }
}

/* ===============================
   DIVIDER
================================ */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(
        90deg,
        transparent,
        #9b5cff,
        transparent
    );
    animation: glowLine 2.5s infinite linear;
}

@keyframes glowLine {
    from { opacity: 0.4; }
    to { opacity: 1; }
}

</style>
""", unsafe_allow_html=True)

# Header Section
st.title("Non-Business Emails – Manual Response Queue")
st.markdown("### Non-Business Emails Requiring Attention")
st.markdown("""
This queue contains non-business emails that require manual review and response.
""")
st.markdown("---")

# Fetch emails
@st.cache_data(ttl=5)
def fetch_emails():
    try:
        response = requests.get(f"{API_BASE_URL}/nonbusiness/emails")
        if response.status_code == 200:
            return response.json().get("emails", [])
        return []
    except Exception as e:
        st.error(f"Failed to fetch emails: {str(e)}")
        return []

def delete_email(email_id):
    try:
        response = requests.delete(
            f"{API_BASE_URL}/nonbusiness/delete",
            json={"email_id": email_id}
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Delete failed: {str(e)}")
        return False

def send_email(email_id, crafted_message):
    try:
        response = requests.post(
            f"{API_BASE_URL}/nonbusiness/send",
            json={"email_id": email_id, "crafted_message": crafted_message}
        )
        if response.status_code == 200:
            return True, response.json()
        return False, {"error": response.text}
    except Exception as e:
        return False, {"error": str(e)}

emails = fetch_emails()

if not emails:
    st.info("No non-business emails found in the database.")
    st.stop()

st.markdown(f"### Total Emails: {len(emails)}")
st.markdown("---")

# Render emails
for i, email in enumerate(emails):
    with st.expander(
        f"Email {i+1} — {email.get('from_name','Unknown')} ({email.get('from_email','N/A')})"
    ):
        with st.form(key=f"form_{i}"):

            st.markdown(
                f"**From:** {email.get('from_name')} "
                f"[{email.get('from_email')}](mailto:{email.get('from_email')})"
            )

            st.text_input("Email ID", value=email.get("email_id"), disabled=True)
            st.text_input("Classification", value=email.get("classification"), disabled=True)
            st.text_area("Message", value=email.get("message"), height=150, disabled=True)

            crafted_message = st.text_area(
                "Response (Editable)",
                placeholder="Write your crafted response here...",
                height=150
            )

            col1, col2 = st.columns(2)
            delete_clicked = col1.form_submit_button("Delete")
            send_clicked = col2.form_submit_button("Send")

            if delete_clicked:
                with st.spinner("Deleting..."):
                    if delete_email(email.get("email_id")):
                        st.success("Email deleted successfully")
                        st.cache_data.clear()
                        st.rerun()

            if send_clicked:
                if not crafted_message.strip():
                    st.error("Please write a response before sending")
                else:
                    with st.spinner("Sending..."):
                        success, result = send_email(email.get("email_id"), crafted_message)
                        if success and result.get("status") == "success":
                            st.success("Email sent successfully")
                            st.cache_data.clear()
                        else:
                            st.error("Failed to send email")
                            st.info(result)

# Footer
st.markdown("---")
st.markdown("""
**Instructions**
- Review each non-business email  
- Check classification for context  
- Write a personalized response  
- Send or delete as needed  
""")
