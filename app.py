import pickle
import joblib
import numpy as np
import streamlit as st
import difflib
import sqlite3
import os
from datetime import datetime

# ================= SAFE MODEL LOADER =================
def load_model(filename):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
        model_path = os.path.join(BASE_DIR, filename)
        return joblib.load(model_path)
    except Exception:
        try:
            with open(model_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"❌ Model load error: {e}")
            return None

# ================= LOAD MODELS =================
rf_model_crop = load_model("decision_tree_model_crop.pkl")
rf_model_fertilizer = load_model("decision_tree_model_fertilizer.pkl")

# ================= DATABASE =================
conn = sqlite3.connect("orders.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

c.execute("""CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
address TEXT,
payment_mode TEXT,
product TEXT,
quantity TEXT,
category TEXT,
date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

c.execute("""CREATE TABLE IF NOT EXISTS crop_calendar(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
crop_name TEXT,
sowing_date TEXT,
fertilizer_date TEXT,
harvest_date TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

conn.commit()

# ================= DB FUNCTIONS =================
def register_user(u, p):
    try:
        c.execute("INSERT INTO users(username,password) VALUES(?,?)", (u,p))
        conn.commit()
        return True
    except:
        return False

def login_user(u,p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
    return c.fetchone()

def save_order(name, address, payment, product, qty, cat):
    c.execute("INSERT INTO orders VALUES(NULL,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
              (name,address,payment,product,qty,cat))
    conn.commit()

def get_orders():
    c.execute("SELECT * FROM orders ORDER BY date DESC")
    return c.fetchall()

def save_crop_calendar(u,crop,sow,fert,harv):
    c.execute("INSERT INTO crop_calendar VALUES(NULL,?,?,?,?,?,CURRENT_TIMESTAMP)",
              (u,crop,sow,fert,harv))
    conn.commit()

def get_crop_calendar(u):
    c.execute("SELECT crop_name,sowing_date,fertilizer_date,harvest_date FROM crop_calendar WHERE username=?", (u,))
    return c.fetchall()

# ================= STYLES =================
st.markdown("""
<style>
.stApp {
background:url("https://png.pngtree.com/thumb_back/fh260/background/20210302/pngtree-crop-green-rice-light-effect-wallpaper-image_571433.jpg") no-repeat center fixed;
background-size:cover;
}
.result-box {
background:#2e8b57;color:white;padding:15px;border-radius:12px;font-size:18px;
}
</style>
""", unsafe_allow_html=True)

# ================= SOUND =================
def play_sound():
    if os.path.exists("mixkit-positive-notification-951.wav"):
        with open("mixkit-positive-notification-951.wav","rb") as f:
            st.audio(f.read(),format="audio/wav")

# ================= ML FUNCTIONS =================
def recommend_crop(ph, humidity, N, P, K, temp, rain):
    if rf_model_crop is None:
        return "Model not loaded"
    X = np.array([[N,P,K,temp,humidity,ph,rain]])
    return rf_model_crop.predict(X)[0]

def recommend_fertilizer(temp,hum,moist,soil,crop,N,P,K):
    if rf_model_fertilizer is None:
        return "Model not loaded"
    soil_map={'Loamy':0,'Sandy':1,'Clayey':2}
    crop_map={'Wheat':0,'Rice':1,'Maize':2,'Barley':3}
    X=np.array([[temp,hum,moist,soil_map[soil],crop_map[crop],N,P,K]])
    return rf_model_fertilizer.predict(X)[0]

# ================= CHATBOT =================
knowledge_base={
"what is agriculture":"Agriculture is the practice of farming crops and animals.",
"what is fertilizer":"Fertilizer improves plant growth.",
"what is wheat":"Wheat is a rabi crop.",
"what is rice":"Rice is a kharif crop.",
}

def chatbot_response(q):
    q=q.lower()
    match=difflib.get_close_matches(q,knowledge_base.keys(),1,0.5)
    return knowledge_base[match[0]] if match else "Sorry, I don't know."

# ================= APP =================
st.set_page_config("🌾 Crop System","wide")
st.title("🌾 Crop & Fertilizer Recommendation System")

if "login" not in st.session_state:
    st.session_state.login=False
    st.session_state.user=""

if not st.session_state.login:
    st.subheader("🔐 Login / Register")
    u=st.text_input("Username")
    p=st.text_input("Password",type="password")
    if st.button("Login"):
        if login_user(u,p):
            st.session_state.login=True
            st.session_state.user=u
            st.rerun()
        else:
            st.error("Invalid credentials")
    if st.button("Register"):
        if register_user(u,p):
            st.success("Registered successfully")
else:
    st.sidebar.success(f"Logged in as {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.login=False
        st.rerun()

    tab1,tab2,tab3,tab4,tab5=st.tabs(
        ["🌱 Recommend","🤖 Chatbot","🛍 Orders","📜 History","⏰ Calendar"]
    )

    with tab1:
        ph=st.number_input("pH",0.0,14.0,6.5)
        hum=st.number_input("Humidity",0.0,100.0,60.0)
        N=st.number_input("Nitrogen",0,100,40)
        P=st.number_input("Phosphorus",0,100,40)
        K=st.number_input("Potassium",0,100,40)
        temp=st.number_input("Temperature",0.0,50.0,25.0)
        soil=st.selectbox("Soil",["Loamy","Sandy","Clayey"])
        crop=st.selectbox("Crop",["Wheat","Rice","Maize","Barley"])
        moist=st.number_input("Moisture",0.0,100.0,30.0)

        if st.button("🌱 Predict"):
            c1=recommend_crop(ph,hum,N,P,K,temp,200)
            f1=recommend_fertilizer(temp,hum,moist,soil,crop,N,P,K)
            st.markdown(f"<div class='result-box'>🌾 Crop: {c1}<br>🌿 Fertilizer: {f1}</div>",unsafe_allow_html=True)

    with tab2:
        q=st.text_input("Ask agriculture question")
        if st.button("Ask"):
            st.success(chatbot_response(q))

    with tab3:
        prod=st.text_input("Product")
        qty=st.text_input("Quantity")
        if st.button("Order"):
            save_order(st.session_state.user,"Address","COD",prod,qty,"General")
            st.success("Order placed")

    with tab4:
        for o in get_orders():
            st.write(o)

    with tab5:
        crop=st.selectbox("Crop",["Wheat","Rice","Maize"])
        sow=st.date_input("Sowing Date")
        fert=st.date_input("Fertilizer Date")
        harv=st.date_input("Harvest Date")
        if st.button("Save Calendar"):
            save_crop_calendar(st.session_state.user,crop,str(sow),str(fert),str(harv))
            st.success("Saved")

        today=datetime.now().date()
        for c_name,s,f,h in get_crop_calendar(st.session_state.user):
            if today==datetime.strptime(s,"%Y-%m-%d").date():
                st.warning(f"🌱 Sowing day for {c_name}")
                play_sound()
