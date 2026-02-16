import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
from src.processing import calculate_solar_output 

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Solar Energy Predictor", 
    page_icon="♻️💡🔋", 
    layout="wide"
)

# 2. CARGA DE CIUDADES DESDE JSON
@st.cache_data
def load_cities():
    try:
        with open('data/cities.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_cities = []
        for category in data.values():
            all_cities.extend(category)
        return sorted(list(set(all_cities)))
    except Exception:
        return ["Bogota", "Medellin"]

full_city_list = load_cities()

# 3. CSS ORIGINAL (Restaurado)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    [data-testid="stMetric"] {
        background-color: #1a232e;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #2d3a4b;
    }
    
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #8094ad !important; }

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
st.markdown("### Real-Time Photovoltaic Analysis Dashboard")

# 5. SIDEBAR
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.secrets["OPENWEATHER_API_KEY"]
    
    selected_cities = st.multiselect(
        "Select Cities to Compare:",
        full_city_list,
        default=["Bogota", "Medellin"]
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
                humidity = data['main']['humidity']
                
                res = calculate_solar_output(temp, clouds, p_nom, eff_user)
                
                results_list.append({
                    "City": city,
                    "Power (W)": res['power_output'],
                    "Temp (°C)": temp,
                    "Clouds (%)": clouds,
                    "Humidity (%)": humidity,
                    "Irradiance (W/m²)": res['irradiance'],
                    "Thermal Factor": res['thermal_factor'],
                    "Description": data['weather'][0]['description'].capitalize()
                })
        except Exception:
            continue

    if results_list:
        df = pd.DataFrame(results_list)
        # Tomamos la primera ciudad de la lista para el enfoque detallado (Focus)
        main_city = results_list[0]

        # --- DISEÑO ORIGINAL RESTAURADO ---
        
        # A. Fila de 4 Métricas (Igual que antes)
        st.markdown(f"#### 📍 Detailed Focus: {main_city['City']}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature", f"{main_city['Temp (°C)']} °C")
        col2.metric("Cloudiness", f"{main_city['Clouds (%)']} %")
        col3.metric("Humidity", f"{main_city['Humidity (%)']} %")
        col4.metric("Irradiance", f"{main_city['Irradiance (W/m²)']} W/m²")

        st.divider()

        # B. Sección de Resultados y Technical Details (Columnas 2:1)
        res_col, tech_col = st.columns([2, 1])

        with res_col:
            st.subheader("🚀 Performance Summary")
            st.success(f"### Current Power Output in {main_city['City']}: **{main_city['Power (W)']} Watts**")
            
            cap_ratio = min(main_city['Power (W)'] / p_nom, 1.0)
            st.write(f"System Capacity Utilization: {cap_ratio*100:.1f}%")
            st.progress(cap_ratio)
            
            # Insertamos el gráfico aquí para que no rompa el flujo visual
            st.subheader("📊 Comparison Chart")
            fig = px.bar(df, x="City", y="Power (W)", color="Power (W)",
                         color_continuous_scale="Blues", template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with tech_col:
            st.subheader("📝 Technical Details")
            st.markdown(f"""
                <div class="tech-details">
                    <p><strong>Sky:</strong> {main_city['Description']}</p>
                    <p><strong>Thermal Factor:</strong> {main_city['Thermal Factor']}x</p>
                    <p><strong>Selected Efficiency:</strong> {eff_user}%</p>
                    <p><strong>Panel Nominal:</strong> {p_nom}W</p>
                </div>
            """, unsafe_allow_html=True)

        # C. Tabla Comparativa (Al final)
        st.divider()
        with st.expander("🔍 View Complete Comparison Table", expanded=True):
            st.table(df)
else:
    st.info("Please select one or more cities to begin.")