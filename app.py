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
    st.sidebar.info("v2.1 - Edición Profesional")

    # --- FILTROS GLOBALES (Solo aplican al Dashboard y Reportes) ---
    st.sidebar.markdown("### 🔍 Filtros de Visualización")
    
    # Clonar datos para filtrar sin perder los originales
    df_filtered = df.copy()
    
    # 1. Filtro de Fechas
    st.sidebar.markdown("**Rango de Fechas:**")
    today = date.today()
    start_date = st.sidebar.date_input("Inicio", today.replace(day=1))
    end_date = st.sidebar.date_input("Fin", today)
    
    # Aplicar filtro de fecha
    if not df_filtered.empty:
        df_filtered["Fecha"] = pd.to_datetime(df_filtered["Fecha"]).dt.date
        df_filtered = df_filtered[(df_filtered["Fecha"] >= start_date) & (df_filtered["Fecha"] <= end_date)]

    # 2. Filtro de CEDIS
    cedis_options = df["CEDIS"].unique().tolist() if "CEDIS" in df.columns else []
    selected_cedis = st.sidebar.multiselect("Filtrar por CEDIS", cedis_options)
    if selected_cedis:
        df_filtered = df_filtered[df_filtered["CEDIS"].isin(selected_cedis)]

    # 3. Filtro de Categoría
    cat_options = df["Categoría"].unique().tolist()
    selected_cats = st.sidebar.multiselect("Filtrar por Categoría", cat_options)
    if selected_cats:
        df_filtered = df_filtered[df_filtered["Categoría"].isin(selected_cats)]


    # --- VISTA: DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<div class='main-header'>Dashboard Financiero de Seguridad</div>", unsafe_allow_html=True)
        st.markdown(f"**Viendo datos del:** {start_date} al {end_date}")
        
        if df_filtered.empty:
            st.warning("No hay datos con los filtros seleccionados.")
            return

        # KPIs Superiores
        total_gasto = df_filtered["Monto"].sum()
        total_ops = len(df_filtered)
        # Promedio por operación
        avg_ticket = total_gasto / total_ops if total_ops > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Gasto Total (Filtrado)", f"${total_gasto:,.2f} MXN")
        c2.metric("Total Operaciones", total_ops)
        c3.metric("Ticket Promedio", f"${avg_ticket:,.2f} MXN")
        
        st.divider()

        # Gráficos Fila 1
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Distribución por Categoría")
            fig_pie = px.pie(df_filtered, values='Monto', names='Categoría', hole=0.4, 
                             color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_g2:
            st.subheader("Tendencia de Gastos (Tiempo)")
            if not df_filtered.empty:
                df_trend = df_filtered.groupby("Fecha")["Monto"].sum().reset_index()
                fig_line = px.line(df_trend, x='Fecha', y='Monto', markers=True, 
                                   line_shape="spline", color_discrete_sequence=["#1E3A8A"])
                st.plotly_chart(fig_line, use_container_width=True)

        # Gráficos Fila 2 (Nuevos)
        st.divider()
        col_g3, col_g4 = st.columns(2)

        with col_g3:
            st.subheader("🏆 Top 5 Proveedores")
            if "Proveedor" in df_filtered.columns:
                df_prov = df_filtered.groupby("Proveedor")["Monto"].sum().reset_index().sort_values("Monto", ascending=False).head(5)
                fig_bar_prov = px.bar(df_prov, x="Monto", y="Proveedor", orientation='h', 
                                      text_auto='.2s', color="Monto", color_continuous_scale="Viridis")
                st.plotly_chart(fig_bar_prov, use_container_width=True)
        
        with col_g4:
            st.subheader("Gastos por CEDIS")
            if "CEDIS" in df_filtered.columns:
                df_cedis = df_filtered.groupby("CEDIS")["Monto"].sum().reset_index().sort_values("Monto", ascending=False).head(10)
                fig_bar_cedis = px.bar(df_cedis, x="CEDIS", y="Monto", text_auto='.2s', 
                                       color="CEDIS", color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_bar_cedis, use_container_width=True)


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
                
                # Lógica para "Concepto" y "Otros"
                conceptos_disponibles = CAT_CONCEPT_MAP[categoria_sel]
                concepto_pre = st.selectbox("Concepto / Subcategoría", conceptos_disponibles)
                
                # Si elige "Varios" u "Otros" en la subcategoría, permitir texto libre
                # O si la categoría principal es "Otros"
                concepto_final = concepto_pre
                if categoria_sel == "Otros" or concepto_pre in ["Varios", "Otros"]:
                    concepto_custom = st.text_input("Especificar Concepto (Escribe manual):")
                    if concepto_custom:
                        concepto_final = concepto_custom

            with c5:
                # Proveedor (Nuevo campo)
                proveedor = st.text_input("Proveedor (Empresa / Persona)")
                descripcion = st.text_area("Descripción Detallada", height=10) # Altura ajustada

            c6, c7, c8 = st.columns(3)
            with c6:
                monto = st.number_input("Monto Total (MXN)", min_value=0.0, format="%.2f")
            with c7:
                factura = st.text_input("No. Factura (Opcional)")
            with c8:
                cotizacion = st.text_input("No. Cotización (Opcional)")
            
            submitted = st.form_submit_button("💾 Guardar Registro en Sistema")
            
            if submitted:
                if monto > 0 and proveedor: # Validar Proveedor también
                    data = {
                        "Fecha": fecha,
                        "Estado": estado,
                        "Municipio": municipio,
                        "CEDIS": cedis,
                        "Categoría": categoria_sel,
                        "Concepto": concepto_final, # Usar el concepto dinámico
                        "Descripción": descripcion,
                        "Proveedor": proveedor,
                        "Factura": factura,
                        "Cotización": cotizacion,
                        "Monto": monto
                    }
                    data_manager.add_expense(data)
                    st.success("✅ Gasto registrado exitosamente.")
                else:
                    st.error("⚠️ El monto y el Proveedor son obligatorios.")


    # --- VISTA: REPORTES ---
    elif menu == "📂 Reportes":
        st.header("Centro de Reportes")
        st.info("💡 Los filtros de la barra lateral también aplican a este reporte.")
        
        st.write(f"Mostrando {len(df_filtered)} registros filtrados.")
        st.dataframe(df_filtered, use_container_width=True)
        
        st.write("---")
        st.markdown("### 📥 Descargar Reporte Segmentado (Filtrado)")
        st.write("Este reporte generará un Excel con los datos que ves en pantalla, separado por categorías.")
        
        if st.button("Generar Archivo Excel"):
            # Generar reporte usando los datos filtrados
            excel_data = data_manager.generate_excel_report(df_filtered)
            st.download_button(
                label="⬇️ Descargar Excel Filtrado",
                data=excel_data,
                file_name=f"Reporte_Seguridad_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- VISTA: EDICIÓN ---
    elif menu == "⚙️ Editar Registros":
        st.header("🛠️ Administrador de Registros")
        
        # Nota: Aquí mostramos TODO (sin filtrar) para evitar borrar algo por error oculto, 
        # o podríamos aplicar filtro si el usuario quiere.
        # Por seguridad, dejemos que edite todo el dataset crudo.
        
        st.info("""
        **Modo Edición Total:** Aquí se muestran TODOS los registros (sin filtros) para mantenimiento.
        1. **Editar:** Haz doble clic en cualquier celda.
        2. **Borrar:** Selecciona las filas y presiona `Supr`.
        3. **Guardar:** Clic en "Guardar Cambios".
        """)

        # Editor de Datos
        edited_df = st.data_editor(
            df, # Usamos df completo, no filtrado
            num_rows="dynamic",
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
