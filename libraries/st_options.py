from .plot_functions import *
from .ai_functions import ask_ai_component
from .general_functions import to_csv_string


def show_info(msg):
    if msg: st.caption(f"ℹ️ {msg}")

def introduction(*args,**kwargs):
    st.header(translation('introduction_header'))
    st.markdown(translation('introduction_markdown_1'))
    st.success(translation('introduction_success'))

def A1(df_main,*args,**kwargs):
    st.header(translation('A1_header'))
    st.markdown(translation('A1_markdown_1'))

    with st.spinner(translation('A1_spinner_1')):
        fig_a1, msg_a1 = analisis_A1(df_main, incluir_proyeccion=False)

    if fig_a1:
        st.plotly_chart(fig_a1, use_container_width=True, key="fig_a1_pulso_nacional")
        if msg_a1:
            show_info(msg_a1)
        
        st.subheader(translation('A1_fig_1_subheader'))
        st.markdown(translation('A1_fig_1_markdown_1'))

        
        contexto = translation('A1_fig_1_context')
        if msg_a1:
            contexto += f"\n{translation('important_note_for_analysis')} {msg_a1}"

        datos_para_ia = [fig_a1]

        ask_ai_component(
            analysis_context=contexto,
            key="a1_nacional",
            extra_data=datos_para_ia
        )
    else:
        st.warning(msg_a1 if msg_a1 else translation('A1_fig_1_warn_1'))

def A2(df_main,*args,**kwargs):
    st.header(translation('A2_header'))
    st.markdown(translation('A2_markdown_1'))

    with st.spinner(translation('A2_spinner_1')):
        fig_a2_abs, fig_a2_pct, msg_a2 = analisis_A2(df_main, incluir_proyeccion=False)

    if fig_a2_abs:
        st.subheader(translation('A2_fig_a2_abs_subheader'))
        st.plotly_chart(fig_a2_abs, use_container_width=True, key="fig_a2_abs_mosaico")
        
        st.markdown(translation('A2_fig_a2_abs_markdown_1'))
        
        ask_ai_component(
            analysis_context=translation('A2_fig_a2_abs_context'),
            key="a2_mosaico_abs",
            extra_data=[fig_a2_abs]
        )
    else:
        st.warning(f"{translation('generic_warn_figs')} (A2).")

    if fig_a2_pct:
        st.subheader(translation('A2_fig_a2_pct_subheader'))
        st.plotly_chart(fig_a2_pct, use_container_width=True, key="fig_a2_pct_mosaico")
        st.markdown(translation('A2_fig_a2_pct_markdown_1'))
        
        ask_ai_component(
            analysis_context=translation('A2_fig_a2_pct_context'),
            key="a2_mosaico_pct",
            extra_data=[fig_a2_pct]
        )
    else:
        st.warning(f"{translation('generic_warn_figs')} (A2).")
    
    show_info(msg_a2)
    
    st.subheader(translation('A2_subheader_2'))
    st.markdown(translation('A2_markdown_2'))

    fig_corr_ramas, df_corr_ramas, msg_corr_ramas = analisis_A2_correlacion_crecimiento_ramas(df_main)

    if fig_corr_ramas:
        st.plotly_chart(fig_corr_ramas, use_container_width=True, key="fig_a2_corr_heatmap")
        
        with st.expander(translation('A2_fig_corr_expander'), expanded=True):
            st.markdown(translation('A2_fig_corr_markdown_1'))

        context_corr_ia = translation('A2_fig_corr_context')
        datos_corr_ia = []
        if df_corr_ramas is not None:
            datos_corr_ia.append(df_corr_ramas)
        if msg_corr_ramas:
            context_corr_ia += f"\n{translation('important_note_for_analysis')} {msg_corr_ramas}"
            
        ask_ai_component(
            analysis_context=context_corr_ia,
            key="a2_corr_ramas",
            extra_data=datos_corr_ia
        )
    else:
        st.warning(msg_corr_ramas if msg_corr_ramas else translation('A2_corr_warn_1'))

def A3(df_main,*args,**kwargs):
    st.header("🔍 Carreras Bajo la Lupa: Popularidad, Tendencias y Dinamismo")
    st.markdown("""
    Tras explorar las grandes ramas del saber, es momento de enfocar nuestra lente en las unidades
    fundamentales: las carreras universitarias. ¿Cuáles son las que capturan el mayor interés estudiantil?
    ¿Cómo ha sido su evolución individual? Y, muy importante, ¿cuáles muestran un crecimiento
    acelerado y cuáles parecen estar perdiendo impulso?
    """)

    st.subheader("🏆 El Podio de las Carreras: ¿Cuáles Lideran la Matrícula Actual?")
    st.markdown(f"""
    A la izquierda observamos el ranking de todas las carreras según su matrícula total en el curso más reciente
    ({df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1}). A la derecha, vemos la evolución histórica de la matrícula
    para las 10 carreras que actualmente se encuentran en la cima de este ranking.
    """)
    with st.spinner("Analizando el ranking y evolución de las carreras top..."):
        fig_a3_evolucion, df_ranking_completo_a3, msg_a3 = analisis_A3(df_main)

    col_ranking, col_evolucion_top = st.columns([1, 2])

    with col_ranking:
        if df_ranking_completo_a3 is not None and not df_ranking_completo_a3.empty:
            st.dataframe(df_ranking_completo_a3, height=500)
        else:
            st.info("No hay datos de ranking de carreras para mostrar.")

    with col_evolucion_top:
        if fig_a3_evolucion:
            st.plotly_chart(fig_a3_evolucion, use_container_width=True, key="fig_a3_lupa_evolucion")
        else:
            st.info("No se generó gráfico de evolución para las carreras top actuales.")

    show_info(msg_a3)

    st.markdown("""
    **Puntos Clave del Podio:**
    *   **Liderazgo Indiscutible:** **Medicina** se posiciona firmemente como la carrera con la mayor matrícula (35,889 estudiantes), una constante que ya habíamos vislumbrado al analizar las ramas del saber.
    *   **Fuerzas Significativas:** Le siguen **Cultura Física** (14,695) y **Educación Primaria** (12,867), demostrando una demanda considerable en estas áreas.
    *   **Top 5 Robusto:** **Enfermería** (9,999) y **Contabilidad y Finanzas** (9,883) completan el top 5, ambas con una matrícula muy cercana a los 10,000 estudiantes.
    *   **Evolución de las Líderes:** El gráfico de la derecha nos permite ver cómo estas carreras (y otras del top 10) han llegado a su posición actual. Observa cómo algunas han tenido un crecimiento más sostenido, mientras otras muestran picos y valles más pronunciados.
    """)

    contexto_podio_ia = "El análisis actual muestra el ranking de matrícula de carreras en el último año y la evolución histórica de las 10 carreras más populares. Los datos se proporcionan en una tabla de ranking y un gráfico de líneas."
    datos_podio_ia = []
    if df_ranking_completo_a3 is not None:
        datos_podio_ia.append(df_ranking_completo_a3)
    if fig_a3_evolucion:
        datos_podio_ia.append(fig_a3_evolucion)
    if msg_a3:
        contexto_podio_ia += f"\nNota del análisis: {msg_a3}"

    ask_ai_component(
        analysis_context=contexto_podio_ia,
        key="a3_carreras_top",
        extra_data=datos_podio_ia
    )
    st.markdown("---")

    st.subheader("🚀 El Ritmo del Cambio: ¿Qué Carreras Despegan o Aterrizan?")
    st.markdown("""
    La **Tasa de Crecimiento Anual Compuesto (CAGR)** nos ofrece una perspectiva del dinamismo.
    Calcula el crecimiento (o decrecimiento) porcentual promedio de la matrícula de una carrera cada año,
    considerando todo el período analizado (2015-2024). Un CAGR alto sugiere una expansión rápida.
    """)
    with st.spinner("Calculando el dinamismo de las carreras (CAGR)..."):
        fig_a6_top_cagr, fig_a6_bottom_cagr, msg_a6 = analisis_A6(df_main)

    col_cagr_top, col_cagr_bottom = st.columns(2)

    with col_cagr_top:
        if fig_a6_top_cagr:
            st.markdown("📈 **Top 15 Carreras con Mayor Crecimiento Promedio Anual**")
            st.plotly_chart(fig_a6_top_cagr, use_container_width=True, key="fig_a6_top_lupa_cagr")
            st.markdown("""
            Estas carreras han experimentado la expansión más notable en su matrícula promedio anual.
            *   **Sorprendente Despegue:** **Servicios Estomatológicos** lidera con un CAGR superior al 100%, lo que indica una duplicación (o más) de su matrícula promedio año tras año.
            *   **Ingenierías en Auge:** Varias ingenierías como **Artística**, **Procesos Agroindustriales** e **Informática** muestran un crecimiento muy saludable.
            *   **Educación con Impulso:** Ramas de la educación como **Preescolar**, **Agropecuaria** y **Primaria** también figuran con un CAGR positivo y significativo.
            """)
        else:
            st.info("No se pudo generar el gráfico de carreras con mayor CAGR.")

    with col_cagr_bottom:
        if fig_a6_bottom_cagr:
            st.markdown("📉 **Top 15 Carreras con Menor Crecimiento o Mayor Decrecimiento Promedio Anual**")
            st.plotly_chart(fig_a6_bottom_cagr, use_container_width=True, key="fig_a6_bottom_lupa_cagr")
            st.markdown("""
            En el otro extremo, estas carreras han visto su matrícula promedio anual disminuir o crecer a un ritmo mucho menor.
            *   **Ajustes Notables:** **Estudios Socioculturales** y **Estomatología** (no confundir con Servicios Estomatológicos) presentan los mayores decrecimientos promedio.
            *   **Desafíos Diversos:** Carreras como **Ingeniería Agrícola**, **Artes Visuales**, **Matemática**, **Música** y varias **Ingenierías** (Hidráulica, Civil, Telecomunicaciones, Industrial) también aparecen en esta lista, sugiriendo una revisión de sus tendencias.
            """)
        else:
            st.info("No se pudo generar el gráfico de carreras con menor CAGR.")

    show_info(msg_a6)

    st.markdown("""
    **Reflexiones Estratégicas a partir de estos Ritmos:**
    *   Un **alto CAGR** no siempre significa una matrícula total masiva (podría ser una carrera pequeña creciendo rápido), pero sí indica una **tendencia positiva fuerte** que merece atención, ya sea para fomentar o para asegurar recursos.
    *   Un **CAGR bajo o negativo** en carreras importantes podría ser una señal para investigar las causas: ¿cambios en el mercado laboral, preferencias estudiantiles, oferta académica?
    *   Es crucial cruzar esta información de CAGR con la matrícula absoluta (del ranking) para obtener una imagen completa.
    """)

    contexto_cagr_ia = "El análisis actual muestra las carreras con mayor y menor Tasa de Crecimiento Anual Compuesto (CAGR) de su matrícula. Los datos se presentan en dos gráficos de barras."
    datos_cagr_ia = []
    if fig_a6_top_cagr:
        datos_cagr_ia.append(fig_a6_top_cagr)
    if fig_a6_bottom_cagr:
        datos_cagr_ia.append(fig_a6_bottom_cagr)
    if msg_a6:
        contexto_cagr_ia += f"\nNota del análisis: {msg_a6}"

    ask_ai_component(
        analysis_context=contexto_cagr_ia,
        key="a3_carreras_cagr",
        extra_data=datos_cagr_ia
    )
    st.markdown("---")

