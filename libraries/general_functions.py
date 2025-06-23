import io
import re
import json
from typing import Any
import streamlit as st
from streamlit_float import float_init, float_parent

def to_csv_string(list_of_dicts):
    """
    Convierte una lista de diccionarios a una cadena de texto en formato CSV.
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
    #DEBE Ser re.DOTALL el pattern!
    for match in re.finditer(pattern, texto): 
        yield match.group("tipo"), match.group("contenido")

@st.cache_data
def _load_translations(path:str='translation.json') -> dict:
    """
    Carga las traducciones desde un archivo JSON.
    
    Args:
        path (str): Ruta al archivo JSON con las traducciones. default path: 'translation.json'
        
    Returns:
        dict: Diccionario con las traducciones.
    """
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
        return _load_translations()[lang if lang else st.session_state.get('lang_selected', 'en')].get(key, default)
    except Exception as e:
        print(f"Error al obtener la traducción para la clave '{key}': {e}")
        return f'CRITICAL ERROR LOADING {key} KEY' 

#Para testeo solamente, aun sin aplicar en produccion.
@st.fragment
def chat_button():
    float_init(theme=True)
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
    with st.container():
        if st.button("💬", key="chat_icon", help="Abrir chat de soporte"):
            st.session_state.show_chat = not st.session_state.show_chat
            st.rerun(scope='fragment')
        float_parent("""
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            z-index: 9999;
        """)
    if st.session_state.show_chat:
        with st.container():
            st.markdown("**🧑‍💻 Soporte en línea**")
            
            msg = st.text_input("Escribe tu mensaje:", key="chat_input", disabled=True)
            st.warning("Aún no se ha implementado esta función...")
            #f msg:
            #    st.success("Mensaje enviado. ¡Gracias por contactarnos!")
            
            float_parent("""
                bottom: 90px;
                right: 20px;
                width: 300px;
                background-color: black;
                padding: 15px;
                border: 1px solid #ccc;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
                z-index: 9998;
            """)