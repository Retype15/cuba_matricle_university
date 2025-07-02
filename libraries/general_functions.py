import io
import re
import json
from typing import Any, Callable, Dict, List, Optional
from language_detection  import detect_browser_language
import streamlit as st
from .streamlit_float_upd import float_init, float_parent

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
    #Acordarse DEBE ser re.DOTALL el pattern!
    for match in re.finditer(pattern, texto): 
        yield match.group("tipo"), match.group("contenido")

@st.cache_data
def _load_translations(path:str='translation.json') -> dict: #TODO:deprecated
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

def translation(key:str, default:Any=None, lang:str|None = None) -> Any: #TODO:deprecated
    
    """
    Obtiene la traducción para una clave específica.
    
    Args:
        key (str): Clave de la traducción.
        default (Optional[Any]): Clave por defecto si no existe la key en el idioma seleccionado.
        lang (Optional[Str]): fuerza el idioma del que quieres recibir el valor
        
    Returns:
        str: Valor correspondiente a la clave.
    """
    return default
    try:
        return _load_translations()[lang if lang else st.session_state.get('lang_selected', 'en')].get(key, default)
    except Exception as e:
        print(f"Error al obtener la traducción para la clave '{key}': {e}")
        return f'CRITICAL ERROR LOADING {key} KEY' 


@st.cache_data
def _get_language_dict(lang_code: str, dir:str='languages') -> dict:
    """Carga un archivo de traducción desde el disco. Advertencia, Cacheado por Streamlit, por lo que si cambia el archivo de traduccion deberá borrar la chaché."""
    path = f"{dir}/{lang_code}.json"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Archivo de traducción no encontrado: {path}")
        return {}
    except json.JSONDecodeError:
        st.error(f"Error al decodificar el archivo JSON: {path}")
        return {}

class LanguageSelector:
    """
    Un componente singleton para gestionar la selección de idioma y las traducciones
    en una aplicación Streamlit.
    
    Uso:
        # Al inicio de tu script
        lang_selector = LanguageSelector(langs={"English": "en", "Español": "es"})
        t = lang_selector.translate # Alias para facilitar el uso

        # En tu app
        st.title(t('welcome_title', "Welcome to my App"))
        lang_selector.render()
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if 'language_selector_instance' not in st.session_state:
            st.session_state.language_selector_instance = super().__new__(cls)
        return st.session_state.language_selector_instance

    def __init__(self, langs: Dict[str, str] = {"English": 'en'}, lang_dir: str = "languages"):
        """
        Inicializa el selector de idioma. Solo se ejecuta una vez por sesión.
        
        Args:
            langs (dict): Un diccionario con el nombre legible del idioma como clave
                          y el código de idioma (ej. 'en') como valor.
            lang_dir (str): El directorio donde se encuentran los archivos .json de idioma.
        """
        if hasattr(self, '_initialized'): return
        
        self.langs = langs
        self.langs_list = list(langs.values())
        self.langs_readable = list(langs.keys())
        self.lang_dir = lang_dir

        self.actual_lang = detect_browser_language() or self.langs_list[0]
        
        try:
            self.lang_index = self.langs_list.index(self.actual_lang)
        except ValueError:
            self.lang_index = 0

        self._initialized = True
        
    def translate(self, key: str, default: Any = None, *, lang: str | None = None) -> Any:
        """
        Obtiene una cadena de traducción para una clave dada.

        Args:
            key (str): La clave de traducción a buscar en el archivo JSON.
            default (Any, optional): Un valor por defecto si la clave no se encuentra.
                                     Si no se proporciona, la clave misma será devuelta.
            lang (str, optional): Un código de idioma para usar en esta traducción específica,
                                  ignorando el idioma seleccionado actualmente.

        Returns:
            Any: El valor traducido, el valor por defecto o la clave.
        """
        final_lang = lang or self.actual_lang
        if final_lang not in self.langs_list: raise ValueError(f"Idioma no reconocido: {final_lang}")
            
        return _get_language_dict(final_lang, dir=self.lang_dir).get(key, f"warn--{default}" or f"[{final_lang}] Missing translation for '{key}'")

    def render(self):
        """Renderiza el selectbox en la barra lateral para cambiar de idioma."""
        
        lang_readable_selected = st.sidebar.selectbox(
            label="Language / Idioma", 
            options=self.langs_readable, 
            index=self.lang_index,
            help=self.translate(
                'lang_select_help', 
                "Select your preferred language for the application."
            )
        )
        
        selected_lang_code = self.langs.get(lang_readable_selected)

        if selected_lang_code and selected_lang_code != self.actual_lang:
            self.lang_index = self.langs_list.index(selected_lang_code)
            self.actual_lang = selected_lang_code
            st.rerun(scope='app')

#Para testeo solamente, aun sin aplicar en produccion.
@st.fragment
def chat_button(*args: Callable):
    float_init(theme=True)
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
    with st.container():
        if st.button("🎮", key="chat_icon", help="Abrir Puntuación"):
            st.session_state.show_chat = not st.session_state.show_chat
            st.rerun(scope='fragment')
        float_parent("""
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
        """)
    if st.session_state.show_chat:
        with st.container():
            for callo in args: callo()
            
            float_parent("""
                bottom: 90px;
                right: 20px;
                width: 300px;
                background-color: black;
                padding: 15px;
                border: 1px solid #ccc;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            """)

