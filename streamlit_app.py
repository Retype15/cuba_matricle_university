from re import S
from libraries.streamlit_extended import HierarchicalSidebarNavigation
from libraries.st_options import *
from libraries.general_functions import translation, _load_translations

st.set_page_config(layout="wide", page_title=translation('config_page_title', 'en'), page_icon="🎓")

df_main = cargar_datos_matricula('data/db.parquet') 
df_ins = cargar_datos_instituciones('data/db_uni.parquet')

idiomas = {"English": "en", "Español": "es"}
st.session_state.setdefault("lang_sel", "en")
lang_selected = st.sidebar.selectbox("Select your language:", list(idiomas.keys()))
if idiomas[lang_selected] != st.session_state.get("lang_sel", None):
    st.session_state["lang_sel"] = idiomas[lang_selected]
    st.rerun(scope='app')

if df_main.empty:
    st.error(translation('load_df_error'))
else:
    st.title(translation('load_screen_title'))
    st.image("images/UH.jpg", caption=translation('main_image_caption'), use_container_width=True)
    st.markdown(translation('main_markdown_1'))
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
    
    nav: HierarchicalSidebarNavigation = HierarchicalSidebarNavigation(navigation_structure)

    st.sidebar.title(translation('sidebar_title'))
    nav.display_sidebar_navigation(radio_title_main=translation('sidebar_radio_title_main'), radio_title_sub_prefix=translation('sidebar_radio_title_sub_prefix'))
    seccion_actual, active_sub = nav.get_active_selection()

    st.sidebar.markdown("---")
    st.sidebar.info(translation('sidebar_info'))

    if seccion_actual in SECTION_MAP:
        SECTION_MAP[seccion_actual](df_main)
    elif seccion_actual == "Playground!":
        if active_sub in PLAYGROUND_MAP:
            kwargs = {"df_main": df_main,"df_ins": df_ins}
            PLAYGROUND_MAP[active_sub](**kwargs)
        else:
            st.error(translation('subseccion_not_valid_in')+"Playground!")

    nav.create_navigation_buttons(prev_text=translation('back: '), next_text=translation('next: '))

st.sidebar.markdown("---")
st.sidebar.markdown(f"{translation('authors:')}\n- Reynier Ramos González\n- Ernesto Herrera García")