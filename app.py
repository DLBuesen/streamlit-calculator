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

PING_URL = "https://ebt-tower-pc-1.tailbd8bdf.ts.net/ping"
SOLVE_URL = "https://ebt-tower-pc-1.tailbd8bdf.ts.net/solve"

import time

st.subheader("Backend Status")

if st.button("Check backend status"):
    start = time.time()
    try:
        r = requests.get(PING_URL, timeout=2.0)
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

    try:
        response = requests.post(
            SOLVE_URL,
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

import streamlit as st
import requests
import time

st.subheader("Run Solver")

run_solver = st.button("Start computation")

if run_solver:
    progress = st.progress(0)
    status = st.empty()

    # Build payload from user inputs
    payload = {
        "x": a,
        "y": b,
        "operation": operation
    }

    with st.spinner("Running solver..."):
        start = time.time()

        try:
            r = requests.post(SOLVE_URL, json=payload, timeout=60)
            r.raise_for_status()
            result = r.json()
            duration = time.time() - start

            # Animate progress bar based on actual duration
            steps = 20
            for i in range(steps):
                time.sleep(duration / steps)
                progress.progress((i + 1) / steps)
                status.text(f"Progress: {int((i + 1) / steps * 100)}%")

            if "result" in result:
                st.success("Computation finished")
                st.write(result["result"])
            elif "error" in result:
                st.error(f"Backend error: {result['error']}")
            else:
                st.error("Unexpected response format")

        except requests.exceptions.Timeout:
            st.error("Backend timed out — try again later")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")






