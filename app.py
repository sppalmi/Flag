import time, requests, streamlit as st

CONF     = st.secrets["firebase"]
API_KEY  = CONF["apiKey"]
PROJECT  = CONF["projectId"]

# ---------- Auth ----------
def _auth_url(action: str):
    return f"https://identitytoolkit.googleapis.com/v1/accounts:{action}?key={API_KEY}"

def login(email: str, password: str):
    """Return dict with idToken, refreshToken, localId, expiresAt."""
    r = requests.post(_auth_url("signInWithPassword"), json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    r.raise_for_status()
    data = r.json()
    data["expiresAt"] = time.time() + int(data["expiresIn"]) - 60
    return data

def refresh(refresh_token: str):
    r = requests.post(
        "https://securetoken.googleapis.com/v1/token",
        params={"key": API_KEY},
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
    )
    d = r.json()
    return {
        "idToken": d["id_token"],
        "refreshToken": d["refresh_token"],
        "expiresAt": time.time() + int(d["expires_in"]) - 60,
    }

# ---------- DB ----------
def _url(path: str, token: str):
    return f"https://{PROJECT}.firebaseio.com/{path}.json?auth={token}"

def put(path: str, obj: dict, token: str):
    requests.put(_url(path, token), json=obj).raise_for_status()

def get(path: str, token: str):
    return requests.get(_url(path, token)).json()
