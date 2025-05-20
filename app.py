import streamlit as st
from streamlit_drawable_canvas import st_canvas
import uuid, time
import pyrebase

# 1 –– Firebase init
fb_conf = st.secrets["firebase"]
firebase = pyrebase.initialize_app(fb_conf)
db   = firebase.database()
auth = firebase.auth()

# 2 –– Simple login
if "user" not in st.session_state:
    with st.form("login"):
        email = st.text_input("Email")
        pw    = st.text_input("Password", type="password")
        if st.form_submit_button("Log in"):
            try:
                st.session_state.user = auth.sign_in_with_email_and_password(email, pw)
            except Exception as e:
                st.error(e)
                st.stop()

user = st.session_state.user
st.sidebar.success(user["email"])

# 3 –– Canvas designer
play_id   = st.sidebar.text_input("Play ID (load)")
play_name = st.sidebar.text_input("Play name")

canvas = st_canvas(
    fill_color="rgba(0, 0, 255, 0.3)",
    stroke_width=3,
    height=600,
    drawing_mode="freedraw",
    key="canvas",
)

# 4 –– Save / Load helpers
def save():
    pid = play_id or uuid.uuid4().hex[:6]
    db.child("plays").child(user["localId"]).child(pid).set({
        "name": play_name or f"Play {pid}",
        "doc": canvas.json_data,
        "t": int(time.time())
    })
    st.toast("Saved!", icon="✅")

def load(pid):
    data = db.child("plays").child(user["localId"]).child(pid).get().val()
    if data: st.session_state.canvas.json_data = data["doc"]

col1, col2 = st.columns(2)
if col1.button("💾 Save"): save()
if col2.button("📂 Load"): load(play_id)

