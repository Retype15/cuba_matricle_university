from .plot_functions import *

def info_msg(msg):
    if msg: st.caption(f"ℹ️ {msg}")

def introduction():
    st.header("🎯 Bienvenidos al Corazón de la Educación Superior Cubana")
    st.markdown("""
        La universidad no es solo un edificio; es un crisol de sueños, un motor de progreso y un reflejo
        de las aspiraciones de una sociedad. En este espacio, nos embarcaremos en un viaje analítico,
        explorando las corrientes que moldean la matrícula universitaria en Cuba.
        
        Desde las tendencias generales hasta el detalle de cada carrera y universidad, desentrañaremos
        las historias ocultas detrás de las distintas universidades del país. ¿El objetivo? Proveer una brújula basada en evidencia para
        la toma de decisiones estratégicas, fomentando un sistema de educación superior más fuerte,
        equitativo y alineado con el futuro de la nación.

        **Utiliza el explorador en el panel lateral para navegar por las distintas secciones.** 
        ¡Que comience el descubrimiento!
    """)
    st.success("¡Tu viaje comienza aquí! Selecciona una sección en el menú lateral o usa el botón 'Siguiente'.")

def A1(df_main):
        st.header("🌍 El Pulso Nacional: ¿Cómo Late la Matrícula Universitaria?")
        st.markdown("""
        Imagina que podemos tomarle el pulso a todo el sistema universitario cubano a lo largo de una década.
        ¿Cómo ha sido su ritmo? ¿Ha experimentado momentos de vigoroso crecimiento, períodos de estabilidad,
        o quizás fases donde el latido se ha vuelto más pausado?

        Este primer vistazo nos ofrece la perspectiva más amplia, el electrocardiograma de la matrícula total
        en nuestras universidades. Es el punto de partida esencial para comprender las dinámicas más profundas
        que exploraremos a continuación.
        """)
        
        # Llamamos a la función de análisis A1, solicitando solo la evolución histórica
        with st.spinner("Construyendo la gráfica A2, por favor espere...", show_time=True):
            fig_a1, msg_a1 = analisis_A1( df_main, incluir_proyeccion=False) 
        
        if fig_a1:
            st.plotly_chart(fig_a1, use_container_width=True, key="fig_a1_pulso_nacional")
            if msg_a1: # Si hay algún mensaje de la función (ej. sobre datos insuficientes)
                st.caption(f"ℹ️ {msg_a1}")
            
            st.subheader("Descifrando el Ritmo de la Década (2015-2025):")
            st.markdown("""
            Observando la trayectoria de la matrícula nacional total en el gráfico superior, podemos identificar varias fases clave:

            *   **Impulso Inicial (2015-16 a 2016-17):** El viaje comienza en el curso 2015-2016 con una cifra que ronda los **165,000 estudiantes**. Inmediatamente, en el siguiente curso (2016-2017), se aprecia un **salto significativo y vigoroso**, elevando la matrícula hasta aproximadamente **220,000 estudiantes**. Este fue el mayor incremento interanual del período.

            *   **Crecimiento Sostenido hacia la Cima (2017-18 a 2020-21):** Tras una ligera consolidación en 2017-2018 (alrededor de **225,000**), la tendencia ascendente se retoma con fuerza. La matrícula crece de forma constante, pasando por los **258,000** en 2019-2020, hasta alcanzar su **punto más álgido en el curso 2020-2021, superando los 285,000 estudiantes**. Este representa el pico de matrícula en la década analizada.

            *   **Meseta y Comienzo del Declive (2021-22 a 2022-23):** El curso 2021-2022 muestra una ligera contracción, manteniendo la matrícula aún por encima de los **280,000**. Sin embargo, es en el curso 2022-2023 donde se evidencia un cambio de tendencia más claro, con una **disminución más notable** que sitúa la cifra en torno a los **263,000 estudiantes**.

            *   **Ajuste Reciente (2023-24 a 2024-25):** Los dos últimos cursos registrados muestran una **continuación de la tendencia descendente**, siendo la caída más pronunciada entre 2022-23 y 2023-24 (llegando a unos **218,000**). El curso 2024-2025 cierra con una matrícula cercana a los **205,000 estudiantes**, indicando que, si bien la disminución persiste, su ritmo parece haberse moderado en comparación con el salto anterior.

            Esta panorámica general nos invita a preguntarnos: ¿Qué factores podrían haber impulsado el crecimiento inicial? ¿Qué circunstancias podrían explicar el cambio de tendencia y el declive posterior?
            Estas son preguntas que, aunque no podemos responder completamente solo con estos datos de matrícula, nos preparan para los análisis más detallados que siguen.
            """)
        else:
            # Si msg_a1 ya fue generado por la función, se muestra, sino un mensaje genérico.
            st.warning(msg_a1 if msg_a1 else "No se pudo generar el gráfico del panorama nacional (A1).")

