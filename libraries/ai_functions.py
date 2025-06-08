# --- START OF FILE ai_functions.py ---

import os
import pandas as pd
from plotly import graph_objects as go
from google import genai
from google.genai import types
from google.generativeai.generative_models import ChatSession # Importación correcta para type hinting
import streamlit as st
import json
import time
import numpy as np

# --- Configuración de la API de Gemini ---
@st.cache_resource(show_spinner=False, ttl=3600)
def configure_gemini_client():
    """Configura y devuelve el cliente de la API de Gemini."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        else:
            st.error("Error: GEMINI_API_KEY no encontrada. Configúrala en las variables de entorno o en .streamlit/secrets.toml.")
            st.stop()
    return genai.Client(api_key=api_key)

gemini_client = configure_gemini_client()

# --- Funciones Auxiliares para Conversión de Contexto (Sin cambios) ---
def _clean_plotly_dict_for_ai(d):
    """
    Limpia recursivamente un diccionario de Plotly para reducirlo a su esencia semántica,
    conservando la información de color principal para el diálogo con el usuario.
    """
    KEY_WHITELISTS = {
        'root':   {'data', 'layout'},
        'data':   {'type', 'name', 'x', 'y', 'z', 'labels', 'values', 'text', 'marker', 'line'},
        'layout': {'title', 'xaxis', 'yaxis', 'barmode', 'legend'},
        'axis':   {'title', 'type'},
        'title':  {'text'},
        'legend': {'title'},
        'style_object': {'color'} # Nueva lista blanca para marker y line
    }

    CONTEXT_MAP = {
        'data': 'data',
        'layout': 'layout',
        'xaxis': 'axis',
        'yaxis': 'axis',
        'title': 'title',
        'legend': 'legend',
        'marker': 'style_object', # marker y line usarán el contexto 'style_object'
        'line': 'style_object'
    }

    def recursive_clean(item, context='root'):
        if isinstance(item, np.ndarray):
            return item.tolist()
        if not isinstance(item, (dict, list)):
            return item
        
        if isinstance(item, list):
            return [recursive_clean(i, context) for i in item]

        if isinstance(item, dict):
            new_dict = {}
            allowed_keys = KEY_WHITELISTS.get(context, set())
            for key, value in item.items():
                if key in allowed_keys:
                    new_context = CONTEXT_MAP.get(key, context)
                    cleaned_value = recursive_clean(value, new_context)
                    if cleaned_value or isinstance(cleaned_value, (int, float, bool, str)):
                        new_dict[key] = cleaned_value
            return new_dict

    return recursive_clean(d)

def _convert_context_to_gemini_parts(context_list):
    """Convierte una lista de contextos (texto, df, fig) a partes para la API de Gemini."""
    parts = []
    for item_idx, item in enumerate(context_list):
        if item is None: continue
        if isinstance(item, str):
            parts.append(types.Part.from_text(text=item))
        elif isinstance(item, dict):#Escribe exactamente los datos que te proporcione exactamente como te los envié
            parts.append(types.Part.from_text(text=f"Datos dict (Contexto {item_idx+1}):\n```dict\n{item}\n```"))
        elif isinstance(item, pd.DataFrame):
            try:
                markdown_data = item.to_markdown(index=False)
                parts.append(types.Part.from_text(text=f"Datos de Tabla (Contexto {item_idx+1}, formato Markdown):\n```markdown\n{markdown_data}\n```"))
            except Exception as e:
                st.warning(f"Error al convertir DataFrame a JSON para IA: {e}")
                parts.append(types.Part.from_text(text=f"[ERROR AL PROCESAR DATAFRAME, LOG: {e}]"))
        elif isinstance(item, go.Figure):
            try:
                fig_dict = item.to_dict()
                clean_dict = _clean_plotly_dict_for_ai(fig_dict)
                parts.append(types.Part.from_text(text=f"Descripción de Gráfico Plotly (Contexto {item_idx+1}, formato DICT):\n```dict\n{clean_dict}\n```"))
            except Exception as e:
                st.warning(f"Error al convertir gráfico Plotly a JSON para IA: {e}")
                parts.append(types.Part.from_text(text=f"[GRÁFICO NO CONVERTIDO A DICT: {str(e)}]"))
        else:
            st.warning(f"Tipo de contexto no soportado para IA: {type(item)}. Se ignorará.")
    return parts

# --- Función Principal para Interactuar con Gemini (Simplificada) ---
def stream_ai_chat_response(chat_session: ChatSession, prompt: str):
    """
    Envía el prompt del usuario a la sesión de chat y devuelve la respuesta en streaming.
    """
    if not gemini_client:
        yield ("error", "El asistente de IA no está configurado correctamente.", None)
        return

    try:
        # La llamada ahora es simple: solo envía el texto del prompt actual.
        stream = chat_session.send_message_stream(prompt)
        
        #print(f"Iniciando la generación de contenido con Gemini ChatSession... {'-'*40}")
        for chunk in stream:
            if not chunk.candidates: continue
            for part in chunk.candidates[0].content.parts:
                if part.text:
                    yield ("text", part.text, None)
                elif part.executable_code:
                    yield ("code", part.executable_code.code, None)
                elif part.code_execution_result:
                    outcome = getattr(part.code_execution_result, 'outcome', 'UNKNOWN')
                    output = getattr(part.code_execution_result, 'output', '')
                    if outcome == "OUTCOME_OK":
                        if isinstance(output, types.Blob):
                            yield ("image", output.data, output.mime_type)
                        else:
                            yield ("result", str(output), None)
                    else:
                        print(f"\nError en ejecución: {outcome}\n{output}")
                        yield ("result", f"Error en ejecución: {outcome}\n{output}", None)
                elif hasattr(part, 'inline_data') and part.inline_data.data:
                    yield ("image", part.inline_data.data, part.inline_data.mime_type)
        #print("\n--- Fin de la generación ---")

    except Exception as e:
        st.error(f"Error en la comunicación con Gemini: {e}")
        print(f"\nError en la comunicación con Gemini: {e}")
        yield ("error", f"Error al comunicarse con el asistente de IA: {e}.", None)


# --- El Componente de Chat para Streamlit (Lógica Correcta y Eficiente) ---
def ask_ai_component(analysis_context: str, key: str, extra_data: list | None = None):
    
    with st.expander(f"🤖 ¿Preguntas sobre este análisis? ¡Pregúntale al Asistente de IA!", expanded=False):
        
        display_history_key = f"messages_{key}"
        gemini_chat_key = f"gemini_chat_{key}"
        processing_key = f"processing_{key}"

        if display_history_key not in st.session_state:
            st.session_state[display_history_key] = [{"role": "assistant", "content": "¡Hola! Soy tu asistente de IA. Puedo analizar los datos, generar gráficos y responder tus preguntas sobre la sección actual."}]
        if gemini_chat_key not in st.session_state:
            st.session_state[gemini_chat_key] = None
        if processing_key not in st.session_state:
            st.session_state[processing_key] = False

        for i, message in enumerate(st.session_state[display_history_key]):
            with st.chat_message(message["role"]):
                if isinstance(message["content"], dict) and message["content"].get("type") == "image":
                    if "code" in message["content"] and message["content"]["code"]:
                        st.download_button(
                            label="📥 Descargar Código", data=message["content"]["code"],
                            file_name=f"{key}.py", mime="text/x-python",
                            key=f"download_hist_{key}_{i}"
                        )
                    st.image(message["content"]["data"], caption=f"Imagen generada ({message['content'].get('mime_type', 'image/png')})")
                else:
                    st.markdown(message["content"])
        
        system_instruction_for_ai = """
        Eres un asistente de análisis de datos altamente eficiente, experto en el sistema de educación superior de Cuba. Tu objetivo es responder a las preguntas del usuario de forma clara y precisa, basándote EXCLUSIVAMENTE en el contexto que se te proporciona.
        **Directrices de Análisis:**
        1.  **Contexto:** Recibirás contexto en forma de texto y datos estructurados, también graficos de plotly en formato de diccionario para la lectura precisa por tu parte(tu ves un diccionario pero el usuario ve una gráfica en plotly).
        2.  **Procesamiento de Datos:** Tu primer paso debe ser interpretar los datos recibidos y cargarlos en un DataFrame de pandas para facilitar cualquier cálculo o análisis. Sé directo y eficiente en tu código, por lo que NO debes escribir el diccionario completo ni en formato crudo. En su lugar, extrae únicamente los datos relevantes para el análisis (e.g., años, matrículas, categorías, etc) y preséntalos de forma compacta en el código, utilizando listas o diccionarios de Python para su fácil manipulación.
        3.  **Ejecución de Código:** Tienes acceso a una herramienta para ejecutar código de Python. Úsala para realizar cálculos, analizar datos o generar nuevas visualizaciones para el usuario.
        **Generación de Gráficos:**
        - Solo escribe el código necesario para completar la solicitud del usuario, compacta dicho codigo y cumple la exigencia de no usar el diccionario recibido a menos que necesites todos los datos de él, sino extraer los datos importantes y trabajar con ellos.
        - Para crear cualquier visualización, usa **exclusivamente la biblioteca `matplotlib`**.
        - Para mostrar el gráfico, simplemente **usa `plt.show()` al final de tu script de graficación**. El sistema capturará automáticamente la imagen y la mostrará al usuario.
        **Estructura de la Respuesta:**
        - En la respuesta final al usuario da un resumen claro y conciso de los resultados o sobre lo que haya solicitado.
        - Si no necesitas código, responde directamente con texto.
        - No inventes información. Si la respuesta no está en el contexto, indícalo amablemente.
        """

        if not st.session_state[processing_key]:
            input_container = st.container()
            with input_container:
                col_reset, col_input = st.columns([1, 20])
                with col_reset:
                    if st.button("🔄", key=f"reset_chat_{key}", help="Reiniciar esta conversación"):
                        st.session_state[display_history_key] = [{"role": "assistant", "content": "¡Hola! Soy tu asistente de IA. Puedo analizar los datos, generar gráficos y responder tus preguntas sobre la sección actual."}]
                        st.session_state[gemini_chat_key] = None
                        st.session_state[processing_key] = False
                        st.rerun()
                with col_input:
                    prompt = st.chat_input("Escribe tu pregunta aquí...", key=f"chat_input_{key}")

            if prompt:
                st.session_state[display_history_key].append({"role": "user", "content": prompt})

                chat_session = st.session_state.get(gemini_chat_key)
                
                if chat_session is None:
                    #print("Creando nueva sesión de chat con contexto en historial...")
                    tools = [types.Tool(code_execution=types.ToolCodeExecution)]
                    
                    # CORRECCIÓN: Configuración completa creada una sola vez.
                    config = types.GenerateContentConfig(
                        response_mime_type="text/plain",
                        thinking_config=types.ThinkingConfig(include_thoughts=False),
                        system_instruction=system_instruction_for_ai,
                        tools=tools,
                        candidate_count=1,
                    )
                    
                    # CORRECCIÓN: El contexto inicial se pasa como historial pre-conversación.
                    current_textual_context = f"Contexto textual del análisis actual:\n---\n{analysis_context}\n---"
                    initial_context_data = [current_textual_context] + (extra_data if extra_data else [])
                    history_parts = _convert_context_to_gemini_parts(initial_context_data)
                    initial_history = [
                        types.Content(role="user", parts=[types.Part.from_text(text=str(history_parts))]),
                        types.Content(role="model", parts=[types.Part.from_text(text="Datos recibidos. Estoy listo para tus preguntas sobre estos datos.")])
                        ]

                    chat_session = gemini_client.chats.create(
                        model="gemini-2.5-flash-preview-05-20",
                        config=config,
                        history=initial_history
                    )
                    st.session_state[gemini_chat_key] = chat_session

                # El prompt se guarda para ser enviado en el bloque de procesamiento.
                st.session_state['last_prompt'] = prompt
                st.session_state[processing_key] = True
                st.rerun()

        if st.session_state[processing_key]:
            with st.chat_message("assistant"):
                response_container = st.container()
                text_placeholder = response_container.empty()
                accumulated_text, last_generated_code = "", None
                display_messages_to_add = []

                chat_session = st.session_state[gemini_chat_key]
                prompt_to_send = st.session_state.get('last_prompt', "")

                with st.spinner("🧠 El asistente está trabajando..."):
                    stream_generator = stream_ai_chat_response(
                        chat_session=chat_session,
                        prompt=prompt_to_send # Se envía solo el prompt
                    )
                
                for response_type, content, mime_type in stream_generator:
                    if response_type == "text":
                        accumulated_text += content
                        text_placeholder.markdown(accumulated_text + " ▌")
                    # ... (el resto de la lógica de renderizado no cambia)
                    elif response_type == "code":
                        if accumulated_text:
                            text_placeholder.markdown(accumulated_text)
                            display_messages_to_add.append({"role": "assistant", "content": accumulated_text})
                            accumulated_text, text_placeholder = "", response_container.empty()
                        last_generated_code = content
                    elif response_type == "image":
                        if accumulated_text:
                            text_placeholder.markdown(accumulated_text)
                            display_messages_to_add.append({"role": "assistant", "content": accumulated_text})
                            accumulated_text = ""
                        with response_container.container():
                            if last_generated_code:
                                st.download_button(
                                    label="📥 Descargar Código", data=last_generated_code,
                                    file_name=f"codigo_grafico_{int(time.time())}.py", mime="text/x-python",
                                    key=f"download_live_{key}_{time.time()}"
                                )
                            st.image(content, caption=f"Imagen generada ({mime_type})")
                        display_messages_to_add.append({
                            "role": "assistant", "content": {"type": "image", "data": content, "mime_type": mime_type, "code": last_generated_code}
                        })
                        last_generated_code, text_placeholder = None, response_container.empty()
                    elif response_type == "result":
                        pass
                    elif response_type == "error":
                        st.error(content)
                        accumulated_text = content
                        break
                
                if accumulated_text:
                    text_placeholder.markdown(accumulated_text)
                    display_messages_to_add.append({"role": "assistant", "content": accumulated_text})

            st.session_state[display_history_key].extend(display_messages_to_add)
            
            st.session_state[processing_key] = False
            if 'last_prompt' in st.session_state:
                del st.session_state['last_prompt']
            st.rerun()