def A4(df_main,*args,**kwargs):
    st.header("♀️♂️ Equilibrando la Balanza: Una Mirada a la Perspectiva de Género")
    st.markdown("""
    La universidad no solo forma profesionales, sino que también moldea una sociedad más justa y equitativa.
    En esta sección, nos adentramos en la composición de género de la matrícula universitaria.
    ¿Existe un equilibrio entre hombres y mujeres en las aulas? ¿Hay áreas del conocimiento
    tradicionalmente asociadas a un género que mantienen esos patrones, o estamos presenciando
    una transformación hacia una mayor paridad? Acompáñanos a descubrirlo.
    """)
    with st.spinner("Analizando la perspectiva de género..."):
        fig_a4_ramas, fig_a4_carreras, msg_a4 = analisis_A4(df_main)

    if fig_a4_ramas:
        st.subheader(f"Participación Femenina por Rama de Ciencias (Curso {df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1})")
        st.plotly_chart(fig_a4_ramas, use_container_width=True, key="fig_a4_ramas_genero")
        st.markdown("""
        **El Panorama General por Áreas del Saber:**
        Este gráfico de barras nos muestra el porcentaje de mujeres matriculadas en cada gran rama de ciencias. La línea roja punteada en el 50% representa la paridad perfecta.

        *   **Liderazgo Femenino Pronunciado:** Las **Ciencias Pedagógicas** destacan con más del **80%** de matrícula femenina, seguidas de cerca por las **Ciencias Sociales y Humanísticas** y las **Ciencias Médicas**, ambas superando el **70%**. Esto indica una fuerte presencia y preferencia femenina en estas importantes áreas.
        *   **Mayoría Femenina Sostenida:** Las **Ciencias Económicas**, **Ciencias de las Artes** y **Ciencias Naturales y Matemáticas** también muestran una mayoría de mujeres, con porcentajes que oscilan entre el **55% y el 65%**, situándose por encima de la línea de paridad.
        *   **Cerca de la Paridad o Ligera Mayoría Masculina:** Las **Ciencias Agropecuarias** se encuentran más cerca del equilibrio, aunque aún con una ligera mayoría femenina (casi el 50%).
        *   **Desafíos en Áreas Técnicas y Deportivas:** En contraste, las **Ciencias Técnicas** (aproximadamente 35% mujeres) y, de manera más marcada, las **Ciencias de la Cultura Física y el Deporte** (alrededor del 32% mujeres) son las ramas con la menor representación femenina, indicando una persistente brecha de género en estos campos.
        """)
        
        contexto_ramas_ia = "El análisis actual muestra el porcentaje de participación femenina por rama de ciencias en Cuba para el último curso académico. Los datos están en el gráfico de barras adjunto."
        datos_ramas_ia = [fig_a4_ramas]
        if msg_a4:
            contexto_ramas_ia += f"\nNota del análisis: {msg_a4}"
        
        ask_ai_component(
            analysis_context=contexto_ramas_ia,
            key="a4_ramas_genero",
            extra_data=datos_ramas_ia
        )
    else:
        st.warning("No se pudo generar el gráfico de género por ramas.")
        show_info(msg_a4)

    if fig_a4_carreras:
        st.subheader(f"Zoom a las Carreras: Extremos del Espectro de Género (Curso {df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1}, Matrícula >= 20)")
        st.plotly_chart(fig_a4_carreras, use_container_width=True, key="fig_a4_carreras_genero")
        st.markdown("""
        **Casos Destacados de Mayoría y Minoría Femenina:**
        Estos gráficos nos llevan al detalle de las carreras, mostrando las 10 con mayor porcentaje de mujeres y las 10 con menor porcentaje (es decir, mayor presencia masculina), siempre que tengan una matrícula de al menos 20 estudiantes para asegurar la representatividad.

        *   **Feminización Extrema en Algunas Áreas:** Carreras como **Educación Preescolar** se acercan al 100% de matrícula femenina. Otras, como **Técnico Superior en Logofonoaudiología**, **Educación Logopedia** y **Educación Español-Literatura**, también muestran una abrumadora mayoría de mujeres, superando el 90%. Esto es consistente con la alta feminización de las Ciencias Pedagógicas. **Servicios Estomatológicos** y **Estudios Socioculturales** también destacan en este grupo.

        *   **Dominio Masculino en Ingenierías y Áreas Técnicas:** En el otro extremo, carreras como **Ingeniería Informática**, **Ingeniería en Automática**, **Ciencias de la Computación**, **Gestión del Proceso Inversionista** y varias **Ingenierías Mecánica, Eléctrica y en Técnicos Superior en Entrenamiento Deportivo** presentan porcentajes de mujeres muy bajos, algunos por debajo del 10% y la mayoría por debajo del 25%. Esto refleja la brecha observada en las Ciencias Técnicas y deportivas a nivel de rama.

        *   **Matices Importantes:** Es crucial observar que incluso dentro de las "Top 10 con Menor % de Mujeres", los porcentajes varían. Mientras algunas ingenierías apenas superan el 5-10% de presencia femenina, otras pueden estar más cerca del 20-25%.
        """)

        contexto_carreras_ia = "El análisis actual muestra las 10 carreras con mayor y menor porcentaje de participación femenina, para el último curso académico. Los datos están en el gráfico de barras adjunto."
        datos_carreras_ia = [fig_a4_carreras]
        if msg_a4:
             contexto_carreras_ia += f"\nNota del análisis: {msg_a4}"
        
        ask_ai_component(
            analysis_context=contexto_carreras_ia,
            key="a4_carreras_genero",
            extra_data=datos_carreras_ia
        )
    else:
        st.warning("No se pudo generar el gráfico de género por carreras.")
        if not fig_a4_ramas:
            show_info(msg_a4)

    st.markdown("""
    ---
    **Reflexiones para la Acción:**
    *   La alta feminización en ciertas ramas y carreras es un fenómeno consolidado. Si bien refleja vocaciones, también es importante asegurar que no existan barreras implícitas o desincentivos para la participación masculina en ellas.
    *   El mayor desafío para la equidad de género se encuentra claramente en las **Ciencias Técnicas** y en varias ingenierías específicas, así como en **Ciencias de la Cultura Física y el Deporte**. Se requieren estrategias continuas y efectivas para atraer y retener a más mujeres en estos campos cruciales para el desarrollo tecnológico y social.
    *   Estos datos son una invitación a profundizar: ¿Cuáles son las causas de estos desbalances? ¿Cómo podemos inspirar a las nuevas generaciones a explorar todas las áreas del conocimiento sin sesgos de género?
    """)

