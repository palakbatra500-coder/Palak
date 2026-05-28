import streamlit as st
import requests
import datetime
from collections import defaultdict
import time
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Weather Lab AI", layout="wide")

API_KEY = "9714766a9bf395e462e7ec24c779db37"

# ---------------- AUTO REFRESH ----------------
st_autorefresh = st.empty()
time.sleep(0.1)

# ---------------- SESSION ----------------
if "users" not in st.session_state:
    st.session_state["users"] = {}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "weather_data" not in st.session_state:
    st.session_state["weather_data"] = None


# ================= LOGIN (UNCHANGED) =================
if st.session_state["page"] == "login":

    st.markdown("""
    <style>
    header {visibility:hidden;}
    .block-container {
        background:white;
        padding:40px;
        border-radius:10px;
        max-width:700px;
        margin:auto;
    }
    .stButton button {
        background-color:#f06d4f;
        color:white;
        border-radius:6px;
        font-weight:bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Sign In To Your Account")
    st.markdown("---")

    email = st.text_input("Enter email")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if email in st.session_state["users"] and st.session_state["users"][email]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["page"] = "dashboard"
            st.rerun()
        else:
            st.error("Invalid Login ❌")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Create an Account"):
            st.session_state["page"] = "signup"

    with col2:
        if st.button("Click here to recover"):
            st.session_state["page"] = "forgot"


elif st.session_state["page"] == "signup":

    st.title("Create Account")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        st.session_state["users"][email] = {
            "username": username,
            "password": password
        }
        st.success("Account Created Successfully ✅")

    if st.button("Back"):
        st.session_state["page"] = "login"


elif st.session_state["page"] == "forgot":

    st.title("Reset Password")

    email = st.text_input("Email")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Reset"):
        if email in st.session_state["users"]:
            st.session_state["users"][email]["password"] = new_pass
            st.success("Updated ✅")

    if st.button("Back"):
        st.session_state["page"] = "login"


# ================= WEATHER APP =================
else:

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: black;
    }

    .main-card {
        background: rgba(255,255,255,0.85);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

    .temp {
        font-size: 90px;
        font-weight: bold;
    }

    .desc {
        font-size: 22px;
        color: #333;
    }

    .forecast {
        background: rgba(255,255,255,0.8);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
    }

    .nav button {
        background: none !important;
        border: none;
        font-weight: bold;
        color: black !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # NAV
    n1, n2, n3, n4, n5 = st.columns(5)

    if n1.button("Dashboard"):
        st.session_state["page"] = "dashboard"
    if n2.button("Graph"):
        st.session_state["page"] = "graph"
    if n3.button("Map"):
        st.session_state["page"] = "map"
    if n4.button("Feedback"):
        st.session_state["page"] = "feedback"
    if n5.button("Contact"):
        st.session_state["page"] = "contact"

    st.markdown("---")

    # DASHBOARD CONTROLS
    if st.session_state["page"] == "dashboard":

        city = st.text_input("Enter City", "Pune")

        unit = st.radio("Unit", ["Celsius", "Fahrenheit"], horizontal=True)
        units = "metric" if unit == "Celsius" else "imperial"

        if st.button("Get Weather"):

            current = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={units}"
            ).json()

            forecast = requests.get(
                f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={units}"
            ).json()

            if current.get("cod") == 200:
                st.session_state["weather_data"] = (current, forecast)

    # ================= DASHBOARD =================
    if st.session_state["weather_data"] and st.session_state["page"] == "dashboard":

        current, forecast = st.session_state["weather_data"]

        temp = round(current['main']['temp'], 1)
        feels = round(current['main']['feels_like'], 1)
        desc = current['weather'][0]['description']

        icon_map = {
            "clear": "☀️",
            "cloud": "☁️",
            "rain": "🌧️",
            "drizzle": "🌦️",
            "thunderstorm": "⛈️",
            "snow": "❄️"
        }

        icon = "🌤️"
        for key in icon_map:
            if key in desc.lower():
                icon = icon_map[key]

        st.markdown(f"""
        <div class="main-card">
            <h2>{city}</h2>
            <div class="temp">{temp}°C {icon}</div>
            <div class="desc">{desc}</div>
            <p>Feels like: {feels}°C</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("5-Day Forecast")

        daily = defaultdict(list)
        for i in forecast["list"]:
            date = i["dt_txt"].split()[0]
            daily[date].append(i)

        cols = st.columns(5)

        for i,(d,items) in enumerate(list(daily.items())[:5]):
            temp = round(items[len(items)//2]["main"]["temp"],1)
            day = datetime.datetime.strptime(d,"%Y-%m-%d").strftime("%a")

            cols[i].markdown(
                f"<div class='forecast'>{day}<br>{temp}°C</div>",
                unsafe_allow_html=True
            )

    # ================= GRAPH PAGE =================
    elif st.session_state["page"] == "graph":

        st.title("📊 Weather Graph")

        if st.session_state["weather_data"]:
            current, forecast = st.session_state["weather_data"]

            dates = []
            temps = []

            for item in forecast["list"][:8]:
                dates.append(item["dt_txt"][5:16])
                temps.append(item["main"]["temp"])

            fig, ax = plt.subplots(figsize=(10,5))
            ax.plot(dates, temps, marker="o", linewidth=3)
            ax.set_title("Temperature Forecast")
            ax.set_xlabel("Date / Time")
            ax.set_ylabel("Temperature °C")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        else:
            st.warning("Please first get weather data from Dashboard.")

    # ================= MAP PAGE =================
    elif st.session_state["page"] == "map":

        st.title("🗺 Weather Map")

        if st.session_state["weather_data"]:
            current, forecast = st.session_state["weather_data"]

            lat = current["coord"]["lat"]
            lon = current["coord"]["lon"]

            m = folium.Map(location=[lat, lon], zoom_start=10)
            folium.Marker(
                [lat, lon],
                tooltip="Selected City",
                popup="Weather Location"
            ).add_to(m)

            st_folium(m, width=1000, height=500)

        else:
            st.warning("Please first get weather data from Dashboard.")

    # ================= FEEDBACK PAGE =================
    elif st.session_state["page"] == "feedback":

        st.title("📩 Feedback")

        name = st.text_input("Your Name")
        feedback = st.text_area("Write Feedback")

        if st.button("Submit Feedback"):
            st.success("Thank you for your feedback!")

    # ================= CONTACT PAGE =================
    elif st.session_state["page"] == "contact":

        st.title("📞 Contact Us")

        st.markdown("""
        ### 📧 Emails:
        - palakbatra500@gmail.com  
        - bhumikachuniyana04@gmail.com  

        ### 📱 Phone Numbers:
        - 9699346311  
        - 9888223768
        """)
