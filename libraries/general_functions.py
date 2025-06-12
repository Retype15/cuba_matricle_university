import io
import re
import json
from typing import Any
import streamlit as st

def to_csv_string(list_of_dicts):
    """
    Convierte una lista de diccionarios a una cadena de texto en formato CSV.
    Es mucho más eficiente que JSON para datos tabulares.
    """
    if not list_of_dicts:
        return ""
    
    output = io.StringIO()
    headers = list_of_dicts[0].keys()
    output.write(','.join(headers) + '\n')
    
    for row_dict in list_of_dicts:
        row = [str(row_dict.get(h, '')) for h in headers]
        output.write(','.join(row) + '\n')
        
    return output.getvalue().strip()


def parse_blocks(pattern, texto):
    """
    Encuentra bloques de texto delimitados por ```tipo y ``` en el texto dado.
    Devuelve un iterador con tuplas (tipo, contenido) para cada bloque encontrado.

    Args:
        texto (str): El texto a analizar.

    Yields:
        tuple: Una tupla (tipo, contenido) para cada bloque encontrado.
    """
    for match in re.finditer(pattern, texto): #DEBE SEr  re.DOTALL el pattern!
        yield match.group("tipo"), match.group("contenido")

@st.cache_data
def _load_translations() -> dict:
    """
    Carga las traducciones desde un archivo JSON.
    
    Args:
        path (str): Ruta al archivo JSON con las traducciones.
        
    Returns:
        dict: Diccionario con las traducciones.
    """
    path = 'translation.json'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: El archivo {path} no se encontró.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: El archivo {path} no es un JSON válido.")
        return {}

def translation(key:str, default:Any=None, lang:str|None = None) -> str|dict|list:
    """
    Obtiene la traducción para una clave específica.
    
    Args:
        key (str): Clave de la traducción.
        
    Returns:
        str: Traducción correspondiente a la clave.
    """
    try:
        return _load_translations()[lang if lang else st.session_state.get('lang_sel', 'en')].get(key, default)
    except Exception as e:
        print(f"Error al obtener la traducción para la clave '{key}': {e}")
        return 'CRITICAL: '+key