def A2(df_main):
    st.header("📚 Un Mosaico de Saberes: ¿Hacia Dónde se Inclinan los Futuros Profesionales?")
    st.markdown("""
    La universidad es un vasto jardín donde florecen diversas disciplinas. Cada rama del conocimiento,
    desde las Ciencias Médicas o Matemáticas hasta las Artes, representa un camino único de formación y contribución
    a la sociedad. En esta sección, desglosamos la matrícula total para ver cómo se distribuyen
    los estudiantes entre estas grandes áreas, con el objetivo de responder preguntascomo:
    - ¿Hay protagonistas claros?
    - ¿Cómo ha danzado el interés estudiantil a lo largo de la última década?
    """)
    
    # Llamamos a la función de análisis A2, solicitando solo la evolución histórica
    with st.spinner("Construyendo la gráfica A2, uno de los trabajadores se clavó por accidente una espada en la rodilla...", show_time=True):
        fig_a2_abs, fig_a2_pct, msg_a2 = analisis_A2( df_main, incluir_proyeccion=False) 
    
    if fig_a2_abs:
        st.subheader("La Fuerza de Cada Rama: Evolución Histórica de la Matrícula")
        st.plotly_chart(fig_a2_abs, use_container_width=True, key="fig_a2_abs_mosaico")
        st.markdown("""
        **Cada Línea, una Corriente del Conocimiento:**
        Este gráfico traza el viaje de la matrícula absoluta (número total de estudiantes) para cada rama de ciencias a lo largo de los años.

        *   **Liderazgo Destacado:** Las **Ciencias Médicas** (línea verde agua) se erigen como la rama con la matrícula más numerosa de forma consistente durante todo el período, partiendo de unos 70,000 estudiantes en 2015-16, alcanzando un pico impresionante cercano a los **95,000 estudiantes en 2020-2021**, y aunque experimentan un descenso posterior, se mantienen como la principal fuerza, cerrando en 2024-2025 con más de 70,000 estudiantes.

        *   **Persecución y Dinamismo:** Las **Ciencias Pedagógicas** (línea naranja) muestran una trayectoria muy dinámica. Comienzan con una matrícula significativa (alrededor de 30,000), experimentan un crecimiento notable hasta superar los **65,000 estudiantes en 2020-2021 y 2021-2022**, convirtiéndose en la segunda rama más grande durante esos años. Sin embargo, sufren un declive pronunciado en los últimos cursos, finalizando cerca de los 40,000 estudiantes.

        *   **Bloque Intermedio Consistente:** Un grupo de ramas mantiene una presencia estable aunque con fluctuaciones:
            *   Las **Ciencias Técnicas** (línea rosa) y las **Ciencias Sociales y Humanísticas** (línea celeste) muestran trayectorias paralelas, creciendo desde aproximadamente 20,000 estudiantes hasta un pico alrededor de los **30,000-32,000** entre 2020-21 y 2021-22, para luego descender y situarse en torno a los 23,000-25,000 estudiantes al final del período.
            *   Las **Ciencias Económicas** (línea roja) presentan un crecimiento más moderado pero constante hasta 2021-22 (alcanzando unos 24,000 estudiantes), seguido de un descenso similar a otras ramas, terminando cerca de los 15,000.
            *   Las **Ciencias Agropecuarias** (línea azul oscuro) y las **Ciencias de la Cultura Física y el Deporte** (línea verde oscuro/marrón) se mantienen en un rango más bajo, generalmente entre 5,000 y 15,000 estudiantes, con picos alrededor de 2020-2021 y descensos posteriores.

        *   **Nicho Especializado:** Las **Ciencias Naturales y Matemáticas** (línea morada) y las **Ciencias de las Artes** (línea violeta) representan las ramas con menor volumen de matrícula, manteniéndose consistentemente por debajo de los 5,000 estudiantes a lo largo de toda la década. Esto sugiere una alta especialización o una demanda más acotada.
        """)
    else:
        st.warning("No se pudo generar el gráfico de evolución absoluta por rama (A2).")

    if fig_a2_pct:
        st.subheader("El Reparto del Pastel Académico: Distribución Porcentual Histórica")
        st.plotly_chart(fig_a2_pct, use_container_width=True, key="fig_a2_pct_mosaico")
        st.markdown("""
        **Proporciones en el Lienzo Universitario:**
        Este gráfico de área apilada nos muestra qué "porción del pastel" ha representado cada rama de ciencias dentro del total de la matrícula universitaria en cada curso académico.

        *   **Dominio Persistente de las Ciencias Médicas:** La ancha banda verde agua en la parte superior confirma que las Ciencias Médicas han representado consistentemente la mayor proporción de estudiantes, ocupando cerca del **40-50% del total** en su punto más alto (alrededor de 2016-17 y nuevamente hacia 2024-2025, tras una ligera reducción porcentual a mediados del período).

        *   **Ascenso y Descenso de las Ciencias Pedagógicas:** La banda naranja de las Ciencias Pedagógicas muestra un interesante cambio en su peso relativo. Comienza siendo una porción importante, se expande significativamente hasta representar la segunda mayor proporción (llegando a casi un **25-30%** del total alrededor de 2019-2021), pero luego reduce su participación porcentual en los últimos años.

        *   **Estabilidad Relativa en el Medio:** Las Ciencias Técnicas (banda marrón/ocre), Sociales y Humanísticas (banda celeste) y Económicas (banda azul oscuro) mantienen proporciones más estables a lo largo del tiempo, aunque con ligeras variaciones. Juntas, suelen conformar una porción significativa del estudiantado. Por ejemplo, las Ciencias Sociales y Humanísticas parecen ocupar consistentemente alrededor del 10-15%.

        *   **Menor Peso Porcentual:** Las demás ramas (Agropecuarias, Cultura Física, Naturales y Matemáticas, Artes) representan individualmente porcentajes menores del total de la matrícula, lo que es coherente con su menor volumen absoluto de estudiantes.

        Este análisis porcentual es crucial porque nos permite entender no solo cuántos estudiantes hay en cada rama, sino también cómo se distribuye el interés o la capacidad de admisión en relación con el conjunto del sistema universitario.
        """)
    else:
        st.warning("No se pudo generar el gráfico de distribución porcentual por rama (A2).")
        
    if msg_a2: # Si la función A2 retornó algún mensaje adicional
        st.caption(f"ℹ️ {msg_a2}")

