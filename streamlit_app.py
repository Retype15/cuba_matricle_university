from libraries.streamlit_extended import HierarchicalSidebarNavigation
from libraries.st_options import *

import streamlit.components.v1 as components

# --- Configuración de la Página de Streamlit ---
st.set_page_config(layout="wide", page_title="Análisis Matrícula Universitaria Cuba", page_icon="🎓")

df_main = cargar_datos_matricula('data/db.parquet') 
df_ins = cargar_datos_instituciones('data/db_uni.parquet')

if df_main.empty:
    st.error("Error crítico: No se pudieron cargar los datos ('db_long.csv'). La aplicación no puede continuar.")
else:
    st.title("🎓 Análisis Estratégico de la Matrícula Universitaria en Cuba")
    st.image("images/UH.jpg", caption="Universidad de La Habana. Un símbolo de la educación superior en Cuba.", use_container_width=True)
    st.markdown("Un viaje a través de los datos (2015-2025) para iluminar el camino de la Educación Superior.")
    st.markdown("---")

    # --- Navegación ---    
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

    st.sidebar.title("🧭 Explorador de secciones")
    nav.display_sidebar_navigation(radio_title_main="Elige una sección:", radio_title_sub_prefix="Subseccion: ")
    seccion_actual, active_sub = nav.get_active_selection()

    st.sidebar.markdown("---")
    st.sidebar.info("Análisis basado en datos de matrícula del período 2015-16 a 2024-25.\n\n -- ⚠️ No incluye el curso 2018-2019 por falta de datos en dicho curso, los análisis se realizan obviando este curso.")

    # --- Contenido por Sección ---
    if seccion_actual in SECTION_MAP:
        SECTION_MAP[seccion_actual](df_main)
    elif seccion_actual == "Playground!":
        if active_sub in PLAYGROUND_MAP:
            kwargs = {"df": df_main,"df_ins": df_ins}
            PLAYGROUND_MAP[active_sub](**kwargs)
        else:
            st.error("Subsección no válida en Playground!")

    nav.create_navigation_buttons(prev_text='Anterior: ', next_text='Siguiente: ')

st.sidebar.markdown("---")
st.sidebar.markdown("Autores:\n- Reynier Ramos González\n- Ernesto")