def A5(df_main,*args,**kwargs):
    st.header("🏛️ Universidades en Perspectiva: Descubriendo Fortalezas y Focos de Especialización")
    st.markdown("""
    Cada universidad es un ecosistema único con su propia historia, vocación y áreas de excelencia.
    En esta sección, cambiamos nuestra perspectiva para analizar cómo se distribuye el talento estudiantil
    a nivel institucional. ¿Qué universidades concentran la mayor cantidad de estudiantes?
    ¿Existen centros altamente especializados en ciertas ramas o carreras? ¿Y qué carreras
    son joyas raras, ofrecidas solo por unas pocas instituciones?
    """)
    with st.spinner("Preparando el análisis institucional..."):
        fig_a5_treemap, df_treemap_data, df_carreras_unicas_a5, msg_a5 = analisis_A5(df_main)

    if fig_a5_treemap:
        st.subheader(f"Mapa Interactivo de la Matrícula Universitaria (Curso {df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1})")
        st.plotly_chart(fig_a5_treemap, use_container_width=True, key="fig_a5_treemap_unis")
        st.markdown("""
        **Navegando el Universo Institucional:**
        Este "mapa de árbol" (treemap) es una representación visual de la matrícula total.
        *   **El Tamaño Importa:** El área de cada rectángulo es proporcional al número de estudiantes. Comienza con "Todas las Universidades"; haz clic en una universidad (ej. `UCLV`, `UO`, `CUJAE`) para ver cómo se desglosa su matrícula por ramas de ciencias. Un nuevo clic en una rama te mostrará las carreras dentro de ella y su peso en esa institución.
        *   **Identifica los Gigantes:** A simple vista, puedes identificar las universidades con mayor volumen de estudiantes. Por ejemplo, la **UCMLH (Universidad de Ciencias Médicas de La Habana)**, **UCM SC (Universidad de Ciencias Médicas de Santiago de Cuba)**, y **UM (Universidad de Matanzas)**, entre otras, muestran rectángulos considerablemente grandes, indicando una matrícula importante.
        *   **Focos de Especialización:** Observa cómo algunas universidades tienen casi toda su "área" concentrada en una o dos ramas (ej. las Universidades de Ciencias Médicas predominantemente en "Ciencias Médicas"), mientras otras muestran una mayor diversificación.
        """)
        
        contexto_treemap_ia = "El análisis actual es sobre la distribución jerárquica de la matrícula por universidad, rama de ciencias y carrera, para el último curso. Los datos completos están en el DataFrame adjunto."
        datos_treemap_ia = []
        if df_treemap_data is not None:
            datos_treemap_ia.append(df_treemap_data)
        if msg_a5:
             contexto_treemap_ia += f"\nNota del análisis: {msg_a5}"

        #Nota para el que revise esta kk: demasiados datos para enviar a la IA, mejor no incluir la ia aqui, si ve este mensaje es que se me olvidó encontrarle una mejor solucion...
        #ask_ai_component(
        #    analysis_context=contexto_treemap_ia,
        #    key="a5_treemap_unis",
        #    extra_data=datos_treemap_ia
        #)
    else:
        st.warning("No se pudo generar el treemap de distribución.")
        show_info(msg_a5)

    if df_carreras_unicas_a5 is not None and not df_carreras_unicas_a5.empty:
        st.subheader("Joyas Académicas: Carreras con Oferta Limitada")
        st.markdown(f"Listado de carreras y el número de universidades que las impartieron con matrícula en el curso {df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1}, ordenadas de menor a mayor número de oferentes.")
        st.dataframe(df_carreras_unicas_a5, height=350)
        st.markdown("""
        *   Las carreras en la parte superior de esta lista son ofrecidas por muy pocas instituciones, lo que puede indicar una alta especialización, una nueva oferta en expansión, o la necesidad de evaluar si su alcance geográfico es adecuado para la demanda potencial.
        """)

        contexto_unicas_ia = "El análisis actual muestra un listado de carreras y el número de universidades que las ofrecen, identificando aquellas con oferta más limitada. Los datos se proporcionan en la tabla adjunta."
        datos_unicas_ia = [df_carreras_unicas_a5]
        if msg_a5:
            contexto_unicas_ia += f"\nNota del análisis: {msg_a5}"

        ask_ai_component(
            analysis_context=contexto_unicas_ia,
            key="a5_carreras_unicas",
            extra_data=datos_unicas_ia
        )
    else:
        if msg_a5 and not fig_a5_treemap:
            show_info(msg_a5)
    
    st.markdown("---")
    
    st.subheader("Lupa en Carreras Clave: ¿Quién es Quién en la Formación Específica?")
    st.markdown("""
    Selecciona hasta 3 carreras de tu interés. El gráfico mostrará la evolución histórica de la matrícula
    para esas carreras, desglosada por cada universidad que las imparte. Esto nos permite comparar
    el peso y la trayectoria de diferentes instituciones en la formación de profesionales en campos específicos.
        
    *Si el gráfico parece muy denso, intenta seleccionar menos carreras o concéntrate en las tendencias generales de las universidades más grandes para cada carrera.*
    """)

    todas_carreras_sorted = sorted(df_main['carrera'].unique())
    default_carreras_a9 = []
    if todas_carreras_sorted:
        top_carreras_df = df_main.groupby('carrera')['Matricula_Total'].sum().nlargest(2)
        if not top_carreras_df.empty:
            default_carreras_a9 = top_carreras_df.index.tolist()
        else:
            default_carreras_a9 = todas_carreras_sorted[:min(2, len(todas_carreras_sorted))]

    carreras_seleccionadas_a9 = st.multiselect(
        "Carreras para comparar evoluciones por universidad:",
        options=todas_carreras_sorted,
        default=default_carreras_a9,
        max_selections=3,
        key="select_carreras_a9_unis"
    )

    if carreras_seleccionadas_a9:
        with st.spinner("Generando gráfico comparativo por universidad..."):
            fig_a9, msg_a9 = analisis_A9(df_main, carreras_a_comparar=carreras_seleccionadas_a9)

        if fig_a9:
            st.plotly_chart(fig_a9, use_container_width=True, key="fig_a9_comparativa_unis")
            show_info(msg_a9)

            contexto_comparativa_ia = f"El análisis actual muestra la evolución histórica de la matrícula para las carreras seleccionadas ({', '.join(carreras_seleccionadas_a9)}), desglosada por cada universidad que las imparte. Los datos están en el gráfico adjunto."
            datos_comparativa_ia = [fig_a9]
            if msg_a9:
                 contexto_comparativa_ia += f"\nNota del análisis: {msg_a9}"

            dynamic_key = "a5_comparativa_unis_" + "_".join(sorted([c.replace(' ','_') for c in carreras_seleccionadas_a9]))

            ask_ai_component(
                analysis_context=contexto_comparativa_ia,
                key=dynamic_key,
                extra_data=datos_comparativa_ia
            )
        else:
            st.warning(msg_a9 if msg_a9 else f"No se pudo generar el gráfico comparativo para: {', '.join(carreras_seleccionadas_a9)}.")
    else:
        st.info("Selecciona al menos una carrera para ver la comparativa de su evolución por universidad.")
    
    st.markdown("""
    ---
    **Visiones Estratégicas para la Red de Universidades:**
    *   **Potenciar la Excelencia:** Identificar universidades líderes en carreras clave puede guiar la inversión para convertirlas en centros de referencia nacional o internacional.
    *   **Optimizar Recursos:** El treemap y el análisis de ofertas únicas pueden revelar duplicidades innecesarias o, por el contrario, la necesidad de expandir la oferta de ciertas carreras en más regiones.
    *   **Colaboración Interinstitucional:** Conocer las fortalezas de cada una puede fomentar sinergias, programas conjuntos y movilidad estudiantil y profesoral.
    """)

