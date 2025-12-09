# import pickle
# import joblib
# import numpy as np
# import streamlit as st
# import difflib
# import sqlite3
# import os
# from datetime import datetime

# # ------------------ Safe Model Loader ------------------
# def load_model(filename):
#     try:
#         model_path = os.path.join(os.path.dirname(__file__), filename)

#         # पहले joblib से load करने की कोशिश
#         return joblib.load(model_path)

#     except FileNotFoundError:
#         st.error(f"❌ Model file '{filename}' not found. Please add it in your repo.")
#         return None
#     except Exception as e:
#         try:
#             # fallback → pickle से load करो
#             with open(model_path, "rb") as file:
#                 return pickle.load(file)
#         except Exception as e2:
#             st.error(f"⚠️ Error loading model '{filename}': {e2}")
#             return None

# # ------------------ Load Models ------------------
# rf_model_crop = load_model("decision_tree_model_crop.pkl")
# rf_model_fertilizer = load_model("decision_tree_model_fertilizer.pkl")

# # ------------------ Database Setup ------------------
# conn = sqlite3.connect("orders.db", check_same_thread=False)
# c = conn.cursor()

# # Orders Table
# c.execute("""
# CREATE TABLE IF NOT EXISTS orders (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT,
#     address TEXT,
#     payment_mode TEXT,
#     product TEXT,
#     quantity TEXT,
#     category TEXT,
#     date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# )
# """)

# # Users Table
# c.execute("""
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE,
#     password TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# )
# """)
# conn.commit()
# # ------------------ Crop Calendar Table ------------------
# c.execute("""
# CREATE TABLE IF NOT EXISTS crop_calendar (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT,
#     crop_name TEXT,
#     sowing_date TEXT,
#     fertilizer_date TEXT,
#     harvest_date TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# )
# """)
# conn.commit()


# # ------------------ DB Functions ------------------
# def save_order(name, address, payment_mode, product, quantity, category):
#     c.execute("INSERT INTO orders (name, address, payment_mode, product, quantity, category) VALUES (?, ?, ?, ?, ?, ?)",
#               (name, address, payment_mode, product, quantity, category))
#     conn.commit()

# def get_orders():
#     c.execute("SELECT id, name, address, payment_mode, product, quantity, category, date FROM orders ORDER BY date DESC")
#     return c.fetchall()

# def delete_order(order_id):
#     c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
#     conn.commit()

# def clear_all_orders():
#     c.execute("DELETE FROM orders")
#     conn.commit()

# def register_user(username, password):
#     try:
#         c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False

# def login_user(username, password):
#     c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
#     return c.fetchone()
#     def save_crop_calendar(username, crop_name, sowing_date, fertilizer_date, harvest_date):
#     c.execute("""
#         INSERT INTO crop_calendar (username, crop_name, sowing_date, fertilizer_date, harvest_date)
#         VALUES (?, ?, ?, ?, ?)
#     """, (username, crop_name, sowing_date, fertilizer_date, harvest_date))
#     conn.commit()

# def get_crop_calendar(username):
#     c.execute("""
#         SELECT crop_name, sowing_date, fertilizer_date, harvest_date
#         FROM crop_calendar WHERE username = ?
#         ORDER BY created_at DESC
#     """, (username,))
#     return c.fetchall()


# # # ------------------ Styles ------------
# def add_global_styles():
#     st.markdown(
#         """
#         <style>
#         .stApp {
#             background: url("https://png.pngtree.com/thumb_back/fh260/background/20210302/pngtree-crop-green-rice-light-effect-wallpaper-image_571433.jpg") no-repeat center center fixed;
#             background-size: cover;
#         }
#         .result-box {
#             background: linear-gradient(135deg, #228B22, #32CD32);
#             color: white;
#             font-size: 18px;
#             font-weight: bold;
#             border-radius: 16px;
#             padding: 18px;
#             margin: 14px 0;
#             box-shadow: 0px 4px 15px rgba(0,0,0,0.25);
#         }
#         .order-box {
#             background: #fff;
#             border-left: 6px solid #32CD32;
#             padding: 12px;
#             margin: 10px 0;
#             border-radius: 10px;
#             font-size: 15px;
#             box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
#         }
#         .chat-bubble { padding: 12px 16px; margin: 8px 0; border-radius: 14px; max-width: 75%; }
#         .user-bubble { background: #d1f5ff; margin-left: auto; border: 1px solid #a3e4ff; }
#         .bot-bubble { background: #e6ffe6; margin-right: auto; border: 1px solid #b3ffb3; }

