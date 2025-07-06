from typing import Any
from libraries.streamlit_extended import HierarchicalSidebarNavigation
from libraries.st_options import *
from libraries.general_functions import translation, Translator, FloatingPanel
from libraries.Gamification import GameController

st.set_page_config(layout="wide", page_title="Cuban University Enrollment Analysis", page_icon="🎓")

df_main = cargar_datos_matricula('data/db.parquet') 
df_ins = cargar_datos_instituciones('data/db_uni.parquet')

#st.map(df_ins, latitude='utm_x', longitude='utm_y')
#st.pydeck_chart()
languages = { "Español": "es", "English": "en", "Français": "fr", "Italiano": 'it', "Português": "pt", "Deutsch": "de", "Русский": 'ru', "中文":'zh', "日本語": 'ja'}


#Ernesto si lees esto, revisa que esté activo el wraper en libraries.general_functions._get_language_dict(...)

ts:Translator = Translator(languages, 'lang') 

game_controller:GameController = GameController(translation=ts.translate('gamification_controller', {}))


@st.dialog(ts.translate('settings_title', "Configuración") + ":", width='large')
def settings():
    ts.render_selector(auto_rerun=False)
    if st.button(ts.translate('save', "Guardar"), type="primary", icon="💾"):
        st.rerun(scope='app')
    

if st.sidebar.button(ts.translate('settings_title', "Configuraciones"), icon='⚙️', use_container_width=True):
    settings()

if df_main.empty:
    st.error(ts.translate('load_df_error', "Error crítico: No se pudieron cargar los datos ('db.parquet'). La aplicación no puede continuar."))
else:
    st.title(ts.translate('load_screen_title',"🎓 Análisis Estratégico de la Matrícula Universitaria en Cuba"))
    st.image("images/UH.jpg", caption=ts.translate('main_image_caption',"Universidad de La Habana. Un símbolo de la educación superior en Cuba."), use_container_width=True)
    st.markdown(ts.translate('main_markdown_1',"Un viaje para iluminar el camino de la Educación Superior."))
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
    seccion_actual, active_sub = nav.get_active_selection()

    panel_progreso = None
    
    if not seccion_actual == "Introduccion" or ('initial_mode_selected' in st.session_state and st.session_state.initial_mode_selected):
        with st.sidebar:                           #TODO:deprecated
            game_controller.display_mode_toggle()  #TODO:deprecated
        panel_progreso = FloatingPanel(
            key="progreso_player",
            content_funcs=[game_controller.display_score_panel],
            button_icon="🏆",
            button_tooltip="Ver mi progreso"
        )
        #if game_controller.game_mode: chat_button(game_controller.display_score_panel) #TODO:deprecated
            #game_controller.display_mode_toggle()                                      #TODO:deprecated

    st.sidebar.title(ts.translate('sidebar_title',"🧭 Explorador de secciones"))
    nav.display_sidebar_navigation(radio_title_main=ts.translate('sidebar_radio_title_main',"Elige una sección:"), radio_title_sub_prefix=ts.translate('sidebar_radio_title_sub_prefix',"Subseccion: "))
       

    st.sidebar.markdown("---")
    st.sidebar.info(
        ts.translate(
        'sidebar_info',
        """Análisis basado en datos de matrícula del período 2015-16 a 2024-25.\n\n -- ⚠️ No incluye el curso 2018-2019 por falta de datos en dicho curso, los análisis se realizan obviando este curso."""
        )
    )
    _kwargs = {
        "df_main": df_main,
        "df_ins": df_ins, 
        "game_controller": game_controller,
        "panel_progreso": panel_progreso,
        "ts": ts
    }
    if seccion_actual in SECTION_MAP:
        SECTION_MAP[seccion_actual](**_kwargs)
    elif seccion_actual == "Playground!":
        if active_sub in PLAYGROUND_MAP:
            
            PLAYGROUND_MAP[active_sub](**_kwargs)
        else:
            st.error(ts.translate('subseccion_not_valid_in',"Subsección no válida en ")+"Playground!")
    
    if not seccion_actual == "Introduccion" or ('initial_mode_selected' in st.session_state and st.session_state.initial_mode_selected):
        nav.create_navigation_buttons(prev_text=ts.translate('back',"Anterior: "), next_text=ts.translate('next',"Siguiente: "))
    
    #game_controller.confirm_deactivation_dialog() #TODO:deprecated

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"{ts.translate('authors',"Autores:")}"
        f"\n- {ts.translate('author_reynier', "Reynier Ramos González")}"
        f"\n- {ts.translate('author_ernesto', "Ernesto Herrera García")}"
    )
    with st.sidebar: 
        if panel_progreso: panel_progreso.render()