def A6(df_main,*args,**kwargs):
    st.header("🔭 Mirando al Mañana: ¿Qué Podríamos Esperar? (Proyecciones Futuras)")
    st.markdown("""
    Anticipar el futuro es un desafío, pero analizar las tendencias recientes nos permite trazar
    escenarios posibles. En esta sección, volvemos a examinar nuestros indicadores clave de matrícula,
    pero esta vez extendiendo nuestra mirada dos cursos académicos hacia adelante mediante proyecciones.

    ⚠️ **Una Brújula, no un Oráculo:** Es fundamental recordar que estas son **proyecciones**, no predicciones
    infalibles. Se basan en modelos de **Regresión Lineal simple aplicados a los últimos 6 años de datos históricos**
    (o menos, si los datos son insuficientes para una rama o carrera específica). Múltiples factores no contemplados
    en estos modelos (cambios de políticas, crisis económicas, nuevas demandas sociales, etc.) podrían
    alterar significativamente estas trayectorias. Utilicémoslas como una herramienta para la reflexión
    estratégica y la planificación proactiva, no como un destino escrito en piedra.
    """)
    st.info("Las líneas discontinuas y los puntos más allá del curso 2024-2025 representan las proyecciones.")
    st.markdown("---")

    st.subheader(" Horizonte Nacional: Proyección de la Matrícula Total")
    with st.spinner("Calculando la proyección de matrícula nacional..."):
        fig_a1_proy, msg_a1_proy = analisis_A1(df_main, incluir_proyeccion=True)
    if fig_a1_proy:
        st.plotly_chart(fig_a1_proy, use_container_width=True, key="fig_a1_futuro_proy_sec6")
        st.markdown("""
        **Interpretando la Tendencia Nacional Proyectada:**
        *   Partiendo de la matrícula del curso 2024-2025 (alrededor de **205,000 estudiantes**), la proyección basada en la tendencia de los últimos seis años sugiere una **continuación de la fase de ajuste o declive moderado**.
        *   Para el curso **2025-2026**, el modelo estima una matrícula que podría rondar los **195,000-200,000 estudiantes**.
        *   Hacia **2026-2027**, esta cifra podría situarse cerca de los **185,000-190,000 estudiantes**.
        *   **Reflexión:** Si esta tendencia se materializa, ¿qué implicaciones tendría para la capacidad instalada, la asignación de recursos y las estrategias de captación a nivel nacional?
        """)
        show_info(msg_a1_proy)

        contexto_proy_nac_ia = "El análisis actual es sobre la proyección de la matrícula total nacional en Cuba para los próximos dos cursos. Los datos históricos y proyectados están en el gráfico adjunto."
        datos_proy_nac_ia = [fig_a1_proy]
        if msg_a1_proy:
            contexto_proy_nac_ia += f"\nNota del análisis: {msg_a1_proy}"

        ask_ai_component(
            analysis_context=contexto_proy_nac_ia,
            key="a6_proy_nacional",
            extra_data=datos_proy_nac_ia
        )
    else:
        st.warning(msg_a1_proy if msg_a1_proy else "No se pudo generar la proyección nacional.")
    st.markdown("---")

    st.subheader(" Mosaico de Saberes del Mañana: Proyección por Rama de Ciencias")
    with st.spinner("Calculando la proyección por ramas de ciencias..."):
        fig_a2_abs_proy, _, msg_a2_proy = analisis_A2(df_main, incluir_proyeccion=True)
    if fig_a2_abs_proy:
        st.plotly_chart(fig_a2_abs_proy, use_container_width=True, key="fig_a2_abs_futuro_proy_sec6")
        st.markdown("""
        **Dinámicas Proyectadas en las Áreas del Conocimiento:**
        Observando las líneas discontinuas para cada rama:
        *   **Ciencias Médicas:** A pesar de su descenso reciente desde el pico, la proyección sugiere que podrían estabilizarse o continuar un declive más suave, manteniéndose como la rama más numerosa, posiblemente entre **55,000 y 65,000 estudiantes** en los próximos dos años.
        *   **Ciencias Pedagógicas:** La fuerte caída reciente parece influir en su proyección, que apunta a una continuación de esta tendencia, situándose entre **35,000 y 40,000 estudiantes**.
        *   **Ramas Intermedias (Técnicas, Sociales, Económicas):** Estas ramas, que ya mostraban un declive, podrían continuar esa trayectoria de forma moderada. Por ejemplo, las Ciencias Técnicas y Sociales podrían moverse hacia los **15,000-20,000 estudiantes** cada una.
        *   **Ramas Menores:** Aquellas con menor volumen (Agropecuarias, Cultura Física, Naturales, Artes) probablemente mantendrán matrículas comparativamente bajas, con proyecciones que siguen sus tendencias recientes, algunas de ellas también a la baja.
        *   **Consideración Clave:** La suma de estas proyecciones individuales por rama debería aproximarse a la proyección nacional total, pero pequeñas discrepancias pueden surgir debido a que cada modelo se ajusta independientemente.
        """)
        show_info(msg_a2_proy)

        contexto_proy_ramas_ia = "El análisis actual es sobre la proyección de la matrícula por rama de ciencias en Cuba para los próximos dos cursos. Los datos están en el gráfico adjunto."
        datos_proy_ramas_ia = [fig_a2_abs_proy]
        if msg_a2_proy:
            contexto_proy_ramas_ia += f"\nNota del análisis: {msg_a2_proy}"

        ask_ai_component(
            analysis_context=contexto_proy_ramas_ia,
            key="a6_proy_ramas",
            extra_data=datos_proy_ramas_ia
        )
    else:
        st.warning(msg_a2_proy if msg_a2_proy else "No se pudo generar la proyección por ramas.")
    st.markdown("---")

    st.subheader(" Carreras Clave en el Horizonte: Proyección Interactiva")
    st.markdown("Selecciona hasta 3 carreras de tu interés para visualizar su proyección de matrícula individual.")

    todas_carreras_sorted_a7 = sorted(df_main['carrera'].unique())
    default_carreras_a7 = []
    if todas_carreras_sorted_a7:
        try:
            default_carreras_a7 = df_main.groupby('carrera')['Matricula_Total'].sum().nlargest(3).index.tolist()
        except:
            default_carreras_a7 = todas_carreras_sorted_a7[:min(3, len(todas_carreras_sorted_a7))]

    carreras_seleccionadas_a7 = st.multiselect(
        "Selecciona carreras para proyectar:",
        options=todas_carreras_sorted_a7,
        default=default_carreras_a7,
        max_selections=3,
        key="select_carreras_a7_proy"
    )

    if carreras_seleccionadas_a7:
        with st.spinner("Calculando la proyección para las carreras seleccionadas..."):
            fig_a7_proy, msg_a7_proy = analisis_A7(df_main, carreras_seleccionadas=carreras_seleccionadas_a7)
        if fig_a7_proy:
            st.plotly_chart(fig_a7_proy, use_container_width=True, key="fig_a7_futuro_proy_dinamica")
            st.markdown(f"""
            **Posibles Escenarios para las Carreras Seleccionadas ({', '.join(carreras_seleccionadas_a7)}):**
            *   Observa las líneas discontinuas para cada una de las carreras que elegiste. ¿Qué tendencia general muestran?
            *   ¿Alguna de ellas parece tener una proyección de crecimiento, estabilidad o declive más marcada?
            *   **Implicaciones:** Estas proyecciones individuales son cruciales. Un descenso proyectado en una carrera de alta demanda, por ejemplo, requeriría un análisis profundo de sus causas y posibles impactos.
            """)
            show_info(msg_a7_proy)

            contexto_proy_carreras_ia = f"El análisis actual es sobre la proyección de matrícula para las carreras seleccionadas: {', '.join(carreras_seleccionadas_a7)}. Los datos están en el gráfico adjunto."
            datos_proy_carreras_ia = [fig_a7_proy]
            if msg_a7_proy:
                contexto_proy_carreras_ia += f"\nNota del análisis: {msg_a7_proy}"

            dynamic_key = "a6_proy_carreras_" + "_".join(sorted([c.replace(' ', '_') for c in carreras_seleccionadas_a7]))
            
            ask_ai_component(
                analysis_context=contexto_proy_carreras_ia,
                key=dynamic_key,
                extra_data=datos_proy_carreras_ia
            )
        else:
            st.warning(msg_a7_proy if msg_a7_proy else f"No se pudo generar la proyección para: {', '.join(carreras_seleccionadas_a7)}.")
    else:
        st.info("Selecciona al menos una carrera para ver su proyección.")

    st.markdown("""
    ---
    **Planificando con Visión de Futuro:**
    Estas proyecciones, con todas sus limitaciones, son un insumo valioso para:
    *   Anticipar necesidades de **infraestructura y profesorado**.
    *   Debatir sobre la **asignación de plazas y recursos** entre diferentes áreas y carreras.
    *   Identificar áreas que podrían requerir **estrategias proactivas** para revertir tendencias negativas o para gestionar un crecimiento sostenible.
    *   Fomentar un diálogo informado sobre el **futuro de la oferta académica** en Cuba.
    """)