#         /* ✅ Force white background for success/error/info/warning messages */
#         .stAlert {
#             background-color: #ffffff !important;
#             color: #000000 !important;
#             border: 1px solid #ccc !important;
#             border-radius: 10px !important;
#             padding: 12px !important;
#             font-weight: 500 !important;
#         }
       
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

# # ------------------ Recommendation & Chatbot ------------------
# crop_descriptions = {
#     "Wheat": "Wheat is a staple cereal crop, requiring cool weather during growth and warm, dry weather at maturity. Best suited for loamy or clay-loam soil with good drainage. Sowing time: October–December.",
#     "Rice": "Rice thrives in clayey, water-retentive soils. It requires high temperature (20–35°C), plenty of water, and humidity. Ideal in areas with standing water (paddy fields). India’s most consumed staple crop.",
#     "Maize": "Maize (corn) is a versatile cereal crop grown in both tropical and temperate climates. Needs well-drained sandy-loam soil and moderate rainfall. Used for food, fodder, and biofuel.",
#     "Barley": "Barley is a hardy cereal grown in cool climates, tolerant to drought. Requires light loamy soil. Used in food, feed, and brewing industries.",
#     "Sugarcane": "Sugarcane requires a long growing season, hot tropical climate, and well-drained fertile soil. Major source of sugar, jaggery, and ethanol.",
#     "Cotton": "Cotton grows best in black soil with good drainage. Needs warm climate and 6–8 months frost-free period. Source of natural fiber.",
#     "Millets": "Millets (Bajra, Ragi, Jowar) are drought-resistant crops. Require low water, can grow in arid regions. Rich in iron, calcium, and fiber.",
# }

# fertilizer_descriptions = {
#     "Urea": "Urea (46% Nitrogen) is the most concentrated solid nitrogen fertilizer. It helps in rapid vegetative growth but should not be applied excessively.",
#     "DAP": "Di-Ammonium Phosphate (DAP) contains 18% Nitrogen and 46% Phosphorus. Best for root development and early crop growth.",
#     "MOP": "Muriate of Potash (60% K2O) is a potassium-rich fertilizer that improves disease resistance and water retention. Commonly used for sugarcane, potatoes, and fruits.",
#     "Compost": "Organic compost improves soil structure, water retention, and nutrient supply. Eco-friendly option for sustainable farming.",
#     "Ammonium Sulphate": "Contains 21% Nitrogen and 24% Sulphur. Promotes protein synthesis and is good for oilseed crops.",
#     "Super Phosphate": "Single Super Phosphate (SSP) contains 16% Phosphorus. Helps in root growth and seed development.",
#     "Vermicompost": "Prepared from earthworms. Rich in micronutrients and organic matter. Boosts soil fertility naturally.",
# }

# knowledge_base = {
#     # 🌾 General Crop Information
#     "what is agriculture": "Agriculture is the science and practice of cultivating soil, growing crops, and raising animals for food, fiber, and other products.",
#     "what is horticulture": "Horticulture is the branch of agriculture that deals with the cultivation of fruits, vegetables, flowers, and ornamental plants.",
#     "what is agronomy": "Agronomy is the science of soil management and crop production.",
#     "difference between kharif and rabi crops": "Kharif crops are grown in the rainy season (e.g., rice, maize), while Rabi crops are grown in winter (e.g., wheat, barley).",
#     "examples of kharif crops": "Rice, maize, cotton, jowar, bajra, groundnut, sugarcane.",
#     "examples of rabi crops": "Wheat, barley, mustard, peas, gram.",
#     "examples of zaid crops": "Watermelon, cucumber, muskmelon, fodder crops.",
#     "what is mixed cropping": "Mixed cropping is growing two or more crops simultaneously on the same field to reduce risk of total crop failure.",
#     "what is intercropping": "Intercropping is growing two or more crops in a definite row pattern to maximize resource use.",
#     "what is monocropping": "Monocropping is growing only one crop year after year on the same land, which may lead to soil nutrient depletion.",
#     "what is crop rotation": "Crop rotation is the practice of growing different crops sequentially on the same field to improve soil fertility and reduce pests.",
#     "crop rotation advantages": "Prevents nutrient depletion, improves soil structure, controls weeds and pests, and increases yield.",
#     "what are millets": "Millets are small-seeded cereals like bajra, ragi, and jowar. They are drought-resistant and highly nutritious.",
#     "what are pulses": "Pulses are leguminous crops like gram, lentil, and pigeon pea. They are rich in protein and improve soil fertility by fixing nitrogen.",

