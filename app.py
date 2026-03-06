import streamlit as st

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="F1 2026 Predictor", page_icon="🏎️")
st.title("🏎️ 2026 Australian GP Predictor")

# --- 2. THE DRIVER LIST ---
drivers = ["Oscar Piastri", "Lando Norris", "Max Verstappen", "Lewis Hamilton", "Charles Leclerc"]

# --- 3. THE PREDICTION FORM ---
# Everything below 'with st.form' MUST be indented!
with st.form("my_race_picks"):
    st.write("Pick your podium for Sunday:")
    
    # Dropdown menus for picks
    winner = st.selectbox("Who wins?", drivers)
    p2 = st.selectbox("Second Place", drivers)
    
    # The Slider for DNFs
    dnfs = st.slider("How many cars will crash/break down?", 0, 20, 2)
    
    # EVERY form needs this exact button to work
    submit_button = st.form_submit_button("Lock in Picks!")

# --- 4. THE RESULTS ---
if submit_button:
    st.balloons()
    st.success(f"Picks Saved! You've got {winner} winning with {dnfs} total DNFs.")
    