def A7(df_main,*args,**kwargs):
    st.header("💡 Áreas de Atención: Identificando Desafíos y Oportunidades Específicas")
    st.markdown("""
    Más allá de las grandes tendencias, existen situaciones particulares en carreras y universidades
    que merecen una lupa especial. Algunas carreras pueden estar emergiendo con vigor, otras podrían
    haber concluido su ciclo de oferta, y un tercer grupo quizás lucha por atraer un número suficiente
    de estudiantes. Identificar estos casos no es señalar problemas, sino descubrir oportunidades
    para una gestión académica más precisa, ágil y adaptada a las realidades cambiantes.
    """)
    with st.spinner("Identificando casos de atención específica..."):
        resultados_a8, msg_a8 = analisis_A8(df_main)
    
    show_info(msg_a8)

    if resultados_a8:
        st.subheader("🌱 Sembrando el Futuro: Posibles Nuevas Ofertas o Reactivaciones")
        st.markdown("""
        Aquí listamos carreras que no registraban matrícula en los primeros años del período analizado (2015-16),
        pero que sí la tienen en cursos más recientes y en el último año registrado. Esto podría indicar
        el lanzamiento de nuevas carreras o la reactivación de algunas que estuvieron en pausa.
        """)
        df_nuevas = resultados_a8.get("nuevas_ofertas")
        if df_nuevas is not None and not df_nuevas.empty:
            st.dataframe(df_nuevas)
            st.markdown(f"*Se detectaron **{len(df_nuevas)}** casos que cumplen este criterio.*")

            contexto_nuevas_ia = "El análisis actual muestra un listado de carreras que parecen ser nuevas ofertas o reactivaciones, ya que no tenían matrícula al inicio del período pero sí al final. Los datos están en la tabla adjunta."
            datos_nuevas_ia = [df_nuevas]
            if msg_a8:
                contexto_nuevas_ia += f"\nNota general del análisis: {msg_a8}"

            ask_ai_component(
                analysis_context=contexto_nuevas_ia,
                key="a7_nuevas_ofertas",
                extra_data=datos_nuevas_ia
            )
        else:
            st.info("No se identificaron carreras que cumplan claramente con el criterio de 'nueva oferta reciente' en el período analizado.")
        st.markdown("---")

        st.subheader("🍂 Ciclos que Concluyen: Posibles Ceses de Oferta")
        st.markdown("""
        Presentamos carreras que contaban con matrícula al inicio del período de análisis pero que
        no registran estudiantes en los últimos cursos. Esto podría sugerir una discontinuación
        planificada o una interrupción que requiere verificación.
        """)
        df_cesadas = resultados_a8.get("cesadas_ofertas")
        if df_cesadas is not None and not df_cesadas.empty:
            st.dataframe(df_cesadas)
            st.markdown(f"*Se detectaron **{len(df_cesadas)}** casos que cumplen este criterio.*")

            contexto_cesadas_ia = "El análisis actual muestra un listado de carreras que podrían haber cesado su oferta, ya que tenían matrícula al inicio del período pero no al final. Los datos están en la tabla adjunta."
            datos_cesadas_ia = [df_cesadas]
            if msg_a8:
                contexto_cesadas_ia += f"\nNota general del análisis: {msg_a8}"

            ask_ai_component(
                analysis_context=contexto_cesadas_ia,
                key="a7_cese_oferta",
                extra_data=datos_cesadas_ia
            )
        else:
            st.info("No se identificaron carreras que cumplan claramente con el criterio de 'cese de oferta reciente'.")
        st.markdown("---")
            
        df_baja = resultados_a8.get("baja_matricula")
        umbral = resultados_a8.get("umbral_bajo", 10)
        st.subheader(f"📉 Focos de Atención: Carreras con Matrícula Reducida (Inferior a {umbral} Estudiantes)")
        st.markdown(f"""
        Finalmente, listamos aquellas carreras que, en el último curso académico registrado
        ({df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1}), tuvieron una matrícula activa (mayor que cero)
        pero inferior a **{umbral} estudiantes**. Estas situaciones pueden tener diversas explicaciones
        y ameritan un análisis particularizado.
        """)
        if df_baja is not None and not df_baja.empty:
            st.dataframe(df_baja)
            st.markdown(f"*Se detectaron **{len(df_baja)}** casos con matrícula inferior a {umbral} (y >0) en el último año.*")

            contexto_baja_ia = f"El análisis actual muestra un listado de carreras con matrícula reducida (menor a {umbral} estudiantes) en el último año. Los datos están en la tabla adjunta."
            datos_baja_ia = [df_baja]
            if msg_a8:
                contexto_baja_ia += f"\nNota general del análisis: {msg_a8}"

            ask_ai_component(
                analysis_context=contexto_baja_ia,
                key="a7_baja_matricula",
                extra_data=datos_baja_ia
            )
        else:
            st.info(f"No se identificaron carreras con matrícula inferior a {umbral} (y >0) en el último año.")
    else:
        st.warning("No se pudo completar el análisis de áreas de atención (A8).")
        
    st.markdown("""
    ---
    **Decisiones Informadas para una Gestión Proactiva:**
    La información presentada en esta sección es un llamado a la acción específica:
    *   **Nuevas Ofertas / Reactivaciones:**
        *   **Verificar:** ¿Corresponden a lanzamientos o reactivaciones planificadas?
        *   **Monitorear:** Evaluar su evolución inicial, necesidades de recursos y estrategias de consolidación.
        *   **Aprender:** ¿Responden a una demanda social o laboral emergente que podría replicarse?
    *   **Posibles Ceses de Oferta:**
        *   **Confirmar:** ¿La discontinuación es oficial y definitiva? Actualizar registros si es necesario.
        *   **Evaluar Impacto:** Si el cese no fue planificado o tiene implicaciones negativas (ej. única oferta en una región), investigar causas.
    *   **Matrícula Reducida:**
        *   **Análisis Causa-Raíz:** ¿Se trata de carreras altamente especializadas con demanda limitada por naturaleza? ¿Problemas de captación? ¿Desactualización curricular? ¿Falta de pertinencia laboral?
        *   **Estrategias Diferenciadas:** Dependiendo del diagnóstico, las acciones podrían ir desde la promoción focalizada, rediseño curricular, hasta la consideración de fusión con otras carreras o, en última instancia, una discontinuación planificada si no se justifica su mantenimiento.

    Una gestión atenta a estos detalles permite optimizar recursos, responder mejor a las necesidades
    del país y asegurar la vitalidad y pertinencia de la oferta académica universitaria.
    """)