#     # 🌱 Fertilizers & Nutrients
#     "what is npk": "NPK stands for Nitrogen (N), Phosphorus (P), and Potassium (K) – the three essential macronutrients for plant growth.",
#     "importance of nitrogen": "Nitrogen promotes vegetative growth, leaf development, and chlorophyll formation.",
#     "importance of phosphorus": "Phosphorus helps in root development, seed formation, and early plant growth.",
#     "importance of potassium": "Potassium improves disease resistance, drought tolerance, and enhances fruit quality.",
#     "what are micronutrients in plants": "Micronutrients include iron, zinc, copper, manganese, boron, and molybdenum, required in small quantities for plant growth.",
#     "best fertilizer for wheat": "Urea and DAP are commonly recommended for wheat.",
#     "best fertilizer for rice": "Urea and Super Phosphate are widely used for rice production.",
#     "best fertilizer for maize": "Maize requires Nitrogen-rich fertilizers like Urea, along with DAP for root establishment.",
#     "what is dap fertilizer": "DAP (Di-Ammonium Phosphate) contains 18% Nitrogen and 46% Phosphorus, good for early crop growth.",
#     "what is mop fertilizer": "MOP (Muriate of Potash) provides 60% K2O, essential for sugarcane, potato, and fruit crops.",
#     "what is urea": "Urea is a nitrogen-rich fertilizer (46% N) used for rapid vegetative growth.",
#     "what is vermicompost": "Vermicompost is an organic fertilizer produced using earthworms. It enriches soil fertility naturally.",
#     "what is green manure": "Green manure is the practice of growing crops like sunhemp or dhaincha and ploughing them back into the soil to improve fertility.",
#     "difference between organic and chemical fertilizers": "Organic fertilizers improve soil health gradually, while chemical fertilizers give quick results but may degrade soil over time.",

#     # 🌍 Soil & Irrigation
#     "best soil for rice": "Clayey soil with good water-holding capacity is best for rice.",
#     "best soil for wheat": "Loamy and clay-loam soils are best for wheat.",
#     "best crop for sandy soil": "Groundnut, Bajra, and Watermelon grow well in sandy soil.",
#     "types of soil in india": "Alluvial, black, red, laterite, desert, and mountain soils.",
#     "what is alluvial soil": "Alluvial soil is fertile, found in river plains, and suitable for crops like rice, wheat, and sugarcane.",
#     "what is black soil": "Black soil, also called regur soil, is rich in clay and suitable for cotton.",
#     "what is red soil": "Red soil is sandy, less fertile, and requires fertilizers. Suitable for millets and pulses.",
#     "what is loamy soil": "Loamy soil is a mixture of sand, silt, and clay. It is the most fertile and ideal for agriculture.",
#     "what is irrigation": "Irrigation is the artificial application of water to crops at required intervals.",
#     "types of irrigation": "Surface irrigation, drip irrigation, sprinkler irrigation, and subsurface irrigation.",
#     "drip irrigation benefits": "Saves water, reduces weeds, provides nutrients directly to roots, and increases yield.",
#     "sprinkler irrigation benefits": "Useful in sandy soils, saves water, and distributes water uniformly.",
#     "flood irrigation disadvantages": "Leads to water wastage, soil erosion, and nutrient leaching.",

#     # 🐛 Pests & Diseases
#     "what is pest": "A pest is any organism that damages crops, livestock, or stored food.",
#     "examples of crop pests": "Locusts, bollworms, stem borers, aphids, and termites.",
#     "what is integrated pest management": "IPM is an eco-friendly approach combining biological, cultural, and chemical methods to control pests.",
#     "what is weeding": "Weeding is the process of removing unwanted plants (weeds) that compete with crops for nutrients and water.",
#     "common weeds in crops": "Parthenium, nutgrass, wild oats, Bermuda grass.",
#     "what is biological pest control": "Using natural predators like ladybugs or neem extracts to control pests.",
#     "fungal diseases in crops": "Rust in wheat, blast in rice, smut in sugarcane.",
#     "bacterial diseases in crops": "Blight in rice, canker in citrus, wilt in tomato.",
#     "viral diseases in crops": "Mosaic in tobacco, leaf curl in cotton, bunchy top in banana.",

#     # 🌿 Organic Farming
#     "what is organic farming": "Organic farming avoids synthetic chemicals and relies on natural methods for crop growth.",
#     "organic farming benefits": "Improves soil fertility, reduces chemical usage, enhances biodiversity, and provides healthy food.",
#     "organic fertilizers examples": "Compost, farmyard manure, vermicompost, green manure.",
#     "what is biodynamic farming": "A method of organic farming that uses natural preparations and follows lunar cycles.",
#     "what is sustainable agriculture": "Sustainable agriculture balances productivity with environmental protection and resource conservation.",