def A3_analisis(df_main):
    st.header("🔍 Carreras Bajo la Lupa: Popularidad, Tendencias y Dinamismo")
    st.markdown("""
    Tras explorar las grandes ramas del saber, es momento de enfocar nuestra lente en las unidades
    fundamentales: las carreras universitarias. ¿Cuáles son las que capturan el mayor interés estudiantil?
    ¿Cómo ha sido su evolución individual? Y, muy importante, ¿cuáles muestran un crecimiento
    acelerado y cuáles parecen estar perdiendo impulso?
    """)
        
    # --- Subsección: El Podio de las Carreras ---
    st.subheader("🏆 El Podio de las Carreras: ¿Cuáles Lideran la Matrícula Actual?")
    st.markdown(f"""
    A la izquierda observamos el ranking de todas las carreras según su matrícula total en el curso más reciente
    ({df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1}). A la derecha, vemos la evolución histórica de la matrícula
    para las 10 carreras que actualmente se encuentran en la cima de este ranking.
    """)
    with st.spinner("Construyendo la gráfica A3, nos esforzamos para que reciba su gráfica cuanto antes...", show_time=True): # Eliminé df_main.copy()
        fig_a3_evolucion, df_ranking_completo_a3, _, msg_a3 = analisis_A3(df_main)
    # Nota: La función analisis_A3 fue modificada para retornar el ranking completo y la figura de evolución de las top N.
    
    col_ranking, col_evolucion_top = st.columns([1, 2]) # Ajusta la proporción si es necesario

    with col_ranking:
        if df_ranking_completo_a3 is not None and not df_ranking_completo_a3.empty:
            st.dataframe(df_ranking_completo_a3, height=500) # Muestra el ranking completo
        else:
            st.info("No hay datos de ranking de carreras para mostrar.")
    
    with col_evolucion_top:
        if fig_a3_evolucion:
            st.plotly_chart(fig_a3_evolucion, use_container_width=True, key="fig_a3_lupa_evolucion")
        else:
            st.info("No se generó gráfico de evolución para las carreras top actuales.")
    
    info_msg(msg_a3)

    st.markdown("""
    **Puntos Clave del Podio:**
    *   **Liderazgo Indiscutible:** **Medicina** se posiciona firmemente como la carrera con la mayor matrícula (35,889 estudiantes), una constante que ya habíamos vislumbrado al analizar las ramas del saber.
    *   **Fuerzas Significativas:** Le siguen **Cultura Física** (14,695) y **Educación Primaria** (12,867), demostrando una demanda considerable en estas áreas.
    *   **Top 5 Robusto:** **Enfermería** (9,999) y **Contabilidad y Finanzas** (9,883) completan el top 5, ambas con una matrícula muy cercana a los 10,000 estudiantes.
    *   **Evolución de las Líderes:** El gráfico de la derecha nos permite ver cómo estas carreras (y otras del top 10) han llegado a su posición actual. Observa cómo algunas han tenido un crecimiento más sostenido, mientras otras muestran picos y valles más pronunciados.
    """)
    st.markdown("---")

    # --- Subsección: El Ritmo del Cambio (CAGR) ---
    st.subheader("🚀 El Ritmo del Cambio: ¿Qué Carreras Despegan o Aterrizan?")
    st.markdown("""
    La **Tasa de Crecimiento Anual Compuesto (CAGR)** nos ofrece una perspectiva del dinamismo.
    Calcula el crecimiento (o decrecimiento) porcentual promedio de la matrícula de una carrera cada año,
    considerando todo el período analizado (2015-2024). Un CAGR alto sugiere una expansión rápida.
    """)
    with st.spinner("Construyendo la gráfica A6, los trabajadores están en horario de chismes...", show_time=True): # Eliminé df_main.copy()
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

    if msg_a6: st.caption(f"ℹ️ {msg_a6}")
    
    st.markdown("""
    **Reflexiones Estratégicas a partir de estos Ritmos:**
    *   Un **alto CAGR** no siempre significa una matrícula total masiva (podría ser una carrera pequeña creciendo rápido), pero sí indica una **tendencia positiva fuerte** que merece atención, ya sea para fomentar o para asegurar recursos.
    *   Un **CAGR bajo o negativo** en carreras importantes podría ser una señal para investigar las causas: ¿cambios en el mercado laboral, preferencias estudiantiles, oferta académica?
    *   Es crucial cruzar esta información de CAGR con la matrícula absoluta (del ranking) para obtener una imagen completa.
    """)