def B1(df_main,*args,**kwargs):
    st.header("🔬 Playground: Perfil Detallado de Carrera: Una Radiografía Completa")
    st.markdown("""
    Sumérgete en los detalles de la carrera que elijas. Descubre su evolución histórica de matrícula,
    incluyendo la composición por género, su tasa de crecimiento promedio en el período que definas,
    y un panorama de las universidades que la imparten actualmente. ¡Una visión 360º a tu alcance!
    """)

    todas_carreras_unicas = sorted(df_main['carrera'].unique())
    carrera_sel_b1 = st.selectbox(
        "Selecciona una Carrera para analizar su perfil:",
        options=todas_carreras_unicas,
        index=todas_carreras_unicas.index("MEDICINA") if "MEDICINA" in todas_carreras_unicas else 0,
        key="sel_carrera_b1_perfil_final"
    )

    fig_b1_evol_gen = None
    df_unis_b1 = None
    fig_pie_genero = None
    fig_bar_unis = None
    cagr_b1_info = {}
    datos_para_ia = []
    contexto_texto_ia = ""
    msg_b1 = ""

    if carrera_sel_b1:
        st.markdown("---")
        
        with st.spinner(f"Generando perfil para {carrera_sel_b1}..."):
            fig_b1_evol_gen, df_evol_para_cagr_b1, df_unis_b1, datos_genero_ultimo_ano_b1, rama_b1, msg_b1 = analisis_perfil_carrera(
                df_main.copy(),
                carrera_sel_b1
            )
        
        st.subheader(f"Perfil Integral de: {carrera_sel_b1}")
        st.markdown(f"**Rama de Ciencias:** {rama_b1}")
        show_info(msg_b1)

        if fig_b1_evol_gen:
            st.plotly_chart(fig_b1_evol_gen, use_container_width=True, key="fig_b1_perfil_evol_genero_final")
        else:
            st.warning("No se pudo generar el gráfico de evolución para esta carrera.")

        st.markdown("---")

        if df_evol_para_cagr_b1 is not None and not df_evol_para_cagr_b1.empty:
            anos_disponibles_carrera_b1 = sorted(df_evol_para_cagr_b1['Ano_Inicio_Curso'].unique())
            if len(anos_disponibles_carrera_b1) >= 2:
                st.markdown("**Crecimiento Promedio Anual (CAGR) para el Período Seleccionado:**")
                st.caption("El CAGR indica la tasa de crecimiento porcentual promedio por año. Ajusta el slider para explorar diferentes períodos.")
                
                selected_years_cagr = st.slider(
                    "Selecciona el rango de años (inicio-fin) para el cálculo del CAGR:",
                    min_value=int(anos_disponibles_carrera_b1[0]),
                    max_value=int(anos_disponibles_carrera_b1[-1]),
                    value=(int(anos_disponibles_carrera_b1[0]), int(anos_disponibles_carrera_b1[-1])),
                    key=f"slider_cagr_dinamico_{carrera_sel_b1.replace(' ','_')}"
                )
                ano_inicio_cagr_sel, ano_fin_cagr_sel = selected_years_cagr

                if ano_inicio_cagr_sel < ano_fin_cagr_sel:
                    cagr_b1_info = calcular_cagr_dinamico(df_evol_para_cagr_b1, ano_inicio_cagr_sel, ano_fin_cagr_sel)
                    st.metric(
                        label=f"CAGR {cagr_b1_info.get('periodo', '')}",
                        value=cagr_b1_info.get('valor', 'N/A')
                    )
                else:
                    st.warning("El año inicial del período CAGR debe ser menor que el año final para un cálculo válido.")
            else:
                st.info(f"No hay suficientes años de datos para '{carrera_sel_b1}' para calcular un CAGR con período seleccionable.")
        st.markdown("---")
        
        col_b1_genero_metric, col_b1_genero_pie = st.columns([1,1])

        with col_b1_genero_metric:
            st.markdown(f"**Composición de Género (Curso {df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1}):**")
            if datos_genero_ultimo_ano_b1 and datos_genero_ultimo_ano_b1.get('Total', 0) > 0:
                st.metric(label="Total Mujeres", value=f"{int(datos_genero_ultimo_ano_b1['Mujeres']):,}")
                st.metric(label="Total Hombres", value=f"{int(datos_genero_ultimo_ano_b1['Hombres']):,}")
            else:
                st.info("No hay datos de género disponibles para el último año.")

        with col_b1_genero_pie:
            if datos_genero_ultimo_ano_b1 and datos_genero_ultimo_ano_b1.get('Total', 0) > 0:
                df_pie_genero = pd.DataFrame({
                    'Genero': ['Mujeres', 'Hombres'],
                    'Cantidad': [datos_genero_ultimo_ano_b1['Mujeres'], datos_genero_ultimo_ano_b1['Hombres']]
                })
                fig_pie_genero = px.pie(df_pie_genero, values='Cantidad', names='Genero',
                                        title=f"Distribución de Género en {carrera_sel_b1}:",
                                        color_discrete_map={'Mujeres':'lightpink', 'Hombres':'lightskyblue'})
                fig_pie_genero.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie_genero, use_container_width=True, key="pie_genero_b1")

        st.markdown("---")

        if df_unis_b1 is not None and not df_unis_b1.empty:
            st.markdown(f"**Universidades que imparten '{carrera_sel_b1}' (Matrícula en último curso):**")
            df_unis_b1_sorted = df_unis_b1.sort_values(by=f'Matrícula {df_main["Ano_Inicio_Curso"].max()}-{df_main["Ano_Inicio_Curso"].max()+1}', ascending=True)
            fig_bar_unis = px.bar(
                df_unis_b1_sorted,
                x=f'Matrícula {df_main["Ano_Inicio_Curso"].max()}-{df_main["Ano_Inicio_Curso"].max()+1}',
                y='Universidad',
                orientation='h',
                title=f"Distribución por Universidad: {carrera_sel_b1}",
                height=max(300, len(df_unis_b1_sorted) * 30)
            )
            fig_bar_unis.update_layout(yaxis_title="Universidad", xaxis_title="Matrícula")
            st.plotly_chart(fig_bar_unis, use_container_width=True, key="fig_b1_bar_unis_final")
        elif df_unis_b1 is not None and df_unis_b1.empty:
             st.info(f"Ninguna universidad registró matrícula para '{carrera_sel_b1}' en el último curso.")
        else:
            st.info("No se encontraron datos de universidades para esta carrera en el último año.")

        contexto_texto_ia = (
            f"Se está analizando el perfil de la carrera: **{carrera_sel_b1}**.\n"
            f"Esta carrera pertenece a la rama de ciencias: **{rama_b1}**.\n"
        )
        if cagr_b1_info:
            contexto_texto_ia += (
                f"Para el período seleccionado ({cagr_b1_info.get('periodo', '')}), la Tasa de Crecimiento Anual Compuesta (CAGR) "
                f"es del **{cagr_b1_info.get('valor', 'N/A')}**."
            )
        if msg_b1:
             contexto_texto_ia += f"\nMensaje adicional del análisis: {msg_b1}"
             
        if fig_b1_evol_gen:
            datos_para_ia.append(fig_b1_evol_gen)
        if fig_pie_genero:
            datos_para_ia.append(fig_pie_genero)
        if fig_bar_unis:
            datos_para_ia.append(fig_bar_unis)

    else:
        st.info("Por favor, selecciona una Carrera para continuar.")
        datos_para_ia = []

    ask_ai_component(
        analysis_context=contexto_texto_ia,
        key=f"b1_perfil_carrera{carrera_sel_b1.replace(' ','_')}",
        extra_data=datos_para_ia
    )