#     # 🌦️ Climate & Cropping
#     "crops grown in winter": "Wheat, barley, mustard, and gram are grown in winter.",
#     "crops grown in summer": "Rice, maize, jowar, bajra, cotton, sugarcane.",
#     "crops grown in rainy season": "Rice, maize, cotton, soybean, groundnut.",
#     "which crop needs more water": "Rice needs the maximum water among cereal crops.",
#     "which crop is drought resistant": "Millets like jowar, bajra, and ragi are drought resistant.",
#     "which crop grows in less water": "Pulses, mustard, and barley grow well in less water conditions.",

#     # 🚜 Farm Practices
#     "what is ploughing": "Ploughing is turning and loosening of soil to prepare it for sowing.",
#     "what is harrowing": "Harrowing breaks up clods and levels the field after ploughing.",
#     "what is sowing": "Sowing is placing seeds in soil for germination.",
#     "what is harvesting": "Harvesting is cutting and collecting mature crops from the field.",
#     "what is threshing": "Threshing is separating grains from stalks after harvesting.",
#     "what is storage of grains": "Grains should be stored in dry, airtight containers or godowns to prevent pest attack.",

#     # 💧 Miscellaneous
#     "what is greenhouse farming": "Greenhouse farming is growing crops under controlled temperature and humidity conditions.",
#     "what is hydroponics": "Hydroponics is a method of growing plants without soil, using nutrient-rich water solutions.",
#     "what is precision farming": "Precision farming uses technology like sensors, drones, and AI to optimize crop production.",
#     "what is food security": "Food security means having reliable access to sufficient, safe, and nutritious food.",
#     "what is famine": "Famine is an extreme scarcity of food causing widespread hunger.",
#     "what is cash crop": "Cash crops like cotton, sugarcane, and coffee are grown mainly for sale in the market.",
#     "what is subsistence farming": "Subsistence farming is when farmers grow food mainly for their own consumption, not for sale.",
# }


# def recommend_crop(ph, humidity, N, P, K, temperature, rainfall):
#     if rf_model_crop is None:
#         return "Model not loaded"
#     features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
#     prediction = rf_model_crop.predict(features)
#     return prediction[0]

# def recommend_fertilizer(temperature, humidity, moisture, soil_type, crop_type, N, P, K):
#     if rf_model_fertilizer is None:
#         return "Model not loaded"
#     soil_mapping = {'Loamy': 0, 'Sandy': 1, 'Clayey': 2}
#     crop_mapping = {'Wheat': 0, 'Rice': 1, 'Maize': 2, 'Barley': 3}
#     features = np.array([[temperature, humidity, moisture,
#                           soil_mapping.get(soil_type, 0),
#                           crop_mapping.get(crop_type, 0),
#                           N, P, K]])
#     prediction = rf_model_fertilizer.predict(features)
#     return prediction[0]

# def chatbot_response(user_input):
#     user_input_lower = user_input.lower()
#     best_match = difflib.get_close_matches(user_input_lower, knowledge_base.keys(), n=1, cutoff=0.5)
#     if best_match:
#         return knowledge_base[best_match[0]]
#     return "Sorry, I don't have an answer for that."

# # ------------------ Streamlit App ------------------
# st.set_page_config(page_title="🌾 Crop & Fertilizer System", layout="wide")
# add_global_styles()
# st.title("🌾 Crop & Fertilizer Recommendation System")

# # ------------------ LOGIN PAGE ------------------
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "username" not in st.session_state:
#     st.session_state.username = ""

# if not st.session_state.logged_in:
#     st.header(" Login / Register")

#     choice = st.radio("Choose Action", ["Login", "Register"])
#     username = st.text_input("👤 Username")
#     password = st.text_input("🔒 Password", type="password")

#     if choice == "Login":
#         if st.button("Login"):
#             user = login_user(username, password)
#             if user:
#                 st.session_state.logged_in = True
#                 st.session_state.username = username
#                 st.success(f"✅ Welcome back, {username}!")
#                 st.rerun()
#             else:
#                 st.error("❌ Invalid username or password")
#     else:
#         if st.button("Register"):
#             if register_user(username, password):
#                 st.success("✅ Registration successful! Please login.")
#             else:
#                 st.error("⚠️ Username already exists!")

# else:
#     st.sidebar.success(f"👤 Logged in as {st.session_state.username}")
#     if st.sidebar.button("🚪 Logout"):
#         st.session_state.logged_in = False
#         st.session_state.username = ""
#         st.rerun()

