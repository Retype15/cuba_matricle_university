import base64
import os
import io
import pandas as pd
from google import genai
from google.genai import types
import plotly.graph_objects as go
import streamlit as st
import json
import time
import numpy as np

# --- Configuración de la API de Gemini ---
@st.cache_resource(show_spinner=False, ttl=3600)
def configure_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        else:
            st.error("Error: GEMINI_API_KEY no encontrada. Configúrala en las variables de entorno o en .streamlit/secrets.toml.")
            return None
    return genai.Client(api_key=api_key)

gemini_client = configure_gemini_client()

# --- Funciones Auxiliares para Conversión de Contexto ---
def _clean_fig_dict_for_json(d):
    """Convierte ndarrays a listas para serialización JSON."""
    if isinstance(d, dict):
        return {k: _clean_fig_dict_for_json(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [_clean_fig_dict_for_json(v) for v in d]
    elif isinstance(d, np.ndarray):
        return d.tolist()
    else:
        return d

def _convert_context_to_gemini_parts(context_list):
    parts = []
    for item_idx, item in enumerate(context_list):
        if item is None: continue
        if isinstance(item, str):
            parts.append(types.Part.from_text(text=item))
        elif isinstance(item, pd.DataFrame):
            try:
                json_data = item.to_json(orient="records", indent=2)
                parts.append(types.Part.from_text(text=f"Datos de Tabla (Contexto {item_idx+1}, formato JSON):\n```json\n{json_data}\n```"))
            except Exception as e:
                st.warning(f"Error al convertir DataFrame a JSON para IA: {e}")
                parts.append(types.Part.from_text(text="[ERROR AL PROCESAR DATAFRAME]"))
        elif isinstance(item, go.Figure):
            try:
                fig_dict = item.to_dict()
                clean_dict = _clean_fig_dict_for_json(fig_dict)
                fig_json = json.dumps(clean_dict, indent=2)
                parts.append(types.Part.from_text(text=f"Descripción de Gráfico Plotly (Contexto {item_idx+1}, formato JSON):\n```json\n{fig_json}\n```"))
            except Exception as e:
                st.warning(f"Error al convertir gráfico Plotly a JSON para IA: {e}")
                parts.append(types.Part.from_text(text=f"[GRÁFICO NO CONVERTIDO A JSON: {str(e)}]"))
        else:
            st.warning(f"Tipo de contexto no soportado para IA: {type(item)}. Se ignorará.")
    return parts

# --- Función Principal para Interactuar con Gemini ---
def generate_ai_response_stream(user_message, conversation_history_for_gemini, system_instruction_text, context_list_for_first_turn=None):
    if not gemini_client:
        yield ("error", "El asistente de IA no está configurado correctamente.")
        return

    current_user_content_parts = [types.Part.from_text(text=user_message)]
    if context_list_for_first_turn:
        context_parts_ready = _convert_context_to_gemini_parts(context_list_for_first_turn)
        current_user_content_parts = context_parts_ready + current_user_content_parts
        
    final_contents_for_gemini = conversation_history_for_gemini + [types.Content(role="user", parts=current_user_content_parts)]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        tools=[types.Tool(code_execution=types.ToolCodeExecution)],
        system_instruction=[types.Part.from_text(text=system_instruction_text)],
    )

    try:
        stream = gemini_client.models.generate_content_stream(
            model="gemini-2.5-flash-preview-05-20",
            contents=final_contents_for_gemini,
            config=generate_content_config,
        )
        for chunk in stream:
            if not chunk.candidates: continue
            for part in chunk.candidates[0].content.parts:
                if part.text:
                    yield ("text", part.text)
                elif part.executable_code:
                    yield ("code", part.executable_code.code)
                elif part.code_execution_result:
                    if hasattr(part.code_execution_result, 'outcome') and part.code_execution_result.outcome == "OUTCOME_OK":
                        if hasattr(part.code_execution_result, 'output') and isinstance(part.code_execution_result.output, types.Blob):
                             yield ("image", part.code_execution_result.output.data, part.code_execution_result.output.mime_type)
                        else:
                             yield ("result", str(part.code_execution_result.output))
                    else:
                         yield ("result", f"Error en ejecución: {str(part.code_execution_result.outcome)}")
                elif hasattr(part, 'inline_data') and part.inline_data.data:
                    yield ("image", part.inline_data.data, part.inline_data.mime_type)
    except Exception as e:
        st.error(f"Error en la comunicación con Gemini: {e}")
        yield ("error", f"Error al comunicarse con el asistente de IA: {e}.")

# --- El Componente de Chat para Streamlit (con Botón de Reinicio Integrado) ---
def ask_ai_component(analysis_context, key, extra_data=None):
    
    with st.expander(f"🤖 ¿Preguntas sobre este análisis? ¡Pregúntale al Asistente de IA!", expanded=False):
        
        history_key = f"messages_{key}"
        gemini_history_key = f"gemini_messages_{key}"

        # Inicialización de historiales si no existen
        if history_key not in st.session_state:
            st.session_state[history_key] = [{"role": "assistant", "content": "¡Hola! Estoy listo para responder tus preguntas sobre el análisis que estás viendo."}]
        if gemini_history_key not in st.session_state:
            st.session_state[gemini_history_key] = []

        # Mostrar historial del chat
        for message in st.session_state[history_key]:
            with st.chat_message(message["role"]):
                # Solo mostrar texto o imágenes en el historial. El código/resultado se ignora.
                if isinstance(message["content"], dict):
                    if message["content"]["type"] == "image":
                        mime_type = message["content"].get("mime_type", "image/png")
                        st.image(message["content"]["data"], caption=f"Imagen generada ({mime_type})")
                else: # Es un string de texto simple
                    st.markdown(message["content"])

        # System Prompt (se mantiene igual, aunque no mostremos el código, la IA aún lo usa)
        system_instruction_for_ai = """
        Eres un asistente de análisis de datos altamente eficiente, experto en el sistema de educación superior de Cuba. Tu objetivo es responder a las preguntas del usuario de forma clara y precisa, basándote EXCLUSIVAMENTE en el contexto que se te proporciona.

        **Directrices de Análisis:**
        1.  **Contexto:** Recibirás contexto en forma de texto y datos estructurados en formato JSON (para tablas y gráficos).
        2.  **Procesamiento de Datos:** Tu primer paso debe ser interpretar los datos JSON y cargarlos en un DataFrame de pandas para facilitar cualquier cálculo o análisis. Sé directo y eficiente en tu código, por lo que no escribas el json, sino los datos más importantes de forma compacta, usando listas o diccionarios.
        3.  **Ejecución de Código:** Tienes acceso a una herramienta para ejecutar código de Python. Úsala para realizar cálculos, analizar datos o generar nuevas visualizaciones.

        **Generación de Gráficos:**
        - Para crear cualquier visualización, usa **exclusivamente la biblioteca `matplotlib.pyplot`**.
        - Para mostrar el gráfico, simplemente **usa `plt.show()` al final de tu script de graficación**. El sistema capturará automáticamente la imagen y la mostrará al usuario.

        **Estructura de la Respuesta:**
        - Ejecuta el código necesario para responder, pero en tu respuesta final al usuario da un resumen claro y conciso de los resultados.
        - Si no necesitas código, responde directamente con texto.
        - No inventes información. Si la respuesta no está en el contexto, indícalo amablemente.
        """
        
        current_textual_context = f"Contexto textual del análisis actual:\n---\n{analysis_context}\n---"
        
        # --- Contenedor para el Input y el Botón de Reinicio ---
        input_container = st.container()
        with input_container:
            col_reset, col_input = st.columns([1, 20]) # Proporción para un botón pequeño y un input grande

            with col_reset:
                # El botón necesita un poco de espacio superior para alinearse visualmente con el chat_input
                #st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True) 
                if st.button("🔄", key=f"reset_chat_{key}", help="Reiniciar esta conversación"):
                    st.session_state[history_key] = []
                    st.session_state[gemini_history_key] = []
                    st.rerun()

            with col_input:
                prompt = st.chat_input("Escribe tu pregunta aquí...", key=f"chat_input_{key}")

        if prompt:
            st.session_state[history_key].append({"role": "user", "content": prompt})
            
            ai_context_to_send = [current_textual_context]
            if not st.session_state[gemini_history_key] and extra_data:
                ai_context_to_send.extend(extra_data)
            
            with st.chat_message("assistant"):
                with st.spinner("🧠 El asistente está trabajando en tu respuesta..."):
                    response_container = st.container()
                    full_text_response = ""

                    for response_type, content, *extra_info in generate_ai_response_stream(
                        user_message=prompt, 
                        conversation_history_for_gemini=st.session_state[gemini_history_key],
                        system_instruction_text=system_instruction_for_ai, 
                        context_list_for_first_turn=ai_context_to_send
                    ):
                        # SOLO RENDERIZAR IMÁGENES Y ACUMULAR TEXTO
                        if response_type == "image":
                            mime_type = extra_info[0] if extra_info else "image/png"
                            response_container.image(content, caption=f"Imagen generada ({mime_type})")
                            # Guardar la imagen en el historial de visualización
                            st.session_state[history_key].append({"role": "assistant", "content": {"type": "image", "data": content, "mime_type": mime_type}})
                        
                        elif response_type == "text":
                            full_text_response += content
                        
                        elif response_type == "error":
                            st.error(content)
                            full_text_response = content
                        
                        # Ignorar "code" y "result" para la visualización

                # Mostrar el texto final acumulado
                if full_text_response:
                    response_container.markdown(full_text_response)
            
            # Guardar la respuesta final en el historial de visualización
            if full_text_response:
                st.session_state[history_key].append({"role": "assistant", "content": full_text_response})
            
            # Actualizar el historial técnico para Gemini
            user_turn_parts = _convert_context_to_gemini_parts([prompt] + (ai_context_to_send if not st.session_state[gemini_history_key] else []))
            st.session_state[gemini_history_key].append(types.Content(role="user", parts=user_turn_parts))
            st.session_state[gemini_history_key].append(types.Content(role="model", parts=[types.Part.from_text(text=full_text_response)]))
            
            st.rerun()