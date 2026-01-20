import streamlit as st
import requests

@st.cache_data(ttl=5)
def cached_backend_status(url: str) -> bool:
    try:
        r = requests.get(url, timeout=1)
        return r.status_code in (200, 400, 405)
    except Exception:
        return False

st.title("Scientific Calculator (Backend Powered)")

BACKEND_URL = "https://ebt-tower-pc-1.tailbd8bdf.ts.net/solve"

if cached_backend_status(BACKEND_URL):
    st.success("Backend is online and reachable")
else:
    st.error("Backend is offline or unreachable")



# --- Input section ---
st.subheader("Inputs")

a = st.number_input("Enter value A", value=0.0, format="%.6f")
b = st.number_input("Enter value B", value=0.0, format="%.6f")

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