def B2(df_main, df_ins,*args,**kwargs):
    st.header("🗺️ B2. Guía de Instituciones: Explora la Oferta Académica por Localidad")
    st.markdown("""
    Descubre las instituciones de educación superior en Cuba, filtrando por provincia y municipio.
    Para cada universidad, encontrarás información general, su composición de género, las ramas de ciencias
    que ofrece y las carreras disponibles con su matrícula en el último año académico registrado.
    """)

    contexto_texto_ia = ""
    datos_para_ia = []

    if df_ins.empty:
        st.warning("Los datos de instituciones ('db_uni.parquet') no están disponibles o están vacíos. Esta sección no puede mostrarse.")
    else:
        st.markdown("#### Filtros de Búsqueda:")
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            provincias_disponibles_b2 = ["TODAS LAS PROVINCIAS"] + sorted(df_ins['provincia'].unique().tolist())
            provincia_sel_b2 = st.selectbox(
               "Provincia:", options=provincias_disponibles_b2, key="sel_prov_b2_guia_cuerpo_final")
        with col_filtro2:
            municipios_disponibles_filtrados_b2 = ["TODOS LOS MUNICIPIOS"]
            if provincia_sel_b2 != "TODAS LAS PROVINCIAS":
                municipios_de_provincia = sorted(df_ins[df_ins['provincia'] == provincia_sel_b2]['municipio'].unique().tolist())
                municipios_disponibles_filtrados_b2.extend(municipios_de_provincia)
            municipio_sel_b2 = st.selectbox(
                "Municipio:", options=municipios_disponibles_filtrados_b2, key="sel_mun_b2_guia_cuerpo_final",
                disabled=(provincia_sel_b2 == "TODAS LAS PROVINCIAS")
            )
        
        pattern_sel_b2 = st.text_input(
            "Buscar por nombre o sigla de institución (filtro visual):",
            key="sel_patron_b2"
        )
        st.markdown("---")

        with st.spinner("Cargando guía de instituciones..."):
            municipio_a_pasar = None
            if provincia_sel_b2 != "TODAS LAS PROVINCIAS" and municipio_sel_b2 != "TODOS LOS MUNICIPIOS":
                municipio_a_pasar = municipio_sel_b2
            
            guia_data_b2, msg_b2 = analisis_guia_universidades(
                df_ins, df_main,
                provincia_seleccionada=provincia_sel_b2,
                municipio_seleccionado=municipio_a_pasar)
        show_info(msg_b2)

        if guia_data_b2:
            contexto_texto_ia = f"Análisis de la guía de instituciones. Filtros aplicados:\n- Provincia: {provincia_sel_b2}\n- Municipio: {municipio_sel_b2}"
            if msg_b2:
                contexto_texto_ia += f"\nMensaje del análisis: {msg_b2}"
            
            fichas_tecnicas_unis = []
            
            filtered_guia_data = {}
            if pattern_sel_b2:
                for nombre, data in guia_data_b2.items():
                    if pattern_sel_b2.lower() in nombre.lower() or pattern_sel_b2.lower() in data.get('sigla', '').lower():
                        filtered_guia_data[nombre] = data
            else:
                filtered_guia_data = guia_data_b2

            st.markdown(f"**Mostrando {len(filtered_guia_data)} de {len(guia_data_b2)} institución(es) según los filtros:**")

            for nombre_uni, data_uni in filtered_guia_data.items():
                
                ficha_actual = {
                    "Institución": nombre_uni,
                    "Sigla": data_uni.get('sigla', 'N/D'),
                    "Provincia": data_uni.get('provincia', 'N/D'),
                    "Municipio": data_uni.get('municipio', 'N/D')
                }
                datos_genero = data_uni.get("datos_genero_uni")
                ficha_actual["Matrícula Mujeres"] = int(datos_genero['Mujeres']) if datos_genero and 'Mujeres' in datos_genero else 0
                ficha_actual["Matrícula Hombres"] = int(datos_genero['Hombres']) if datos_genero and 'Hombres' in datos_genero else 0
                
                lista_carreras_consolidada = []
                if data_uni.get("ramas_ofertadas"):
                    for rama_info in data_uni["ramas_ofertadas"]:
                        if rama_info.get("carreras"):
                            for carrera_info in rama_info["carreras"]:
                                lista_carreras_consolidada.append({
                                    "rama": rama_info['nombre_rama'],
                                    "carrera": carrera_info['nombre_carrera'],
                                    "matricula": carrera_info['matricula_ultimo_ano']
                                })
                ficha_actual["Oferta Académica (CSV)"] = to_csv_string(lista_carreras_consolidada)
                fichas_tecnicas_unis.append(ficha_actual)

                titulo_expander = f"🏛️ {nombre_uni} ({data_uni['sigla']})"
                detalles_loc_exp = [d for d in [data_uni.get('municipio'), data_uni.get('provincia')] if d and d != 'N/D']
                if detalles_loc_exp: titulo_expander += f" | {', '.join(detalles_loc_exp)}"
                if data_uni.get('ano_creacion') and pd.notna(data_uni['ano_creacion']):
                    titulo_expander += f" (Fundada en {int(data_uni['ano_creacion'])})"

                with st.expander(titulo_expander):
                    col_info_basica, col_genero_pastel_uni = st.columns([2, 1])

                    with col_info_basica:
                        st.markdown(f"**Organismo:** `{data_uni.get('organismo', 'N/D')}`")
                        st.markdown(f"**Dirección:** *{data_uni.get('direccion', 'N/D')}*")
                        st.markdown(f"**Modalidad Principal:** `{data_uni.get('modalidad_estudio', 'N/D')}`")

                    with col_genero_pastel_uni:
                        if datos_genero and datos_genero.get('Total', 0) > 0:
                            df_pie_genero_uni = pd.DataFrame({'Género': ['Mujeres', 'Hombres'], 'Cantidad': [datos_genero['Mujeres'], datos_genero['Hombres']]})
                            fig_pie_genero_uni = px.pie(df_pie_genero_uni, values='Cantidad', names='Género',
                                                        title=f"Género Total ({df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1})",
                                                        color_discrete_map={'Mujeres': 'orchid', 'Hombres': 'royalblue'}, height=250)
                            fig_pie_genero_uni.update_layout(margin=dict(t=30, b=0, l=0, r=0), showlegend=False)
                            fig_pie_genero_uni.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig_pie_genero_uni, use_container_width=True)
                        else:
                            st.caption("Sin datos de género disponibles para el último año.")

                    st.markdown("---")
                    if data_uni.get("ramas_ofertadas"):
                        st.markdown("**Oferta Académica (Ramas y Carreras con matrícula en último año):**")
                        for rama_info in data_uni["ramas_ofertadas"]:
                            with st.container():
                                st.markdown(f"##### <span style='color: #1E90FF;'>►</span> {rama_info['nombre_rama']}", unsafe_allow_html=True)
                                if rama_info.get("carreras"):
                                    df_carreras_rama = pd.DataFrame(rama_info["carreras"])
                                    df_carreras_rama.rename(columns={'nombre_carrera': 'Carrera', 'matricula_ultimo_ano': 'Matrícula'}, inplace=True)
                                    st.dataframe(df_carreras_rama.set_index('Carrera'))
                                else:
                                    st.caption("  ↳ *No se encontraron carreras con matrícula en el último año.*")
                    else:
                        st.info("Esta institución no tiene ramas de ciencias con oferta activa o carreras con matrícula reportada.")

            if fichas_tecnicas_unis:
                df_consolidado_ia = pd.DataFrame(fichas_tecnicas_unis)
                datos_para_ia.append(df_consolidado_ia)

        elif provincia_sel_b2 and provincia_sel_b2 != "TODAS LAS PROVINCIAS":
            st.info(f"No se encontraron instituciones para los filtros aplicados.")
        else:
            st.info("No hay instituciones para mostrar con los filtros actuales.")
    st.markdown('---')
    ask_ai_component(
        analysis_context=contexto_texto_ia,
        key="b2_guia_instituciones",
        extra_data=datos_para_ia
    )