def A3_playground(df_main):
    B1(df_main)

def A4(df_main):
    pass

def B1(df):
        st.header("🔬 B1. Perfil Detallado de Carrera: Una Radiografía Completa")
        st.markdown("""
        Sumérgete en los detalles de la carrera que elijas. Descubre su evolución histórica de matrícula,
        incluyendo la composición por género, su tasa de crecimiento promedio en el período que definas,
        y un panorama de las universidades que la imparten actualmente. ¡Una visión 360º a tu alcance!
        """)

        todas_carreras_unicas = sorted(df['carrera'].unique())
        carrera_sel_b1 = st.selectbox(
            "Selecciona una Carrera para analizar su perfil:", 
            options=todas_carreras_unicas, 
            index=todas_carreras_unicas.index("MEDICINA") if "MEDICINA" in todas_carreras_unicas else 0,
            key="sel_carrera_b1_perfil_final"
        )

        if carrera_sel_b1:
            st.markdown("---")
            
            with st.spinner(f"Generando perfil para {carrera_sel_b1}..."):
                # Llamada a la función de análisis (ya no pasa años CAGR)
                fig_b1_evol_gen, df_evol_para_cagr_b1, df_unis_b1, datos_genero_ultimo_ano_b1, rama_b1, msg_b1 = analisis_perfil_carrera(
                    df.copy(), 
                    carrera_sel_b1
                )
            
            st.subheader(f"Perfil Integral de: {carrera_sel_b1}")
            st.markdown(f"**Rama de Ciencias:** {rama_b1}")
            info_msg(msg_b1) # Mostrar cualquier mensaje de la función

            # Mostrar el gráfico de evolución de matrícula y género primero
            if fig_b1_evol_gen:
                st.plotly_chart(fig_b1_evol_gen, use_container_width=True, key="fig_b1_perfil_evol_genero_final")
            else:
                st.warning("No se pudo generar el gráfico de evolución para esta carrera.")

            st.markdown("---") # Separador antes de los controles CAGR y otros gráficos

            # Controles para el CAGR (Slider) y muestra del CAGR
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
                    ano_inicio_cagr_sel = selected_years_cagr[0]
                    ano_fin_cagr_sel = selected_years_cagr[1]

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
            
            # Métricas de Género y Gráfico de Pastel
            col_b1_genero_metric, col_b1_genero_pie = st.columns([1,1]) # Dos columnas para esto

            with col_b1_genero_metric:
                st.markdown(f"**Composición de Género (Curso {df['Ano_Inicio_Curso'].max()}-{df['Ano_Inicio_Curso'].max()+1}):**")
                if datos_genero_ultimo_ano_b1 and datos_genero_ultimo_ano_b1.get('Total', 0) > 0:
                    porc_mujeres = (datos_genero_ultimo_ano_b1['Mujeres'] / datos_genero_ultimo_ano_b1['Total']) * 100
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
            # Gráfico de Barras para Universidades
            if df_unis_b1 is not None and not df_unis_b1.empty:
                st.markdown(f"**Universidades que imparten '{carrera_sel_b1}' (Matrícula en último curso):**")
                df_unis_b1_sorted = df_unis_b1.sort_values(by=f'Matrícula {df["Ano_Inicio_Curso"].max()}-{df["Ano_Inicio_Curso"].max()+1}', ascending=True)
                fig_bar_unis = px.bar(
                    df_unis_b1_sorted, 
                    x=f'Matrícula {df["Ano_Inicio_Curso"].max()}-{df["Ano_Inicio_Curso"].max()+1}', 
                    y='Universidad', 
                    orientation='h',
                    title=f"Distribución por Universidad: {carrera_sel_b1}",
                    height=max(300, len(df_unis_b1_sorted) * 30) # Altura dinámica
                )
                fig_bar_unis.update_layout(yaxis_title="Universidad", xaxis_title="Matrícula")
                st.plotly_chart(fig_bar_unis, use_container_width=True, key="fig_b1_bar_unis_final")
            elif df_unis_b1 is not None and df_unis_b1.empty:
                 st.info(f"Ninguna universidad registró matrícula para '{carrera_sel_b1}' en el último curso.")
            else:
                st.info("No se encontraron datos de universidades para esta carrera en el último año.")
        else:
            st.info("Por favor, selecciona una Carrera para continuar.")

