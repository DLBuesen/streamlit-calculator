import streamlit as st
import requests
import time

@st.cache_data(ttl=50)
def cached_backend_status(url: str) -> bool:
    try:
        r = requests.get(url, timeout=1)
        return r.status_code in (200, 400, 405)
    except Exception:
        return False

st.title("Scientific Calculator (Backend Powered)")

BACKEND_URL = "https://ebt-tower-pc-1.tailbd8bdf.ts.net/ping"

import time

st.subheader("Backend Status")

if st.button("Check backend status"):
    start = time.time()
    try:
        r = requests.get(BACKEND_URL, timeout=2.0)
        latency_ms = (time.time() - start) * 1000

        if r.status_code == 200:
            st.success(f"Backend online — {latency_ms:.1f} ms response time")
        else:
            st.error(f"Backend responded with status {r.status_code}")
    except Exception:
        st.error("Backend is offline or unreachable")




# --- Input section ---
st.subheader("Inputs")

a = st.number_input("Enter value A", value=0.0, format="%.0f")
b = st.number_input("Enter value B", value=0.0, format="%.0f")

operation = st.selectbox(
    "Choose operation",
    ["Add", "Subtract", "Multiply", "Divide"]
)

# --- Compute button ---
if st.button("Compute"):
    BACKEND_URL = "https://ebt-tower-pc-1.tailbd8bdf.ts.net/solve"

    try:
        response = requests.post(
            BACKEND_URL,
            json={"x": a, "y": b, "operation": operation}
        )

        data = response.json()

        if "result" in data:
            st.subheader("Result")
            st.write(data["result"])
        else:
            st.error(data.get("error", "Unknown error"))

    except Exception as e:
        st.error(f"Backend unreachable: {e}")

# --- Status Bar ---

st.subheader("Run Solver")

if st.button("Start computation"):
    progress = st.progress(0)
    status = st.empty()

    with st.spinner("Running solver..."):
        for i in range(100):
            time.sleep(0.1)
            progress.progress(i + 1)
            status.text(f"Progress: {i+1}%")

        # Define payload from user inputs
        payload = {
            "x": a,
            "y": b,
            "operation": operation
        }

        # Send to backend
        r = requests.post(BACKEND_URL, json=payload, timeout=60)
        result = r.json()

    st.success("Computation finished")
    st.write(result)