#     # After login → Show all other tabs
#    tab1, tab2, tab3, tab4, tab5 = st.tabs(
#     ["🌱 Crop & Fertilizer", "🤖 Chatbot", "🛍 Order Page", "📜 Order History", "⏰ Crop Calendar"]
# )


#     # ------------------ Tab1: Crop & Fertilizer ------------------
#     with tab1:
#         st.header("🌱 Enter Soil & Weather Details")
#         col1, col2 = st.columns(2)
#         with col1:
#             ph = st.number_input("Soil pH", 0.0, 14.0, 6.5)
#             humidity = st.number_input("Humidity (%)", 0.0, 100.0, 60.0)
#             N = st.number_input("Nitrogen (N)", 0, 100, 50)
#             P = st.number_input("Phosphorous (P)", 0, 100, 40)
#             K = st.number_input("Potassium (K)", 0, 100, 40)
#         with col2:
#             temperature = st.number_input("Temperature (°C)", -10.0, 50.0, 25.0)
#             moisture = st.number_input("Moisture (%)", 0.0, 100.0, 30.0)
#             soil_type = st.selectbox("Soil Type", ["Loamy", "Sandy", "Clayey"])
#             crop_type = st.selectbox("Crop Type", ["Wheat", "Rice", "Maize", "Barley"])

#         if st.button("🌱 Get Recommendations"):
#             crop_result = recommend_crop(ph, humidity, N, P, K, temperature, rainfall=200.0)
#             fert_result = recommend_fertilizer(temperature, humidity, moisture, soil_type, crop_type, N, P, K)

#             st.markdown(f"<div class='result-box'>🌾 Recommended Crop: {crop_result}<br><i>{crop_descriptions.get(crop_result, '')}</i></div>", unsafe_allow_html=True)
#             st.markdown(f"<div class='result-box'>🌿 Recommended Fertilizer: {fert_result}<br><i>{fertilizer_descriptions.get(fert_result, '')}</i></div>", unsafe_allow_html=True)

#     # ------------------ Tab2: Chatbot ------------------
#     with tab2:
#         st.header("🤖 Chatbot Assistant")
#         if "chat_history" not in st.session_state:
#             st.session_state.chat_history = []
#         user_input = st.text_input("Ask me anything about crops or fertilizers:")
#         if st.button("Send"):
#             if user_input:
#                 response = chatbot_response(user_input)
#                 st.session_state.chat_history.append(("user", user_input))
#                 st.session_state.chat_history.append(("bot", response))
#         for role, msg in st.session_state.chat_history:
#             bubble_class = "user-bubble" if role == "user" else "bot-bubble"
#             st.markdown(f'<div class="chat-bubble {bubble_class}">{msg}</div>', unsafe_allow_html=True)

#     # ------------------ Tab3: Order Page ------------------
#     with tab3:
#         st.header("🛍 Order Crops, Seeds & Fertilizers")
#         name = st.text_input("👤 Enter Your Name", value=st.session_state.username)
#         address = st.text_area("🏠 Enter Delivery Address")
#         payment_mode = st.selectbox("💳 Payment Mode", ["Cash on Delivery", "UPI", "Net Banking", "Card Payment"])
#         category = st.radio("Choose Category:", ["🌾 Crops", "🌱 Seeds", "💊 Fertilizers"])

#         if category == "🌾 Crops":
#             crop = st.selectbox("Select Crop:", ["Wheat", "Rice", "Maize", "Barley"])
#             qty = st.number_input("Quantity (Quintals)", 1, 100, 1)
#             if st.button("🛒 Order Crop"):
#                 save_order(name, address, payment_mode, crop, f"{qty} Quintals", "Crop")
#                 st.success(f"✅ Order placed for {qty} Quintals of {crop}")

#         elif category == "🌱 Seeds":
#             seed = st.selectbox("Select Seed:", ["Wheat Seed", "Rice Seed", "Maize Seed", "Barley Seed"])
#             qty = st.number_input("Quantity (Kg)", 1, 500, 10)
#             if st.button("🛒 Order Seeds"):
#                 save_order(name, address, payment_mode, seed, f"{qty} Kg", "Seed")
#                 st.success(f"✅ Order placed for {qty} Kg of {seed}")

#         else:
#             fert = st.selectbox("Select Fertilizer:", ["Urea", "DAP", "MOP", "Compost"])
#             qty = st.number_input("Quantity (Bags)", 1, 200, 1)
#             if st.button("🛒 Order Fertilizer"):
#                 save_order(name, address, payment_mode, fert, f"{qty} Bags", "Fertilizer")
#                 st.success(f"✅ Order placed for {qty} Bags of {fert}")

