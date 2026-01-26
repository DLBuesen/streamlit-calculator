import streamlit as st
import requests
import time
import pandas as pd

PING_URL = "https://ebt-tower-pc-1.tailbd8bdf.ts.net/ping"
SOLVE_URL = "https://ebt-tower-pc-1.tailbd8bdf.ts.net/solve"

st.title("Scientific Calculator (Backend Powered)")

tab1, tab2 = st.tabs(["Backend Status", "Calculator"])

# ------------------------- TAB 1 — Backend Status -------------------------

with tab1:
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

# ------------------------- TAB 2 — Calculator -------------------------

with tab2:
    st.header("Calculator")

    # -------------------------
    # Session defaults
    # -------------------------
    if "A_default" not in st.session_state:
        st.session_state.A_default = 1
    if "B_default" not in st.session_state:
        st.session_state.B_default = 2
    if "excel_loaded" not in st.session_state:
        st.session_state.excel_loaded = False

    # -------------------------
    # Manual calculator
    # -------------------------
    x = st.number_input("Enter value A", value=st.session_state.A_default, key="A")
    y = st.number_input("Enter value B", value=st.session_state.B_default, key="B")
    operation = st.selectbox("Choose operation", ["Add", "Subtract", "Multiply", "Divide"])

    if st.button("Start Computation"):
        payload = {"x": x, "y": y, "operation": operation}
        try:
            r = requests.post(SOLVE_URL, json=payload, timeout=10)
            r.raise_for_status()
            result = r.json().get("result")
            st.success(f"Result: {result}")
        except Exception as e:
            st.error(f"Request failed: {e}")

    st.markdown("---")

    # -------------------------
    # Excel Upload
    # -------------------------
    st.subheader("Batch Calculation via Excel Upload")

    uploaded_file = st.file_uploader(
        "Upload an Excel file (.xlsx) with columns A and B",
        type=["xlsx"]
    )

    df = None

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)

            if not {"A", "B"}.issubset(df.columns):
                st.error("Excel file must contain columns named 'A' and 'B'.")
            else:
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                # Auto‑populate A/B only once per upload
                if not st.session_state.excel_loaded:
                    st.session_state.A_default = float(df.iloc[0]["A"])
                    st.session_state.B_default = float(df.iloc[0]["B"])
                    st.session_state.excel_loaded = True
                    st.rerun()

        except Exception as e:
            st.error(f"Failed to read Excel file: {e}")

    # -------------------------
    # Batch computation
    # -------------------------
    if df is not None and st.button("Run Batch Computation"):
        results = []
        progress = st.progress(0)
        status = st.empty()

        def safe_solve(payload, retries=3, delay=1):
            for attempt in range(retries):
                try:
                    r = requests.post(SOLVE_URL, json=payload, timeout=10)
                    r.raise_for_status()
                    return r.json().get("result")
                except Exception as e:
                    time.sleep(delay)
            return f"Error: {e}"

        for i, row in enumerate(df.itertuples(index=False), start=1):
            payload = {
                "x": float(row.A),
                "y": float(row.B),
                "operation": operation
            }
            result = safe_solve(payload)
            results.append(result)

            progress.progress(i / len(df))
            status.text(f"Progress: {int(i / len(df) * 100)}%")
            time.sleep(0.2)

        df["Result"] = results
        st.success("Batch computation complete.")
        st.dataframe(df)
