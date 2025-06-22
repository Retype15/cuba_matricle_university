from libraries.streamlit_extended import HierarchicalSidebarNavigation
from libraries.st_options import *
from libraries.general_functions import translation, chat_button
from streamlit_js_eval import get_user_agent, get_browser_language

st.set_page_config(layout="wide", page_title="Cuban University Enrollment Analysis", page_icon="🎓")
chat_button()
df_main = cargar_datos_matricula('data/db.parquet') 
df_ins = cargar_datos_instituciones('data/db_uni.parquet')

idiomas = { "Español": "es", "English": "en", "Français": "fr", "Português": "pt", "Deutsch": "de"}
idiomas_index = {"es":0, "en":1, "fr":2, "pt":3, "de":4}
st.session_state.setdefault("lang_sel", 'en')
lang_selected = st.sidebar.selectbox("Select your language:", list(idiomas.keys()), index=idiomas_index.get(get_browser_language(),0), help=translation('lang_select_help', "Select your preferred language for the application."))
if idiomas[lang_selected] != st.session_state.get("lang_sel", None):
    st.session_state["lang_sel"] = idiomas[lang_selected]
    st.rerun(scope='app')

if df_main.empty:
    st.error(translation('load_df_error', "Error crítico: No se pudieron cargar los datos ('db.parquet'). La aplicación no puede continuar."))
else:
    st.title(translation('load_screen_title',"🎓 Análisis Estratégico de la Matrícula Universitaria en Cuba"))
    st.image("images/UH.jpg", caption=translation('main_image_caption',"Universidad de La Habana. Un símbolo de la educación superior en Cuba."), use_container_width=True)
    st.markdown(translation('main_markdown_1',"Un viaje para iluminar el camino de la Educación Superior."))
    st.markdown("---")

    navigation_structure = {
        "Introduccion": None,
        "1. Pulso Nacional": None,
        "2. Mosaico de Saberes": None,
        "3. Carreras Bajo la Lupa": None,
        "4. Perspectiva de Género": None, 
        "5. Universidades: Fortalezas y Focos": None,
        "6. Mirando al Mañana (Proyecciones)": None, 
        "Playground!": ["Perfil Detallado de Carrera", "Guía de Instituciones"],
        "7. Áreas de Atención": None,
        "Conclusiones Finales": None
    }

    SECTION_MAP = {
        "Introduccion": introduction,
        "1. Pulso Nacional": A1,
        "2. Mosaico de Saberes": A2,
        "3. Carreras Bajo la Lupa": A3,
        "4. Perspectiva de Género": A4,
        "5. Universidades: Fortalezas y Focos": A5,
        "6. Mirando al Mañana (Proyecciones)": A6,
        "7. Áreas de Atención": A7,
        "Conclusiones Finales": conclusion
    }
    PLAYGROUND_MAP = {
        "Perfil Detallado de Carrera": B1,
        "Guía de Instituciones": B2
    }

#SI lees esto, revisa que esté activo el wraper en general_functions._load_translations()
    
    nav: HierarchicalSidebarNavigation = HierarchicalSidebarNavigation(navigation_structure)
###-----------------------------------------------------------------------------------
    
    

###----------------------------------------------------------------------------------------

    st.sidebar.title(translation('sidebar_title',"🧭 Explorador de secciones"))
    nav.display_sidebar_navigation(radio_title_main=translation('sidebar_radio_title_main',"Elige una sección:"), radio_title_sub_prefix=translation('sidebar_radio_title_sub_prefix',"Subseccion: "))
    seccion_actual, active_sub = nav.get_active_selection()

    st.sidebar.markdown("---")
    st.sidebar.info(translation(
        'sidebar_info',
        """Análisis basado en datos de matrícula del período 2015-16 a 2024-25.\n\n -- ⚠️ No incluye el curso 2018-2019 por falta de datos en dicho curso, los análisis se realizan obviando este curso."""))
    if seccion_actual in SECTION_MAP:
        SECTION_MAP[seccion_actual](df_main)
    elif seccion_actual == "Playground!":
        if active_sub in PLAYGROUND_MAP:
            kwargs = {"df_main": df_main,"df_ins": df_ins}
            PLAYGROUND_MAP[active_sub](**kwargs)
        else:
            st.error(translation('subseccion_not_valid_in',"Subsección no válida en ")+"Playground!")

    nav.create_navigation_buttons(prev_text=translation('back',"Anterior: "), next_text=translation('next',"Siguiente: "))

st.sidebar.markdown("---")
st.sidebar.markdown(f"{translation('authors',"Autores:")}\n- Reynier Ramos González\n- Ernesto Herrera García")