#     # ------------------ Tab4: Order History ------------------
#     with tab4:
#         st.header("📜 Your Order History")
#         orders = get_orders()
#         if not orders:
#             st.info("No orders yet.")
#         else:
#             if st.button("🗑 Clear All Orders"):
#                 clear_all_orders()
#                 st.success("✅ All orders deleted.")
#                 st.rerun()
#             for i, (oid, name, address, pm, product, qty, cat, date) in enumerate(orders, 1):
#                 col1, col2 = st.columns([4, 1])
#                 with col1:
#                     st.markdown(f"<div class='order-box'>📝 {i}. <b>{product}</b> - {qty} ({cat})<br>👤 {name} | 💳 {pm}<br>🏠 {address}<br>📅 {date}</div>", unsafe_allow_html=True)
#                 with col2:
#                     if st.button("❌ Delete", key=f"del_{oid}"):
#                         delete_order(oid)
#                         st.warning(f"❌ Order {i} deleted")
#                         st.rerun()
# # ------------------ ✅ Tab5: Crop Calendar & Reminder ------------------
# # 🔊 Reminder Sound Player (Correct WAV Path)
# def play_sound():
#     try:
#         audio_path = "mixkit-positive-notification-951.wav"
#         with open(audio_path, "rb") as audio_file:
#             st.audio(audio_file.read(), format="audio/wav")
#     except:
#         st.warning("⚠️ Sound file not found! Check file name & location.")


# with tab5:
#     st.header("⏰ Crop Calendar & Smart Reminder")

#     crop_name = st.selectbox(
#         "🌾 Select Crop",
#         ["Wheat", "Rice", "Maize", "Barley", "Sugarcane", "Cotton"]
#     )

#     sowing_date = st.date_input("🌱 Sowing Date")
#     fertilizer_date = st.date_input("💊 Fertilizer Date")
#     harvest_date = st.date_input("🚜 Harvest Date")

#     # ✅ Save Schedule
#     if st.button("✅ Save Crop Schedule"):
#         save_crop_calendar(
#             st.session_state.username,
#             crop_name,
#             str(sowing_date),
#             str(fertilizer_date),
#             str(harvest_date)
#         )
#         st.success("✅ Crop calendar saved successfully!")

#     st.subheader("📅 Your Saved Crop Schedules")
#     records = get_crop_calendar(st.session_state.username)

#     if not records:
#         st.info("No crop schedules added yet.")
#     else:
#         today = datetime.now().date()

#         for crop, sow, fert, harvest in records:
#             sow_d = datetime.strptime(sow, "%Y-%m-%d").date()
#             fert_d = datetime.strptime(fert, "%Y-%m-%d").date()
#             harv_d = datetime.strptime(harvest, "%Y-%m-%d").date()

#             st.markdown(f"""
# ✅ **Crop:** {crop}  
# 🌱 **Sowing:** {sow}  
# 💊 **Fertilizer:** {fert}  
# 🚜 **Harvest:** {harvest}
# """)

#             # 🔔 🔊 SMART AUTO REMINDER WITH SOUND
#             if today == sow_d:
#                 st.warning(f"🌱 Today is *Sowing Day* for {crop}!")
#                 play_sound()

#             if today == fert_d:
#                 st.warning(f"💊 Today is *Fertilizer Day* for {crop}!")
#                 play_sound()

#             if today == harv_d:
#                 st.success(f"🚜 Today is *Harvest Day* for {crop}!")
#                 play_sound()

#             st.markdown("---")
import pickle
import joblib
import numpy as np
import streamlit as st
import difflib
import sqlite3
import os
from datetime import datetime

# ------------------ Safe Model Loader ------------------
def load_model(filename):
    try:
        model_path = os.path.join(os.path.dirname(__file__), filename)
        return joblib.load(model_path)

    except FileNotFoundError:
        st.error(f"❌ Model file '{filename}' not found.")
        return None
    except Exception:
        try:
            with open(model_path, "rb") as file:
                return pickle.load(file)
        except Exception as e2:
            st.error(f"⚠️ Error loading model '{filename}': {e2}")
            return None

# ------------------ Load Models ------------------
rf_model_crop = load_model("decision_tree_model_crop.pkl")
rf_model_fertilizer = load_model("decision_tree_model_fertilizer.pkl")

