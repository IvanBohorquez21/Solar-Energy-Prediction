import streamlit as st
import requests
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
    /* Fondo de la aplicación */
    .main { background-color: #0e1117; }
    
    /* Tarjetas de métricas en AZUL OSCURO (estilo Dashboard profesional) */
    [data-testid="stMetric"] {
        background-color: #1a232e; /* Azul oscuro azulado */
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #2d3a4b;
    }
    
    /* Texto de las métricas en blanco */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8094ad !important;
    }

    /* Caja de Technical Details */
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
st.markdown("### Real-Time Photovoltaic Analysis Dashboard")

# 4. SIDEBAR
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.secrets["OPENWEATHER_API_KEY"]
    city = st.text_input("City Name:", value="Bogota")
    st.divider()
    p_nom = st.number_input("Nominal Power (Watts):", value=330)
    eff_user = st.slider("Efficiency (%)", 10.0, 25.0, 18.5)

# 5. LÓGICA DE API Y CÁLCULOS
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

try:
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        temp = data['main']['temp']
        clouds = data['clouds']['all']
        humidity = data['main']['humidity']
        desc = data['weather'][0]['description']

        # Llamada a la capa de procesamiento
        results = calculate_solar_output(temp, clouds, p_nom, eff_user)

        # 6. FILA DE MÉTRICAS (SUPERIOR)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature", f"{temp} °C")
        col2.metric("Cloudiness", f"{clouds} %")
        col3.metric("Humidity", f"{humidity} %")
        col4.metric("Irradiance", f"{results['irradiance']} W/m²")

        st.divider()

        # 7. SECCIÓN INFERIOR: RESULTADOS + TECHNICAL DETAILS
        res_col, tech_col = st.columns([2, 1])

        with res_col:
            st.subheader("🚀 Estimated Performance")
            st.success(f"### Current Power Output: **{results['power_output']} Watts**")
            
            # Barra de progreso
            cap_ratio = min(results['power_output'] / p_nom, 1.0)
            st.write(f"System Capacity Utilization: {cap_ratio*100:.1f}%")
            st.progress(cap_ratio)

        with tech_col:
            # Reinsertamos la sección de Technical Details con el estilo azul
            st.subheader("📝 Technical Details")
            st.markdown(f"""
                <div class="tech-details">
                    <p><strong>Sky:</strong> {desc.capitalize()}</p>
                    <p><strong>Thermal Factor:</strong> {results['thermal_factor']}x</p>
                    <p><strong>Selected Efficiency:</strong> {eff_user}%</p>
                    <p><strong>Panel Nominal:</strong> {p_nom}W</p>
                </div>
            """, unsafe_allow_html=True)

    else:
        st.error(f"API Error: {data.get('message')}")

except Exception as e:
    st.error(f"Connection error: {e}")