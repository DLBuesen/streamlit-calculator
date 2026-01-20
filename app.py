import streamlit as st

st.title("Scientific Calculator")

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
    if operation == "Add":
        result = a + b
    elif operation == "Subtract":
        result = a - b
    elif operation == "Multiply":
        result = a * b
    elif operation == "Divide":
        result = a / b if b != 0 else "Error: division by zero"

    st.subheader("Result")
    st.write(result)