# ------------------ Database Setup ------------------
conn = sqlite3.connect("orders.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    payment_mode TEXT,
    product TEXT,
    quantity TEXT,
    category TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS crop_calendar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    crop_name TEXT,
    sowing_date TEXT,
    fertilizer_date TEXT,
    harvest_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ------------------ DB Functions ------------------
def save_order(name, address, payment_mode, product, quantity, category):
    c.execute("INSERT INTO orders (name, address, payment_mode, product, quantity, category) VALUES (?, ?, ?, ?, ?, ?)",
              (name, address, payment_mode, product, quantity, category))
    conn.commit()

def get_orders():
    c.execute("SELECT id, name, address, payment_mode, product, quantity, category, date FROM orders ORDER BY date DESC")
    return c.fetchall()

def delete_order(order_id):
    c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()

def clear_all_orders():
    c.execute("DELETE FROM orders")
    conn.commit()

def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def save_crop_calendar(username, crop_name, sowing_date, fertilizer_date, harvest_date):
    c.execute("""
        INSERT INTO crop_calendar (username, crop_name, sowing_date, fertilizer_date, harvest_date)
        VALUES (?, ?, ?, ?, ?)
    """, (username, crop_name, sowing_date, fertilizer_date, harvest_date))
    conn.commit()

def get_crop_calendar(username):
    c.execute("""
        SELECT crop_name, sowing_date, fertilizer_date, harvest_date
        FROM crop_calendar WHERE username = ?
        ORDER BY created_at DESC
    """, (username,))
    return c.fetchall()

# ------------------ Styles ------------------
def add_global_styles():
    st.markdown("""
        <style>
        .stApp {
            background: url("https://png.pngtree.com/thumb_back/fh260/background/20210302/pngtree-crop-green-rice-light-effect-wallpaper-image_571433.jpg") no-repeat center center fixed;
            background-size: cover;
        }
        .result-box {
            background: linear-gradient(135deg, #228B22, #32CD32);
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 16px;
            padding: 18px;
            margin: 14px 0;
        }
        .order-box {
            background: #fff;
            border-left: 6px solid #32CD32;
            padding: 12px;
            margin: 10px 0;
            border-radius: 10px;
            font-size: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

# ------------------ SOUND FUNCTION ------------------
def play_sound():
    try:
        audio_path = "mixkit-positive-notification-951.wav"
        if os.path.exists(audio_path):
            with open(audio_path, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/wav")
        else:
            st.warning("⚠️ Sound file not found.")
    except Exception as e:
        st.error(f"Sound Error: {e}")

# ------------------ PREDICTIONS ------------------
def recommend_crop(ph, humidity, N, P, K, temperature, rainfall):
    if rf_model_crop is None:
        return "Model not loaded"
    features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    return rf_model_crop.predict(features)[0]

def recommend_fertilizer(temperature, humidity, moisture, soil_type, crop_type, N, P, K):
    if rf_model_fertilizer is None:
        return "Model not loaded"
    soil_mapping = {'Loamy': 0, 'Sandy': 1, 'Clayey': 2}
    crop_mapping = {'Wheat': 0, 'Rice': 1, 'Maize': 2, 'Barley': 3}
    features = np.array([[temperature, humidity, moisture,
                          soil_mapping.get(soil_type, 0),
                          crop_mapping.get(crop_type, 0), N, P, K]])
    return rf_model_fertilizer.predict(features)[0]

def chatbot_response(user_input):
    user_input_lower = user_input.lower()
    knowledge_base = {
      # 🌱 Agriculture Basics
        "what is agriculture": "Agriculture is the practice of cultivating crops and rearing animals for food, fiber, and other products.",
        "types of agriculture": "The main types of agriculture are subsistence farming, commercial farming, organic farming, and mixed farming.",
        "importance of agriculture": "Agriculture provides food, raw materials, employment, and supports the economy.",

        # 🌾 Crops
        "what is crop": "A crop is a plant that is grown and harvested for food or profit.",
        "types of crops": "Major crop types include food crops, cash crops, plantation crops, and horticultural crops.",
        "kharif crops": "Kharif crops are grown in the rainy season like rice, maize, and cotton.",
        "rabi crops": "Rabi crops are grown in winter like wheat, barley, and mustard.",
        "zaid crops": "Zaid crops are grown between Kharif and Rabi seasons like watermelon and cucumber.",

        # 🌧 Climate & Soil
        "what is soil": "Soil is the upper layer of earth where plants grow.",
        "types of soil": "Main soil types are sandy, clayey, loamy, black, red, and alluvial soil.",
        "best soil for crops": "Loamy soil is best for most crops because it has good drainage and fertility.",
        "what is rainfall": "Rainfall is the amount of rain received in an area and is important for crop growth.",

        # 🌿 Fertilizers
        "what is fertilizer": "Fertilizer is a substance added to soil to improve plant growth.",
        "types of fertilizers": "Fertilizers are organic (manure, compost) and chemical (DAP, urea, NPK).",
        "what is urea": "Urea is a nitrogen-rich fertilizer used for leaf and plant growth.",
        "what is dap": "DAP (Di-Ammonium Phosphate) provides nitrogen and phosphorus to plants.",
        "npk fertilizer": "NPK fertilizer contains Nitrogen, Phosphorus, and Potassium for balanced growth.",

        # 🚜 Farming Methods
        "organic farming": "Organic farming avoids chemical fertilizers and uses natural manure.",
        "mixed farming": "Mixed farming includes both crop production and animal farming.",
        "crop rotation": "Crop rotation means growing different crops in sequence to improve soil fertility.",

        # 💧 Irrigation
        "what is irrigation": "Irrigation is the artificial supply of water to crops.",
        "types of irrigation": "Irrigation methods include drip irrigation, sprinkler, canal, and tube wells.",
        "best irrigation method": "Drip irrigation is the most water-efficient method.",

        # 🐛 Pests & Diseases
        "what are pests": "Pests are insects or organisms that damage crops.",
        "pest control": "Pests can be controlled using pesticides, biological methods, and crop rotation.",

        # 🌾 Major Crops Info
        "wheat crop": "Wheat is a Rabi crop grown in winter and harvested in spring.",
        "rice crop": "Rice is a Kharif crop grown in rainy season and needs a lot of water.",
        "maize crop": "Maize is grown in both Kharif and Rabi seasons.",
        "cotton crop": "Cotton is a cash crop used to make clothes.",
        "sugarcane crop": "Sugarcane is used for making sugar and juice.",

        # 🌍 General
        "green revolution": "The Green Revolution increased agricultural production using modern methods.",
        "food security": "Food security means everyone has access to sufficient food.",
        "climate change": "Climate change affects rainfall, temperature, and crop production."

    }
    best_match = difflib.get_close_matches(user_input_lower, knowledge_base.keys(), n=1, cutoff=0.5)
    return knowledge_base[best_match[0]] if best_match else "Sorry, I don't know that yet."

# ------------------ APP ------------------
st.set_page_config(page_title="🌾 System", layout="wide")
add_global_styles()
st.title("🌾 Crop & Fertilizer System")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:

    st.header("Login / Register")
    choice = st.radio("Choose Action", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Login":
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid login")

    else:
        if st.button("Register"):
            if register_user(username, password):
                st.success("Registered successfully!")
            else:
                st.error("Username already exists")

else:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🌱 Crop", "🤖 Chatbot", "🛍 Orders", "📜 History", "⏰ Calendar"]
    )

    with tab1:
        ph = st.number_input("pH", 0.0, 14.0, 6.5)
        humidity = st.number_input("Humidity", 0.0, 100.0, 60.0)
        N = st.number_input("Nitrogen", 0, 100, 40)
        P = st.number_input("Phosphorus", 0, 100, 40)
        K = st.number_input("Potassium", 0, 100, 40)
        temperature = st.number_input("Temperature", -10.0, 50.0, 25.0)

        if st.button("Predict Crop"):
            crop = recommend_crop(ph, humidity, N, P, K, temperature, 200)
            st.success(f"Recommended Crop: {crop}")

    with tab2:
        msg = st.text_input("Ask something")
        if st.button("Send"):
            st.success(chatbot_response(msg))

    with tab3:
        product = st.text_input("Product")
        qty = st.text_input("Quantity")
        if st.button("Order"):
            save_order(st.session_state.username, "Address", "COD", product, qty, "General")
            st.success("Order Placed")

    with tab4:
        orders = get_orders()
        for o in orders:
            st.write(o)

    with tab5:
        crop = st.selectbox("Crop", ["Wheat", "Rice", "Maize"])
        sow = st.date_input("Sowing Date")
        fert = st.date_input("Fertilizer Date")
        harv = st.date_input("Harvest Date")

        if st.button("Save Calendar"):
            save_crop_calendar(st.session_state.username, crop, str(sow), str(fert), str(harv))
            st.success("Saved")

        today = datetime.now().date()
        records = get_crop_calendar(st.session_state.username)

        for c_name, s, f, h in records:
            if today == datetime.strptime(s, "%Y-%m-%d").date():
                st.warning(f"Sowing Reminder for {c_name}")
                play_sound()  knowledge base add more