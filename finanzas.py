import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Archivo de datos
DATA_FILE = "registro_financiero.json"

# Configuración de la página web
st.set_page_config(page_title="Analizador Financiero Corporativo", page_icon="🏢", layout="wide")

# Funciones de datos
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"registros": []}
    return {"registros": []}

def guardar_datos(datos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# Cargar la base de datos local
datos = cargar_datos()
df = pd.DataFrame(datos["registros"])

# Título Principal en la Web
st.title("🏢 Analizador de Días Financieros")
st.markdown("Plataforma corporativa para el control de ingresos, gastos y rendimiento operativo.")
st.divider()

# =========================================================
# BARRA LATERAL (Para registrar nuevos datos)
# =========================================================
st.sidebar.header("📝 Registrar Operación Diaria")
with st.sidebar.form("formulario_registro"):
    fecha = st.date_input("Fecha de Registro", datetime.now())
    ingresos = st.number_input("Ingresos del Día ($)", min_value=0.0, step=100.0, format="%.2f")
    gastos = st.number_input("Gastos del Día ($)", min_value=0.0, step=100.0, format="%.2f")
    boton_guardar = st.form_submit_button("Guardar Registro")

if boton_guardar:
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    # Validar si ya existe la fecha
    existe = False
    for r in datos["registros"]:
        if r["fecha"] == fecha_str:
            existe = True
            break
            
    if existe:
        st.sidebar.error(f"⚠️ Ya existe un registro para el día {fecha_str}")
    else:
        ganancia = ingresos - gastos
        estado = "ganancia" if ganancia > 0 else "perdida" if ganancia < 0 else "equilibrio"
        
        nuevo = {
            "fecha": fecha_str,
            "ingresos": ingresos,
            "gastos": gastos,
            "ganancia": ganancia,
            "estado": estado
        }
        datos["registros"].append(nuevo)
        guardar_datos(datos)
        st.sidebar.success("✅ ¡Día registrado con éxito!")
        st.rerun() # Recarga la página para mostrar los datos nuevos

# =========================================================
# CUADRO PRINCIPAL (Visualización Profesional)
# =========================================================
if df.empty:
    st.info("💡 No hay registros financieros aún. Utiliza el panel de la izquierda para agregar datos.")
else:
    # 1. TARJETAS DE MÉTRICAS (KPIs de Empresa)
    total_ingresos = df["ingresos"].sum()
    total_gastos = df["gastos"].sum()
    balance_total = total_ingresos - total_gastos
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="💰 Total Ingresos", value=f"${total_ingresos:,.2f}")
    col2.metric(label="💸 Total Gastos", value=f"${total_gastos:,.2f}")
    col3.metric(
        label="📊 Balance Neto", 
        value=f"${balance_total:,.2f}", 
        delta=f"${balance_total:,.2f}",
        delta_color="normal" if balance_total >= 0 else "inverse"
    )
    
    st.divider()
    
    # 2. GRÁFICO EVOLUTIVO INTERACTIVO
    st.subheader("📈 Tendencia Financiera")
    df_ordenado = df.sort_values("fecha")
    st.line_chart(df_ordenado.set_index("fecha")[["ingresos", "gastos", "ganancia"]])
    
    st.divider()
    
    # 3. TABLA DE DATOS Y TOP 5
    col_tabla, col_tops = st.columns([2, 1])
    
    with col_tabla:
        st.subheader("📋 Historial de Registros")
        st.dataframe(df_ordenado, use_container_width=True)
        
        # Botón para borrar base de datos
        if st.button("🗑️ Eliminar todos los datos"):
            datos["registros"] = []
            guardar_datos(datos)
            st.success("Base de datos limpiada.")
            st.rerun()
            
    with col_tops:
        st.subheader("🏆 Rendimiento Destacado")
        
        mejores = df.sort_values(by="ganancia", ascending=False).head(3)
        st.markdown("**Top 3 Días con Más Ganancia:**")
        for idx, fila in mejores.iterrows():
            st.write(f"🟢 {fila['fecha']}: *${fila['ganancia']:,.2f}*")
            
        peores = df[df["ganancia"] < 0].sort_values(by="ganancia").head(3)
        st.markdown("**Top 3 Días con Más Pérdida:**")
        if peores.empty:
            st.write("🎉 ¡No hay días con pérdidas registrados!")
        else:
            for idx, fila in peores.iterrows():
                st.write(f"🔴 {fila['fecha']}: *${fila['ganancia']:,.2f}*")