def conclusion(*args,**kwargs):
    st.header("🏁 Conclusiones y Horizontes Futuros: Forjando la Universidad del Mañana")
    st.markdown("""
    Hemos viajado a través de una década de datos, explorando el complejo ecosistema
    de la educación superior en Cuba. Donde hemos visualizado
    una parte de una historia más grande: la historia de miles de aspiraciones, de esfuerzos institucionales
    y de la incesante búsqueda del conocimiento que define a nuestra nación.

    Este análisis no es un punto final, sino un faro que ilumina el camino recorrido y nos ayuda
    a discernir los senderos que se abren ante nosotros.
    """)
    st.success(
        "**La información es poder, y el poder de estos datos reside en nuestra capacidad para transformarlos en acción sabia y visión estratégica.**"
    )
    st.markdown("---")

    st.subheader("🌟 Destellos del Viaje: Principales Hallazgos en este Recorrido")
    hallazgos_texto = """
    Al mirar atrás en nuestro análisis, emergen varios faros que guían nuestra comprensión:

    1.  **El Pulso Dinámico de la Nación:** La matrícula universitaria nacional ha mostrado una notable capacidad de expansión, alcanzando picos significativos a principios de la década de 2020, seguida de una fase de ajuste más reciente. Esta fluctuación nos recuerda la sensibilidad del sistema a factores contextuales y la necesidad de una planificación flexible. *(Ref. Sección 1)*

    2.  **El Corazón Médico y el Alma Pedagógica:** Las **Ciencias Médicas** se consolidan como la columna vertebral en términos de volumen estudiantil, un testimonio de su importancia estratégica. Las **Ciencias Pedagógicas**, por su parte, han demostrado un dinamismo extraordinario, con un crecimiento masivo seguido de una contracción, reflejando posibles cambios en la demanda o en las políticas de formación docente. *(Ref. Sección 2)*

    3.  **El Ascenso de Nuevas Vocaciones:** El análisis de crecimiento (CAGR) ha revelado el despegue impresionante de carreras como **Servicios Estomatológicos** y el vigor de varias **Ingenierías** (Artística, Procesos Agroindustriales, Informática), señalando posibles nuevas fronteras de interés y demanda laboral. *(Ref. Sección 3)*

    4.  **Avances y Desafíos en la Equidad de Género:** Si bien Cuba exhibe una alta participación femenina en la educación superior, con muchas ramas y carreras mostrando una mayoría de mujeres, persisten desafíos significativos. La subrepresentación femenina en las **Ciencias Técnicas** e **Ingenierías específicas**, así como en **Ciencias de la Cultura Física y el Deporte**, nos llama a redoblar esfuerzos para construir un panorama verdaderamente equitativo. *(Ref. Sección 4)*

    5.  **La Riqueza de la Diversidad Institucional:** Cada universidad aporta su matiz único al sistema. Hemos visto desde grandes centros multidisciplinarios hasta instituciones con una marcada especialización (como las Universidades de Ciencias Médicas). La identificación de carreras con oferta limitada subraya la importancia de una red universitaria coordinada y estratégicamente distribuida. *(Ref. Sección 5)*

    6.  **Una Mirada Prudente al Mañana:** Las proyecciones, aunque sujetas a la incertidumbre inherente al futuro, sugieren una posible continuación de la fase de ajuste en la matrícula general y en varias ramas y carreras clave. Esto no es un augurio, sino una invitación a la preparación y a la acción proactiva. *(Ref. Sección 6)*

    7.  **La Importancia de los Detalles:** El análisis de "Áreas de Atención" nos ha recordado que la salud del sistema también reside en la vitalidad de cada uno de sus componentes, incluyendo las carreras emergentes, aquellas con matrícula reducida o las que podrían estar concluyendo su ciclo. *(Ref. Sección 7)*
    """
    st.markdown(hallazgos_texto)
    st.markdown("---")

    st.subheader("🧭 Trazando la Carta de Navegación: Recomendaciones Estratégicas")
    recomendaciones_texto = """
    Con estos hallazgos como brújula, proponemos las siguientes líneas de acción para la Sede Central
    y todos los actores involucrados en la Educación Superior cubana:

    *   **Fortalecer el Observatorio de la Educación Superior:**
        *   **Acción:** Mantener y enriquecer este sistema de análisis de datos como una herramienta permanente para el monitoreo de tendencias, la evaluación de políticas y la toma de decisiones informadas.
        *   **Impacto Esperado:** Mayor agilidad y capacidad de respuesta del sistema a las dinámicas cambiantes.

    *   **Fomentar la Pertinencia y la Calidad con Visión de Futuro:**
        *   **Acción:** Realizar estudios prospectivos continuos sobre las necesidades del desarrollo socioeconómico del país y las demandas del mercado laboral para alinear la oferta académica. Evaluar y actualizar los planes de estudio de carreras con baja demanda o decrecimiento, e invertir en aquellas con potencial de crecimiento y relevancia estratégica.
        *   **Impacto Esperado:** Egresados mejor preparados para los desafíos del futuro y una mayor contribución de la universidad al desarrollo nacional.

    *   **Impulsar la Equidad de Género en Todas las Disciplinas:**
        *   **Acción:** Diseñar e implementar programas específicos y sostenidos para incentivar la participación femenina en carreras STEM y otras áreas subrepresentadas, y viceversa, abordando estereotipos desde etapas tempranas de la educación.
        *   **Impacto Esperado:** Un sistema universitario más inclusivo que aproveche el talento de toda la población sin sesgos de género.

    *   **Optimizar la Red Universitaria y Promover la Colaboración:**
        *   **Acción:** Utilizar los análisis de especialización y distribución para tomar decisiones sobre la apertura, fusión o cierre de carreras en diferentes instituciones, buscando la eficiencia, la calidad y la cobertura territorial equitativa. Fomentar la creación de redes de conocimiento y programas interuniversitarios.
        *   **Impacto Esperado:** Un sistema más cohesionado, con centros de excelencia fortalecidos y una mejor utilización de los recursos disponibles.

    *   **Integrar la Voz de los Actores:**
        *   **Acción:** Complementar los análisis cuantitativos con investigaciones cualitativas que recojan las percepciones y experiencias de estudiantes, profesores, egresados y empleadores.
        *   **Impacto Esperado:** Decisiones más holísticas y políticas mejor adaptadas a las realidades y expectativas de la comunidad universitaria y la sociedad.
    """
    st.markdown(recomendaciones_texto)
    st.markdown("---")
        
    st.header("✨ Un Legado Continuo, Un Futuro Brillante")
    st.markdown("""
    El análisis de estos datos no es meramente un ejercicio académico; es un acto de responsabilidad
    y un compromiso con el futuro. Las Universidades Cubanas, cada una con su rica historia y su papel trascendental
    en la sociedad, tiene ante sí el desafío y la oportunidad de seguir evolucionando, adaptándose
    e innovando.
        
    Esperamos que estos datos los inspire a todos a trabajar juntos por una educación
    superior que no solo responda a las necesidades del presente, sino que activamente modele
    un mañana más próspero, justo y lleno de conocimiento para todos los jóvenes Cubanos.
    """)

    if 'balloons_shown' not in st.session_state:
        st.session_state.balloons_shown = True
        st.balloons()
    
    contexto_conclusion_ia = (
        "Esta es la sección de conclusiones y recomendaciones finales del análisis sobre la educación superior en Cuba. "
        "A continuación se presentan los principales hallazgos y las recomendaciones estratégicas derivadas de los datos. "
        "Tu rol es discutir estos puntos, ofrecer perspectivas adicionales o responder preguntas sobre estas conclusiones."
        "\n\n--- HALLAZGOS PRINCIPALES ---\n"
        f"{hallazgos_texto}"
        "\n\n--- RECOMENDACIONES ESTRATÉGICAS ---\n"
        f"{recomendaciones_texto}"
    )

    ask_ai_component(
        analysis_context=contexto_conclusion_ia,
        key="conclusiones_finales",
    )