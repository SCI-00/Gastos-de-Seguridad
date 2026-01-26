import pandas as pd
import os
from datetime import datetime
import io
import streamlit as st
from streamlit_gsheets import GSheetsConnection

FILE_NAME = "gastos_operacion_seguridad.xlsx"

# Columnas oficiales para la V2
COLUMNS = [
    "Fecha", "Estado", "Municipio", "CEDIS", "Categoría", "Concepto", 
    "Descripción", "Proveedor", "Factura", "Cotización", "Monto", "Fecha_Registro"
]

def get_connection():
    """Intenta obtener la conexión a Google Sheets."""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        return None

def initialize_data():
    """
    Verifica la conexión. Si es local, crea el Excel.
    Si es remoto (Sheets), confiamos en que la hoja existe o se creará al escribir.
    """
    conn = get_connection()
    # Si no hay conexión (ej. local sin secretos), usar modo Local
    if conn is None:
        if not os.path.exists(FILE_NAME):
            df = pd.DataFrame(columns=COLUMNS)
            df.to_excel(FILE_NAME, index=False)
            return True
        else:
            # Migración simple local
            try:
                df = pd.read_excel(FILE_NAME)
                missing_cols = [c for c in COLUMNS if c not in df.columns]
                if missing_cols:
                    for c in missing_cols:
                        df[c] = "" if c != "Monto" else 0.0
                    df = df[COLUMNS]
                    df.to_excel(FILE_NAME, index=False)
            except:
                pass
    return False

def load_data():
    """Carga los datos desde Google Sheets (Prioridad) o Excel Local (Fallback)."""
    conn = get_connection()
    
    # 1. Intentar cargar de Google Sheets
    if conn:
        try:
            # ttl=0 asegura que no cachee y siempre traiga datos frescos
            df = conn.read(ttl=0)
            
            # Si la hoja está vacía o nueva, normalizar columnas
            if df.empty:
                return pd.DataFrame(columns=COLUMNS)
                
            # Asegurar que tenga todas las columnas requeridas
            missing_cols = [c for c in COLUMNS if c not in df.columns]
            for c in missing_cols:
                df[c] = "" if c != "Monto" else 0.0
            
            # Filtrar solo columnas oficiales y reordenar
            # (Esto evita errores si la hoja tiene columnas extra de metadatos)
            valid_cols = [c for c in df.columns if c in COLUMNS]
            return df[valid_cols]
        except Exception as e:
            # Si falla (ej. tabla no existe, error de red), intentar local pero avisar
            st.warning(f"⚠️ No se pudo conectar a Google Sheets: {e}. Usando modo local temporal.")
    
    # 2. Modo Local (Fallback)
    initialize_data()
    try:
        return pd.read_excel(FILE_NAME)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def add_expense(data_dict):
    """
    Agrega un nuevo gasto a Google Sheets o Local.
    """
    # Cargar datos actuales (esto ya maneja la lógica de dónde leer)
    df = load_data()
    
    # Preparar nueva fila
    new_row = data_dict.copy()
    new_row["Fecha_Registro"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convertir a DataFrame la nueva fila
    new_entry = pd.DataFrame([new_row])
    
    # Concatenar
    # Aseguramos que df tenga las columnas correctas antes de concatenar
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
            
    df_updated = pd.concat([df, new_entry], ignore_index=True)
    df_updated = df_updated[COLUMNS] # Forzar orden y limpieza
    
    conn = get_connection()
    
    # 1. Intentar guardar en Google Sheets
    if conn:
        try:
            conn.update(data=df_updated)
            return True
        except Exception as e:
            st.error(f"❌ Error guardando en Nube: {e}")
            # Intentar guardar local como respaldo de emergencia
    
    # 2. Guardar Local (Fallback o emergencia)
    try:
        df_updated.to_excel(FILE_NAME, index=False)
        return True
    except Exception as e:
        st.error(f"Error crítico guardando datos: {e}")
        return False

def generate_excel_report(df_filtered=None):
    """Genera reporte Excel descargable."""
    if df_filtered is None:
        df = load_data()
    else:
        df = df_filtered

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="General", index=False)
        if not df.empty and "Categoría" in df.columns:
            categorias = df["Categoría"].unique()
            for cat in categorias:
                if pd.notna(cat):
                    safe_name = str(cat)[:30].replace("/", "-")
                    df_cat = df[df["Categoría"] == cat]
                    df_cat.to_excel(writer, sheet_name=safe_name, index=False)
    output.seek(0)
    return output

def save_all_data(df):
    """Sobrescribe toda la base de datos (Ej. tras editar en grid)."""
    conn = get_connection()
    
    # Asegurar formato
    df = df[COLUMNS]
    
    if conn:
        try:
            conn.update(data=df)
            return True
        except Exception as e:
            st.error(f"Error actualizando nube: {e}")
            
    try:
        df.to_excel(FILE_NAME, index=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False
