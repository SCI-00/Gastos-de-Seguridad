import pandas as pd
import os
from datetime import datetime
import io

FILE_NAME = "gastos_operacion_seguridad.xlsx"

# Columnas oficiales para la V2
COLUMNS = [
    "Fecha", "Estado", "Municipio", "CEDIS", "Categoría", "Concepto", 
    "Descripción", "Factura", "Cotización", "Monto", "Fecha_Registro"
]

def initialize_data():
    """Crea el archivo Excel si no existe, o lo actualiza si tiene formato viejo."""
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(FILE_NAME, index=False)
        return True
    else:
        # Migración simple: Si faltan columnas, agregarlas
        df = pd.read_excel(FILE_NAME)
        missing_cols = [c for c in COLUMNS if c not in df.columns]
        if missing_cols:
            for c in missing_cols:
                df[c] = "" if c not in ["Monto"] else 0.0
            # Reordenar
            df = df[COLUMNS]
            df.to_excel(FILE_NAME, index=False)
    return False

def load_data():
    """Carga los datos del archivo Excel."""
    initialize_data() # Asegura que el archivo tenga la estructura correcta
    try:
        return pd.read_excel(FILE_NAME)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def add_expense(data_dict):
    """
    Agrega un nuevo gasto.
    Recibe un diccionario con: fecha, estado, municipio, cedis, categoria, concepto, descripcion, factura, cotizacion, monto.
    """
    df = load_data()
    
    # Preparar nueva fila
    new_row = data_dict.copy()
    new_row["Fecha_Registro"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convertir a DataFrame
    new_entry = pd.DataFrame([new_row])
    
    # Concatenar y guardar
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(FILE_NAME, index=False)
    return True

def generate_excel_report():
    """
    Genera un archivo Excel en memoria con pestañas separadas por categoría.
    Retorna: Objeto BytesIO listo para descargar.
    """
    df = load_data()
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja General
        df.to_excel(writer, sheet_name="General", index=False)
        
        # Hojas por Categoría
        categorias = df["Categoría"].unique()
        for cat in categorias:
            # Limpiar nombre de pestaña (Excel no permite >31 chars o caracteres especiales)
            safe_name = str(cat)[:30].replace("/", "-")
            df_cat = df[df["Categoría"] == cat]
            df_cat.to_excel(writer, sheet_name=safe_name, index=False)
            
    output.seek(0)
    return output

def save_all_data(df):
    """
    Sobrescribe el archivo Excel con el DataFrame proporcionado (usado para ediciones/borrado).
    """
    try:
        # Asegurar que las columnas coincidan con la estructura oficial
        # Si faltan colummnas, las rellenamos, pero idealmente el editor mantiene la estructura
        df.to_excel(FILE_NAME, index=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False
