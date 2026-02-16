import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
from src.processing import calculate_solar_output 

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Solar Energy Predictor", 
    page_icon="☀️", 
    layout="wide"
)

# 2. CARGA DE CIUDADES DESDE JSON (Nueva lógica)
@st.cache_data # Usamos caché para no leer el disco en cada clic
def load_cities():
    try:
        # Apuntamos a la carpeta 'data' donde creaste el archivo
        with open('data/cities.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Unimos las listas de Colombia e International
        all_cities = []
        for category in data.values():
            all_cities.extend(category)
        return sorted(list(set(all_cities)))
    except FileNotFoundError:
        # Fallback por si el archivo no se encuentra
        return ["Bogota", "Medellin", "Miami", "Madrid"]

full_city_list = load_cities()

# 3. CSS PARA EL DISEÑO AZULADO
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background-color: #1a232e;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3a4b;
    }
    .tech-details {
        background-color: #1a232e;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #007bff;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. HEADER
st.title("☀️ Solar Energy Production Estimator")
st.markdown("### Real-Time Analysis & Global Comparison")

# 5. SIDEBAR
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.secrets["OPENWEATHER_API_KEY"]
    
    selected_cities = st.multiselect(
        "Select Cities to Compare:",
        full_city_list,
        default=["Bogota", "Medellin"] if "Bogota" in full_city_list else full_city_list[:2]
    )
    
    st.divider()
    p_nom = st.number_input("Nominal Power (Watts):", value=330)
    eff_user = st.slider("Efficiency (%)", 10.0, 25.0, 18.5)

# 6. LÓGICA DE PROCESAMIENTO
if selected_cities:
    results_list = []

    for city in selected_cities:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                clouds = data['clouds']['all']
                
                res = calculate_solar_output(temp, clouds, p_nom, eff_user)
                
                results_list.append({
                    "City": city,
                    "Power (W)": res['power_output'],
                    "Temp (°C)": temp,
                    "Clouds (%)": clouds,
                    "Irradiance (W/m²)": res['irradiance'],
                    "Thermal Factor": res['thermal_factor'],
                    "Description": data['weather'][0]['description'].capitalize()
                })
        except Exception as e:
            st.error(f"Error connecting for {city}")

    if results_list:
        df = pd.DataFrame(results_list)

        # 7. GRÁFICA COMPARATIVA
        st.subheader("📊 Comparative Solar Potential")
        fig = px.bar(
            df, x="City", y="Power (W)", color="Power (W)",
            text_auto='.2f', color_continuous_scale="Blues", template="plotly_dark"
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # 8. FOCO EN LA PRIMERA SELECCIÓN
        st.divider()
        main_city = results_list[0]
        st.subheader(f"📍 Focus: {main_city['City']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature", f"{main_city['Temp (°C)']} °C")
        c2.metric("Cloudiness", f"{main_city['Clouds (%)']} %")
        c3.metric("Irradiance", f"{main_city['Irradiance (W/m²)']} W/m²")

        res_col, tech_col = st.columns([2, 1])
        with res_col:
            st.success(f"### Estimated Power: **{main_city['Power (W)']} Watts**")
            st.progress(min(main_city['Power (W)'] / p_nom, 1.0))

        with tech_col:
            st.markdown(f"""
                <div class="tech-details">
                    <p><strong>Sky:</strong> {main_city['Description']}</p>
                    <p><strong>Thermal Factor:</strong> {main_city['Thermal Factor']}x</p>
                    <p><strong>Config:</strong> {p_nom}W @ {eff_user}%</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("Please select cities from the sidebar.")