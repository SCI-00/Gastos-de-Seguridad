import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import data_manager

# --- Configuración de Categorías y Conceptos (Basado en la imagen del usuario) ---
CAT_CONCEPT_MAP = {
    "Seguridad Patrimonial": [
        "Servicio de Monitoreo de Alarmas ADT",
        "Kits de Alarmas ADT",
        "Seguridad Privada",
        "Equipos de Emergencia",
        "Renta GPS Vehículos Utilitarios",
        "Inspección de Protección Patrimonial a Cedis"
    ],
    "Protección Civil": [
        "Visto Bueno de Proteccion Civil por Tercer Acreditado",
        "Capacitación de Proteccion Civil por Tercer Acreditado",
        "Cuotas y/o Donaciones Solicitadas por Autoridades",
        "Dictamen Eléctrico",
        "Dictamen Estructural",
        "Licencia/Permiso Ambiental",
        "Programa Interno de PC"
    ],
    "Seguridad y Salud": [
        "Mantenimiento y Recarga de Extintores",
        "Equipo de Protección Personal (EPP)",
        "Señalética",
        "Exámenes Médicos",
        "Botiquines"
    ],
    "Otros": ["Varios", "Administrativo"]
}

ESTADOS_MX = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas", "Chihuahua",
    "Ciudad de México", "Coahuila", "Colima", "Durango", "Guanajuato", "Guerrero", "Hidalgo",
    "Jalisco", "México", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla",
    "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas",
    "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"
]

LISTA_CEDIS = [
    "Acayucan", "Ciudad Neza", "Coatzacoalcos", "Colonia Roma", "Cordoba", "Cuautitlan", 
    "Ecatepec", "Izucar de Matamoros", "Martinez de la Torre", "Poza Rica Veracruz", 
    "Puebla Norte", "Puebla Sur", "San Andres Tuxtla", "Satelite", "Tehuacan", "Texcoco", 
    "Tlalnepantla", "Tlalpan (Acoxpa)", "Toluca", "Veracruz", "Xalapa", "Ensenada", 
    "Mexicali", "Tijuana", "La Paz", "Chihuahua OMNILIFE ft SEYTÚ", "Ciudad Juárez", 
    "Saltillo", "Torreon", "Durango", "Guadalupe", "Monterrey", "Culiacan", "Los Mochis", 
    "Mazatlan", "Hermosillo", "San Luis Rio Colorado", "Ciudad Victoria", "Matamoros", 
    "Nuevo Laredo", "Reynosa", "Tampico", "Aguascalientes", "Colima", "Irapuato", "León", 
    "Acapulco", "Pachuca", "Ecocentro", "Patria (Amistad)", "Prisciliano", "Puerto Vallarta", 
    "Tlaquepaque", "La Piedad", "Lazaro Cardenas", "Morelia", "Uruapan", "Cuernavaca", 
    "Tepic", "Queretaro", "San Luis Potosi", "Zacatecas", "Campeche", "Cancún", "Chetumal", 
    "Ciudad del Carmen", "Comalcalco", "Comitan", "Huajuapan de Leon", "Merida", 
    "Merida Norte", "Merida Hub", "Oaxaca", "Playa del Carmen", "Puerto Escondido", 
    "Salina Cruz", "San Cristobal", "Tapachula", "Tenosique", "Tuxtepec", 
    "Tuxtla Gutierrez", "Villahermosa"
]
LISTA_CEDIS.sort() # Ordenar alfabéticamente para facilitar la búsqueda

# Configuración de la página
st.set_page_config(page_title="Gestión de Seguridad PRO", page_icon="🛡️", layout="wide")

