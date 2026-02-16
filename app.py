import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from src.processing import calculate_solar_output 

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Solar Energy Predictor", 
    page_icon="☀️", 
    layout="wide"
)

# 2. CSS PARA EL COLOR AZULADO Y VISIBILIDAD
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

# 3. HEADER
st.title("☀️ Solar Energy Production Estimator")
st.markdown("### Real-Time Photovoltaic Analysis & City Comparison")

# 4. SIDEBAR
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.secrets["OPENWEATHER_API_KEY"]
    
    # Selección múltiple de ciudades
    selected_cities = st.multiselect(
        "Select Cities to Compare:",
        ["Bogota", "Medellin", "Cali", "Barranquilla", "Miami", "Madrid", "Mexico City", "London", "Tokyo"],
        default=["Bogota", "Medellin"]
    )
    
    st.divider()
    p_nom = st.number_input("Nominal Power (Watts):", value=330)
    eff_user = st.slider("Efficiency (%)", 10.0, 25.0, 18.5)

# 5. LÓGICA DE OBTENCIÓN DE DATOS Y CÁLCULOS
if selected_cities:
    results_list = []

    for city in selected_cities:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                temp = data['main']['temp']
                clouds = data['clouds']['all']
                humidity = data['main']['humidity']
                desc = data['weather'][0]['description']

                # Cálculo usando tu función de processing.py
                res = calculate_solar_output(temp, clouds, p_nom, eff_user)
                
                results_list.append({
                    "City": city,
                    "Power (W)": res['power_output'],
                    "Temp (°C)": temp,
                    "Clouds (%)": clouds,
                    "Humidity (%)": humidity,
                    "Irradiance (W/m²)": res['irradiance'],
                    "Thermal Factor": res['thermal_factor'],
                    "Description": desc.capitalize()
                })
        except Exception as e:
            st.error(f"Error connecting for {city}: {e}")

    if results_list:
        df = pd.DataFrame(results_list)

        # 6. GRÁFICA DE BARRAS (Comparativa)
        st.subheader("📊 Power Output Comparison")
        fig = px.bar(
            df, 
            x="City", 
            y="Current Power (W)", 
            color="Power (W)",
            text_auto='.2f',
            color_continuous_scale="Blues",
            template="plotly_dark"
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # 7. MÉTRICAS Y DETALLES (De la primera ciudad seleccionada para mantener el diseño original)
        st.subheader(f"📍 Detailed Focus: {selected_cities[0]}")
        main_city = results_list[0]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature", f"{main_city['Temp (°C)']} °C")
        col2.metric("Cloudiness", f"{main_city['Clouds (%)']} %")
        col3.metric("Humidity", f"{main_city['Humidity (%)']} %")
        col4.metric("Irradiance", f"{main_city['Irradiance (W/m²)']} W/m²")

        st.divider()

        res_col, tech_col = st.columns([2, 1])

        with res_col:
            st.subheader("🚀 Performance Summary")
            st.success(f"### Current Power Output in {main_city['City']}: **{main_city['Power (W)']} Watts**")
            
            cap_ratio = min(main_city['Power (W)'] / p_nom, 1.0)
            st.write(f"System Capacity Utilization: {cap_ratio*100:.1f}%")
            st.progress(cap_ratio)

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

        # Tabla comparativa completa al final
        with st.expander("🔍 View Complete Comparison Table"):
            st.table(df)
else:
    st.info("Please select one or more cities in the sidebar to start the analysis.")