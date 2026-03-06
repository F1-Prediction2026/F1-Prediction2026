import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
try:
    from streamlit_extras.let_it_rain import rain
except:
    pass

# 1. PAGE SETUP
st.set_page_config(page_title="F1 2026 World League", page_icon="🏎️", layout="wide")

# 2. GOOGLE SHEET SETTINGS
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lv0DINT8fe1KrEWewDImqW7FEVMOWLALq5yKtdX04ac/edit#gid=0"

# 3. SEASON DATA
races_2026 = [
    {"name": "Australia", "date": "Mar 8"}, {"name": "China", "date": "Mar 15"},
    {"name": "Japan", "date": "Mar 29"}, {"name": "Bahrain", "date": "Apr 12"},
    {"name": "Saudi Arabia", "date": "Apr 19"}, {"name": "Miami", "date": "May 3"},
    {"name": "Canada", "date": "May 24"}, {"name": "Monaco", "date": "Jun 7"},
    {"name": "Spain", "date": "Jun 14"}, {"name": "Austria", "date": "Jun 28"},
    {"name": "Britain", "date": "Jul 5"}, {"name": "Belgium", "date": "Jul 19"},
    {"name": "Hungary", "date": "Jul 26"}, {"name": "Netherlands", "date": "Aug 23"},
    {"name": "Italy", "date": "Sep 6"}, {"name": "Baku", "date": "Sep 20"},
    {"name": "Singapore", "date": "Oct 11"}, {"name": "Austin", "date": "Oct 25"},
    {"name": "Mexico", "date": "Nov 1"}, {"name": "Brazil", "date": "Nov 8"},
    {"name": "Vegas", "date": "Nov 22"}, {"name": "Qatar", "date": "Nov 29"},
    {"name": "Abu Dhabi", "date": "Dec 6"}
]

drivers_list = [
    "-- Select Driver --", "L. Norris (McLaren)", "O. Piastri (McLaren)", 
    "M. Verstappen (Red Bull)", "C. Leclerc (Ferrari)", "L. Hamilton (Ferrari)", 
    "K. Antonelli (Mercedes)", "G. Russell (Mercedes)", "C. Sainz (Williams)", 
    "F. Alonso (Aston Martin)", "N. Hülkenberg (Audi)", "S. Pérez (Cadillac)"
]

# 4. APP MEMORY (Session State)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'active_race' not in st.session_state: st.session_state.active_race = None

# --- PAGE 1: LOGIN ---
if not st.session_state.auth:
    st.title("🏁 F1 2026 Season Login")
    with st.container(border=True):
        u = st.text_input("Username", key="user_in")
        p = st.text_input("League Password", type="password", key="pwd_in")
        if st.button("Enter Paddock"):
            if p == "f12026" and u:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials. Try 'f12026'")

# --- PAGE 2: AUTHENTICATED DASHBOARD ---
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Race Selection", "Season Standings", "My History"])
    conn = st.connection("gsheets", type=GSheetsConnection)

    # --- SUB-PAGE: RACE SELECTION ---
    if menu == "Race Selection":
        st.header("🏁 2026 Race Calendar")
        st.write("Click a race to lock in your picks:")
        
        cols = st.columns(4)
        for i, race in enumerate(races_2026):
            if cols[i % 4].button(f"🏁 {race['name']}\n{race['date']}", key=f"btn_{race['name']}"):
                st.session_state.active_race = race['name']
        
        if st.session_state.active_race:
            st.divider()
            with st.form("prediction_form", clear_on_submit=True):
                st.subheader(f"Picks for {st.session_state.active_race}")
                p1 = st.selectbox("Race Winner (P1)", drivers_list)
                p2 = st.selectbox("Second Place (P2)", drivers_list)
                p3 = st.selectbox("Third Place (P3)", drivers_list)
                pit = st.selectbox("Fastest Pit Stop Team", ["Red Bull", "Ferrari", "McLaren", "Mercedes", "Audi", "Cadillac"])
                
                submitted = st.form_submit_button("Lock in Picks")
                
                if submitted:
                    new_pick = pd.DataFrame([{
                        "User": st.session_state.user,
                        "Race": st.session_state.active_race,
                        "P1": p1, "P2": p2, "P3": p3, "Pit": pit, "Points": 0
                    }])
                    try:
                        # Connect and Update Google Sheet
                        existing = conn.read(spreadsheet=SHEET_URL, worksheet="Picks", ttl=0)
                        updated = pd.concat([existing, new_pick], ignore_index=True)
                        conn.update(spreadsheet=SHEET_URL, worksheet="Picks", data=updated)
                        
                        st.success(f"✅ Picks for {st.session_state.active_race} saved to Cloud!")
                        try:
                            rain(emoji="🏎️", font_size=54, falling_speed=5, animation_length=3)
                        except:
                            st.balloons()
                    except Exception as e:
                        st.error(f"Cloud Connection Error: {e}")

    # --- SUB-PAGE: STANDINGS ---
    elif menu == "Season Standings":
        st.header("🏆 2026 World Championship Standings")
        try:
            df = conn.read(spreadsheet=SHEET_URL, worksheet="Picks", ttl=0)
            if not df.empty:
                standings = df.groupby("User")["Points"].sum().sort_values(ascending=False).reset_index()
                st.table(standings)
            else:
                st.info("No entries recorded yet!")
        except:
            st.warning("Could not load standings. Ensure 'Picks' tab exists in Google Sheets.")

    # --- SUB-PAGE: HISTORY ---
    elif menu == "My History":
        st.header(f"History for {st.session_state.user}")
        try:
            df = conn.read(spreadsheet=SHEET_URL, worksheet="Picks", ttl=0)
            user_df = df[df['User'] == st.session_state.user]
            st.dataframe(user_df)
        except:
            st.info("No history found.")

# --- ADMIN SECTION (FOR YOU TO ADD POINTS) ---
if st.session_state.auth and st.sidebar.checkbox("🔒 Admin Panel"):
    st.subheader("FIA Admin: Award Points")
    race_to_score = st.selectbox("Select Race to Score", [r['name'] for r in races_2026])
    winning_driver = st.selectbox("Official Winner", drivers_list, key="admin_win")
    
    if st.button("Award 25 Points to Winners"):
        try:
            df = conn.read(spreadsheet=SHEET_URL, worksheet="Picks", ttl=0)
            # Give 25 points to anyone who picked the right P1 for this specific race
            mask = (df['Race'] == race_to_score) & (df['P1'] == winning_driver)
            df.loc[mask, 'Points'] += 25
            conn.update(spreadsheet=SHEET_URL, worksheet="Picks", data=df)
            st.success(f"Points awarded for {race_to_score}!")
        except Exception as e:
            st.error(f"Admin Error: {e}")
