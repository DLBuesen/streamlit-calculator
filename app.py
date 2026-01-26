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

    # ---------- Session state init ----------
    if "A" not in st.session_state:
        st.session_state.A = 1.0
    if "B" not in st.session_state:
        st.session_state.B = 2.0
    if "excel_applied" not in st.session_state:
        st.session_state.excel_applied = False
    if "df" not in st.session_state:
        st.session_state.df = None

    # ---------- Excel upload (runs BEFORE widgets) ----------
    st.subheader("Batch Calculation via Excel Upload")

    uploaded_file = st.file_uploader(
        "Upload an Excel file (.xlsx) with columns A and B",
        type=["xlsx"]
    )

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)

            if not {"A", "B"}.issubset(df.columns):
                st.error("Excel file must contain columns named 'A' and 'B'.")
                st.session_state.df = None
            else:
                st.session_state.df = df
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                # ✅ Apply Excel values BEFORE widgets are created
                if not st.session_state.excel_applied:
                    st.session_state.A = float(df.iloc[0]["A"])
                    st.session_state.B = float(df.iloc[0]["B"])
                    st.session_state.excel_applied = True

        except Exception as e:
            st.error(f"Failed to read Excel file: {e}")
            st.session_state.df = None

    else:
        # Reset when no file is present
        st.session_state.df = None
        st.session_state.excel_applied = False

    st.markdown("---")

    # ---------- Manual calculator (widgets always visible) ----------
    x = st.number_input("Enter value A", key="A")
    y = st.number_input("Enter value B", key="B")
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

    # ---------- Batch computation with progress ----------
    df = st.session_state.df

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
            time.sleep(0.1)

        df = df.copy()
        df["Result"] = results
        st.success("Batch computation complete.")
        st.dataframe(df)