def B2(df_main, df_ins):
        st.header("🗺️ B2. Guía de Instituciones: Explora la Oferta Académica por Localidad")
        st.markdown("""
        Descubre las instituciones de educación superior en Cuba, filtrando por provincia y municipio.
        Para cada universidad, encontrarás información general, su composición de género, las ramas de ciencias
        que ofrece y las carreras disponibles con su matrícula en el último año académico registrado.
        """)

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
                    disabled=(provincia_sel_b2 == "TODAS LAS PROVINCIAS" and len(municipios_disponibles_filtrados_b2) <=1)
                )
                #Usar un cuadro para escribir parte del nombre a buscar:
            pattern_sel_b2 = st.text_input(
                        "Buscar por nombre o info de institución (opcional):",
                        value="",
                        autocomplete="on",
                        key="sel_patron_b2",
                        disabled=  len(municipios_disponibles_filtrados_b2) > 1 
            )
            st.markdown("---")

            with st.spinner(f"Cargando guía de instituciones... Obreros ocupados..."):
                municipio_a_pasar = None
                if provincia_sel_b2 != "TODAS LAS PROVINCIAS" and municipio_sel_b2 != "TODOS LOS MUNICIPIOS":
                    municipio_a_pasar = municipio_sel_b2
                
                guia_data_b2, msg_b2 = analisis_guia_universidades(
                    df_ins, df_main, 
                    provincia_seleccionada=provincia_sel_b2,
                    municipio_seleccionado=municipio_a_pasar)
            info_msg(msg_b2)

            if guia_data_b2:
                st.markdown(f"**Mostrando {len(guia_data_b2)} institución(es) según los filtros aplicados:**")
                for nombre_uni, data_uni in guia_data_b2.items():

                    titulo_expander = f"🏛️ {nombre_uni} ({data_uni['sigla']})" # ... (título como antes) ...
                    if pattern_sel_b2 and pattern_sel_b2.lower() not in titulo_expander.lower():
                        continue
                    detalles_loc_exp = []
                    if data_uni.get('municipio') and data_uni['municipio'] != 'N/D': detalles_loc_exp.append(data_uni['municipio'])
                    if data_uni.get('provincia') and data_uni['provincia'] != 'N/D': detalles_loc_exp.append(data_uni['provincia'])
                    if detalles_loc_exp: titulo_expander += f" | {', '.join(detalles_loc_exp)}"
                    if data_uni.get('ano_creacion') and pd.notna(data_uni['ano_creacion']): 
                        titulo_expander += f" (Fundada en {int(data_uni['ano_creacion'])})"
                    
                    with st.expander(titulo_expander):
                        # --- Columnas para información básica y gráfico de pastel de género ---
                        col_info_basica, col_genero_pastel_uni = st.columns([2,1]) # Dar más espacio a la info básica

                        with col_info_basica:
                            st.markdown(f"**Organismo:** `{data_uni.get('organismo', 'N/D')}`")
                            st.markdown(f"**Dirección:** *{data_uni.get('direccion', 'N/D')}*")
                            st.markdown(f"**Modalidad Principal:** `{data_uni.get('modalidad_estudio', 'N/D')}`")
                        
                        with col_genero_pastel_uni:
                            datos_genero = data_uni.get("datos_genero_uni")
                            if datos_genero and datos_genero.get('Total', 0) > 0:
                                df_pie_genero_uni = pd.DataFrame({
                                    'Género': ['Mujeres', 'Hombres'],
                                    'Cantidad': [datos_genero['Mujeres'], datos_genero['Hombres']]
                                })
                                fig_pie_genero_uni = px.pie(df_pie_genero_uni, values='Cantidad', names='Género', 
                                                        title=f"Género Total ({df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1})",
                                                        color_discrete_map={'Mujeres':'orchid', 'Hombres':'royalblue'},
                                                        height=250) # Gráfico compacto
                                fig_pie_genero_uni.update_layout(margin=dict(t=30, b=0, l=0, r=0), showlegend=False)
                                fig_pie_genero_uni.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig_pie_genero_uni, use_container_width=True)
                            else:
                                st.caption("Sin datos de género disponibles para el último año.")
                        
                        st.markdown("---")
                        if data_uni["ramas_ofertadas"]:
                            st.markdown("**Oferta Académica (Ramas y Carreras con matrícula en último año):**")
                            for rama_info in data_uni["ramas_ofertadas"]:
                                with st.container(): # Contenedor para cada rama
                                    st.markdown(f"##### <span style='color: #1E90FF;'>►</span> {rama_info['nombre_rama']}", unsafe_allow_html=True)
                                    if rama_info["carreras"]:
                                        df_carreras_rama = pd.DataFrame(rama_info["carreras"])
                                        df_carreras_rama.rename(columns={
                                            'nombre_carrera': 'Carrera',
                                            'matricula_ultimo_ano': 'Matrícula' # Más corto
                                        }, inplace=True)
                                        st.dataframe(df_carreras_rama.set_index('Carrera'))
                                    else:
                                        st.caption("  ↳ *Esta rama está indicada como ofertada, pero no se encontraron carreras con matrícula en el último año.*")
                                    #st.markdown("---")
                        else:
                            st.info("Esta institución no tiene ramas de ciencias con oferta activa o carreras con matrícula reportada...")
            # ... (resto del manejo de errores como antes) ...
            elif provincia_sel_b2 and provincia_sel_b2 != "TODAS LAS PROVINCIAS":
                st.info(f"No se encontraron instituciones para la provincia de '{provincia_sel_b2}'" + 
                        (f" y el municipio de '{municipio_sel_b2}'" if municipio_sel_b2 and municipio_sel_b2 != "TODOS LOS MUNICIPIOS" else "") +
                        " que cumplan los criterios.")
            else:
                st.info("No hay instituciones para mostrar con los filtros actuales, o no hay datos de instituciones cargados.")