class FloatingPanel:
    """
    Creates a floating panel that can be shown or hidden using a button,
    with dynamic content and independent state.
    """

    def __init__(self,
                 key: str,
                 content_funcs: List[Callable]=[],
                 button_icon: str = "💬",
                 button_tooltip: str = "Open panel",
                 css_button: str | None = None,
                 css_panel: str | None = None):
        """
        Initializes an instance of a floating panel.

        Args:
            key (str): A unique and required key for this panel.
                       Allows for multiple independent panels on the same page.
            content_funcs (List[Callable]): A list of functions to be called
                                            to render the content inside the panel.
            button_icon (str): The icon or text for the toggle button.
            button_tooltip (str): The tooltip text that appears when hovering over the button.
            css_button (str): CSS for the floating button.
            css_panel (str): CSS for the content panel.
        """
        self.key = key
        self.content_funcs = content_funcs
        self.button_icon = button_icon
        self.button_tooltip = button_tooltip
        self.state_key = f"show_panel_{self.key}"

        self.css_button = css_button or """
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
        """
        self.css_panel = css_panel or """
        bottom: 90px;
        right: 20px;
        width: 350px;
        background-color: rgba(10, 10, 10, 0.9);
        color: #F0F0F0;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #333;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.45);
        transition: transform 2s ease, opacity 1s ease;
        z-index: 1000;

        :hover {
        transform: translateY(-0.1px);
        }
        """

        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = False

    def _toggle_state(self):
        """Toggles the panel's visibility state."""
        st.session_state[self.state_key] = not st.session_state[self.state_key]

    def add_funtion(self, *args:Callable, funcs: List[Callable]|Callable=[]):
        """Add as a functions elements on the floating panel."""
        if args:
            self.content_funcs.extend(args)
        if isinstance(funcs, List):
            self.content_funcs.extend(funcs)
        elif isinstance(funcs, Callable):
            self.content_funcs.append(funcs)
        else:
            raise TypeError("Only can add Callable elements as a list or independent callable value.")

    @st.fragment
    def render(self):
        """
        Renders the button and floating panel. This is the main function to call.
        """
        button_container = st.container()
        with button_container:
            st.button(self.button_icon,
                      key=f"toggle_button_{self.key}",
                      help=self.button_tooltip,
                      on_click=self._toggle_state)
        button_container.float(self.css_button)

        if st.session_state[self.state_key]:
            panel_container = st.container()
            with panel_container:
                for func in self.content_funcs:
                    func()

            panel_container.float(self.css_panel)