# CSS Profesional
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        font-weight: 700;
    }
    .metric-container {
        background-color: #ffffff;
        border-left: 5px solid #1E3A8A;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Inicializar datos
    data_manager.initialize_data()
    df = data_manager.load_data()

    # --- Sidebar de Navegación ---
    st.sidebar.title("🛡️ Panel de Control")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Ir a:", ["📊 Dashboard", "📝 Registrar Gasto", "📂 Reportes", "⚙️ Editar Registros"])
    
    st.sidebar.markdown("---")
    st.sidebar.info("v2.0 - Edición Profesional")

    # --- VISTA: DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<div class='main-header'>Dashboard Financiero de Seguridad</div>", unsafe_allow_html=True)
        st.write("") # Espacio
        
        if df.empty:
            st.warning("No hay datos para mostrar. Ve a 'Registrar Gasto' para comenzar.")
            return

        # KPIs Superiores
        total_gasto = df["Monto"].sum()
        gasto_mes = df[pd.to_datetime(df["Fecha"]).dt.month == date.today().month]["Monto"].sum()
        top_cat = df.groupby("Categoría")["Monto"].sum().idxmax()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Gasto Total Histórico", f"${total_gasto:,.2f} MXN")
        c2.metric("Gasto Este Mes", f"${gasto_mes:,.2f} MXN")
        c3.metric("Categoría Más Costosa", top_cat)
        
        st.divider()

        # Gráficos
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Distribución por Categoría")
            fig_pie = px.pie(df, values='Monto', names='Categoría', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_g2:
            st.subheader("Tendencia de Gastos")
            # Agrupar por fecha
            df_trend = df.groupby("Fecha")["Monto"].sum().reset_index()
            fig_line = px.line(df_trend, x='Fecha', y='Monto', markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

    # --- VISTA: REGISTRO ---
    elif menu == "📝 Registrar Gasto":
        st.markdown("<h2 style='text-align: center;'>Nuevo Registro Operativo</h2>", unsafe_allow_html=True)
        
        with st.form("entry_form", clear_on_submit=True):
            st.markdown("#### 1. Datos Generales")
            c1, c2, c3, c_cedis = st.columns(4)
            with c1:
                fecha = st.date_input("Fecha", value=date.today())
            with c2:
                estado = st.selectbox("Estado", ESTADOS_MX)
            with c3:
                municipio = st.text_input("Municipio")
            with c_cedis:
                cedis = st.selectbox("CEDIS / Sucursal", LISTA_CEDIS)

            st.markdown("#### 2. Detalle Financiero")
            c4, c5 = st.columns(2)
            with c4:
                # Selección Inteligente
                categoria_sel = st.selectbox("Categoría Principal", list(CAT_CONCEPT_MAP.keys()))
                # Subcategoría dinámica basada en la selección anterior
                conceptos_disponibles = CAT_CONCEPT_MAP[categoria_sel]
                concepto_sel = st.selectbox("Concepto / Subcategoría", conceptos_disponibles)
            with c5:
                # Descripción libre
                descripcion = st.text_area("Descripción Detallada", height=108)

            c6, c7, c8 = st.columns(3)
            with c6:
                monto = st.number_input("Monto Total (MXN)", min_value=0.0, format="%.2f")
            with c7:
                factura = st.text_input("No. Factura (Opcional)")
            with c8:
                cotizacion = st.text_input("No. Cotización (Opcional)")
            
            submitted = st.form_submit_button("💾 Guardar Registro en Sistema")
            
            if submitted:
                if monto > 0:
                    data = {
                        "Fecha": fecha,
                        "Estado": estado,
                        "Municipio": municipio,
                        "CEDIS": cedis,
                        "Categoría": categoria_sel,
                        "Concepto": concepto_sel,
                        "Descripción": descripcion,
                        "Factura": factura,
                        "Cotización": cotizacion,
                        "Monto": monto
                    }
                    data_manager.add_expense(data)
                    st.success("✅ Gasto registrado exitosamente.")
                else:
                    st.error("⚠️ El monto debe ser mayor a 0.")

    # --- VISTA: REPORTES ---
    elif menu == "📂 Reportes":
        st.header("Centro de Reportes")
        st.write("Aquí puedes visualizar la base de datos completa y descargarla.")
        
        st.dataframe(df, use_container_width=True)
        
        st.write("---")
        st.markdown("### 📥 Descargar Reporte Segmentado")
        st.write("Este reporte generará un Excel con pestañas separadas por cada categoría.")
        
        if st.button("Generar Archivo Excel"):
            excel_data = data_manager.generate_excel_report()
            st.download_button(
                label="⬇️ Descargar Excel Segmentado",
                data=excel_data,
                file_name=f"Reporte_Seguridad_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- VISTA: EDICIÓN ---
    elif menu == "⚙️ Editar Registros":
        st.header("🛠️ Administrador de Registros")
        st.info("""
        **Instrucciones:**
        1. **Editar:** Haz doble clic en cualquier celda para cambiar su valor.
        2. **Borrar:** Selecciona las filas (casilla izquierda) y presiona la tecla `Supr` o `Del`.
        3. **IMPORTANTE:** Al finalizar, dale clic al botón **"💾 Guardar Cambios"** para actualizar el Excel.
        """)

        # Editor de Datos
        edited_df = st.data_editor(
            df,
            num_rows="dynamic", # Permite añadir/borrar filas
            use_container_width=True,
            key="editor_gastos",
            column_config={
                "Monto": st.column_config.NumberColumn(format="$%.2f"),
                "Fecha": st.column_config.DateColumn(format="YYYY-MM-DD"),
            }
        )

        if st.button("💾 Guardar Cambios Realizados"):
            if data_manager.save_all_data(edited_df):
                st.success("✅ ¡Base de datos actualizada correctamente!")
                st.rerun() # Recargar la página para ver cambios
            else:
                st.error("❌ Hubo un error al guardar.")

if __name__ == "__main__":
    main()
