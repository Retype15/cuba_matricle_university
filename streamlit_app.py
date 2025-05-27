from functions import *

# --- Configuración de la Página de Streamlit ---
st.set_page_config(layout="wide", page_title="Análisis Matrícula Universitaria Cuba", page_icon="🎓")

df_main = cargar_datos_streamlit()

# Almacenar figuras cacheadas si es necesario para "Mirando al Futuro"
# Esto se haría si las funciones son muy costosas y el df_main no cambia
# Por ahora, las llamaremos de nuevo.

if df_main.empty:
    st.error("Error crítico: No se pudieron cargar los datos ('db_long.csv'). La aplicación no puede continuar.")
else:
    st.title("🎓 Análisis Estratégico de la Matrícula Universitaria en Cuba")
    st.image("UH.jpg", caption="Universidad de La Habana. Un símbolo de la educación superior en Cuba.", use_container_width=True)
    st.markdown("Un viaje a través de los datos (2015-2025) para iluminar el camino de la Educación Superior.")
    st.markdown("---")

    # --- Navegación ---
    st.sidebar.header("🧭 Explorador del Análisis")
    opciones_sidebar = ("Introducción", "1. Pulso Nacional", "2. Mosaico de Saberes",
                        "3. Carreras Bajo la Lupa", "4. Perspectiva de Género", 
                        "5. Universidades: Fortalezas y Focos",
                        "6. Mirando al Mañana (Proyecciones)", 
                        "7. Áreas de Atención", "Conclusiones Finales")
    
    # Estado para la sección actual
    if 'current_section_index' not in st.session_state:
        st.session_state.current_section_index = 0

    seccion_actual = opciones_sidebar[st.session_state.current_section_index]
    
    # Radio buttons en el sidebar para selección directa
    seleccion_sidebar = st.sidebar.radio("Elige una sección:", options=opciones_sidebar, 
                                         index=st.session_state.current_section_index, key="radio_nav")
    
    # Si la selección del radio cambia, actualizamos el índice
    if opciones_sidebar.index(seleccion_sidebar) != st.session_state.current_section_index:
        st.session_state.current_section_index = opciones_sidebar.index(seleccion_sidebar)
        seccion_actual = opciones_sidebar[st.session_state.current_section_index]
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info("Análisis basado en datos de matrícula del período 2015-16 a 2024-25.\n\n -- ⚠️ No incluye el curso 2018-2019 por falta de datos en dicho curso, los análisis se realizan obviando este curso.")

    # --- Contenido por Sección ---
    
    # Placeholder para mensajes de las funciones de análisis
    def mostrar_mensaje(msg):
        if msg: st.caption(f"ℹ️ {msg}")

    if seccion_actual == "Introducción":
        st.header("🎯 Bienvenidos al Corazón de la Educación Superior Cubana")
        st.markdown("""
        La universidad no es solo un edificio; es un crisol de sueños, un motor de progreso y un reflejo
        de las aspiraciones de una sociedad. En este espacio, nos embarcaremos en un viaje analítico,
        explorando las corrientes que moldean la matrícula universitaria en Cuba. 
        
        Desde las tendencias generales hasta el detalle de cada carrera y universidad, desentrañaremos
        historias ocultas en los números. ¿El objetivo? Proveer una brújula basada en evidencia para
        la toma de decisiones estratégicas, fomentando un sistema de educación superior más fuerte,
        equitativo y alineado con el futuro de la nación.

        **Utiliza el explorador en el panel lateral para navegar por las distintas secciones.** 
        ¡Que comience el descubrimiento!
        """)
        st.success("¡Tu viaje comienza aquí! Selecciona una sección en el menú lateral o usa el botón 'Siguiente'.")

    elif seccion_actual == "1. Pulso Nacional":
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

    elif seccion_actual == "2. Mosaico de Saberes":
        st.header("📚 Un Mosaico de Saberes: ¿Hacia Dónde se Inclinan los Futuros Profesionales?")
        st.markdown("""
        La universidad es un vasto jardín donde florecen diversas disciplinas. Cada rama del conocimiento,
        desde las Ciencias Médicas hasta las Artes, representa un camino único de formación y contribución
        a la sociedad. En esta sección, desglosamos la matrícula total para ver cómo se distribuyen
        los estudiantes entre estas grandes áreas. ¿Hay protagonistas claros? ¿Cómo ha danzado el interés
        estudiantil a lo largo de la última década?
        """)
        
        # Llamamos a la función de análisis A2, solicitando solo la evolución histórica
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

    elif seccion_actual == "3. Carreras Bajo la Lupa":
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

        fig_a3_evolucion, df_ranking_completo_a3, _, msg_a3 = analisis_A3( df_main)
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
        
        if msg_a3: st.caption(f"ℹ️ {msg_a3}")

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
        
        fig_a6_top_cagr, fig_a6_bottom_cagr, msg_a6 = analisis_A6( df_main)
        
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

# --- SECCIÓN 4: PERSPECTIVA DE GÉNERO ---

    elif seccion_actual == "4. Perspectiva de Género":
        st.header("♀️♂️ Equilibrando la Balanza: Una Mirada a la Perspectiva de Género")
        st.markdown("""
        La universidad no solo forma profesionales, sino que también moldea una sociedad más justa y equitativa.
        En esta sección, nos adentramos en la composición de género de la matrícula universitaria.
        ¿Existe un equilibrio entre hombres y mujeres en las aulas? ¿Hay áreas del conocimiento
        tradicionalmente asociadas a un género que mantienen esos patrones, o estamos presenciando
        una transformación hacia una mayor paridad? Acompáñanos a descubrirlo.
        """)
        
        fig_a4_ramas, fig_a4_carreras, msg_a4 = analisis_A4( df_main)
        
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
        else:
            st.warning("No se pudo generar el gráfico de género por ramas.")
            if msg_a4: st.caption(f"ℹ️ {msg_a4}") # Mostrar mensaje si existe aunque no haya gráfico

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
        else:
            st.warning("No se pudo generar el gráfico de género por carreras.")
            # Mostrar msg_a4 aquí también si el primer gráfico falló pero este no, o si msg_a4 es general.
            if msg_a4 and not fig_a4_ramas: st.caption(f"ℹ️ {msg_a4}")
        
        st.markdown("""
        ---
        **Reflexiones para la Acción:**
        *   La alta feminización en ciertas ramas y carreras es un fenómeno consolidado. Si bien refleja vocaciones, también es importante asegurar que no existan barreras implícitas o desincentivos para la participación masculina en ellas.
        *   El mayor desafío para la equidad de género se encuentra claramente en las **Ciencias Técnicas** y en varias ingenierías específicas, así como en **Ciencias de la Cultura Física y el Deporte**. Se requieren estrategias continuas y efectivas para atraer y retener a más mujeres en estos campos cruciales para el desarrollo tecnológico y social.
        *   Estos datos son una invitación a profundizar: ¿Cuáles son las causas de estos desbalances? ¿Cómo podemos inspirar a las nuevas generaciones a explorar todas las áreas del conocimiento sin sesgos de género?
        """)

# --- SECCIÓN 5: EL ROL DE LAS UNIVERSIDADES (DENTRO DEL BLOQUE if/elif DE STREAMLIT) ---

    elif seccion_actual == "5. Universidades: Fortalezas y Focos":
        st.header("🏛️ Universidades en Perspectiva: Descubriendo Fortalezas y Focos de Especialización")
        st.markdown("""
        Cada universidad es un ecosistema único con su propia historia, vocación y áreas de excelencia.
        En esta sección, cambiamos nuestra perspectiva para analizar cómo se distribuye el talento estudiantil
        a nivel institucional. ¿Qué universidades concentran la mayor cantidad de estudiantes?
        ¿Existen centros altamente especializados en ciertas ramas o carreras? ¿Y qué carreras
        son joyas raras, ofrecidas solo por unas pocas instituciones?
        """)
        
        fig_a5_treemap, df_carreras_unicas_a5, msg_a5 = analisis_A5( df_main)
        
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
        else:
            st.warning("No se pudo generar el treemap de distribución.")
            if msg_a5: st.caption(f"ℹ️ {msg_a5}")

        if df_carreras_unicas_a5 is not None and not df_carreras_unicas_a5.empty:
            st.subheader("Joyas Académicas: Carreras con Oferta Limitada")
            st.markdown(f"Listado de carreras y el número de universidades que las impartieron con matrícula en el curso {df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1}, ordenadas de menor a mayor número de oferentes.")
            st.dataframe(df_carreras_unicas_a5, height=350) # Muestra todas
            st.markdown("""
            *   Las carreras en la parte superior de esta lista son ofrecidas por muy pocas instituciones, lo que puede indicar una alta especialización, una nueva oferta en expansión, o la necesidad de evaluar si su alcance geográfico es adecuado para la demanda potencial.
            """)
        else:
            # Mostrar mensaje de msg_a5 si existe, incluso si df_carreras_unicas_a5 está vacío pero se intentó generar
            if msg_a5 and not fig_a5_treemap : st.caption(f"ℹ️ {msg_a5}")
            
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
            else: # Fallback si no hay datos o nlargest no devuelve nada
                default_carreras_a9 = todas_carreras_sorted[:min(2, len(todas_carreras_sorted))]


        carreras_seleccionadas_a9 = st.multiselect(
            "Carreras para comparar evoluciones por universidad:", 
            options=todas_carreras_sorted,
            default=default_carreras_a9, 
            max_selections=3, 
            key="select_carreras_a9_unis"
        )
        
        if carreras_seleccionadas_a9:
            fig_a9, msg_a9 = analisis_A9( df_main, carreras_a_comparar=carreras_seleccionadas_a9)
            
            if fig_a9:
                st.plotly_chart(fig_a9, use_container_width=True, key="fig_a9_comparativa_unis")
                if msg_a9: st.caption(f"ℹ️ {msg_a9}")
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

# --- SECCIÓN 6: MIRANDO AL MAÑANA (PROYECCIONES) (DENTRO DEL BLOQUE if/elif DE STREAMLIT) ---

    elif seccion_actual == "6. Mirando al Mañana (Proyecciones)":
        st.header("🔭 Mirando al Mañana: ¿Qué Podríamos Esperar? (Proyecciones)")
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

        # --- Proyección Nacional ---
        st.subheader(" Horizonte Nacional: Proyección de la Matrícula Total")
        fig_a1_proy, msg_a1_proy = analisis_A1( df_main, incluir_proyeccion=True) 
        if fig_a1_proy:
            st.plotly_chart(fig_a1_proy, use_container_width=True, key="fig_a1_futuro_proy_sec6") # Key única
            st.markdown("""
            **Interpretando la Tendencia Nacional Proyectada:**
            *   Partiendo de la matrícula del curso 2024-2025 (alrededor de **205,000 estudiantes**), la proyección basada en la tendencia de los últimos seis años sugiere una **continuación de la fase de ajuste o declive moderado**.
            *   Para el curso **2025-2026**, el modelo estima una matrícula que podría rondar los **195,000-200,000 estudiantes**.
            *   Hacia **2026-2027**, esta cifra podría situarse cerca de los **185,000-190,000 estudiantes**.
            *   **Reflexión:** Si esta tendencia se materializa, ¿qué implicaciones tendría para la capacidad instalada, la asignación de recursos y las estrategias de captación a nivel nacional?
            """)
            if msg_a1_proy: st.caption(f"ℹ️ Detalles del modelo: {msg_a1_proy}")
        else:
            st.warning(msg_a1_proy if msg_a1_proy else "No se pudo generar la proyección nacional.")
        st.markdown("---")

        # --- Proyección por Rama de Ciencias ---
        st.subheader(" Mosaico de Saberes del Mañana: Proyección por Rama de Ciencias")
        fig_a2_abs_proy, _, msg_a2_proy = analisis_A2( df_main, incluir_proyeccion=True) 
        if fig_a2_abs_proy:
            st.plotly_chart(fig_a2_abs_proy, use_container_width=True, key="fig_a2_abs_futuro_proy_sec6") # Key única
            st.markdown("""
            **Dinámicas Proyectadas en las Áreas del Conocimiento:**
            Observando las líneas discontinuas para cada rama:
            *   **Ciencias Médicas:** A pesar de su descenso reciente desde el pico, la proyección sugiere que podrían estabilizarse o continuar un declive más suave, manteniéndose como la rama más numerosa, posiblemente entre **55,000 y 65,000 estudiantes** en los próximos dos años.
            *   **Ciencias Pedagógicas:** La fuerte caída reciente parece influir en su proyección, que apunta a una continuación de esta tendencia, situándose entre **35,000 y 40,000 estudiantes**.
            *   **Ramas Intermedias (Técnicas, Sociales, Económicas):** Estas ramas, que ya mostraban un declive, podrían continuar esa trayectoria de forma moderada. Por ejemplo, las Ciencias Técnicas y Sociales podrían moverse hacia los **15,000-20,000 estudiantes** cada una.
            *   **Ramas Menores:** Aquellas con menor volumen (Agropecuarias, Cultura Física, Naturales, Artes) probablemente mantendrán matrículas comparativamente bajas, con proyecciones que siguen sus tendencias recientes, algunas de ellas también a la baja.
            *   **Consideración Clave:** La suma de estas proyecciones individuales por rama debería aproximarse a la proyección nacional total, pero pequeñas discrepancias pueden surgir debido a que cada modelo se ajusta independientemente.
            """)
            if msg_a2_proy: st.caption(f"ℹ️ {msg_a2_proy}")
        else:
            st.warning(msg_a2_proy if msg_a2_proy else "No se pudo generar la proyección por ramas.")
        st.markdown("---")

        # --- Proyección por Carreras Seleccionadas (CON SELECTOR) ---
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
            fig_a7_proy, msg_a7_proy = analisis_A7( df_main, carreras_seleccionadas=carreras_seleccionadas_a7)
            if fig_a7_proy:
                st.plotly_chart(fig_a7_proy, use_container_width=True, key="fig_a7_futuro_proy_dinamica") # Key única
                st.markdown(f"""
                **Posibles Escenarios para las Carreras Seleccionadas ({', '.join(carreras_seleccionadas_a7)}):**
                *   Observa las líneas discontinuas para cada una de las carreras que elegiste. ¿Qué tendencia general muestran?
                *   ¿Alguna de ellas parece tener una proyección de crecimiento, estabilidad o declive más marcada?
                *   **Implicaciones:** Estas proyecciones individuales son cruciales. Un descenso proyectado en una carrera de alta demanda, por ejemplo, requeriría un análisis profundo de sus causas y posibles impactos.
                """)
                if msg_a7_proy: st.caption(f"ℹ️ Detalles de los modelos: {msg_a7_proy}")
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

# --- SECCIÓN 7: ÁREAS DE ATENCIÓN (DENTRO DEL BLOQUE if/elif DE STREAMLIT) ---

    elif seccion_actual == "7. Áreas de Atención":
        st.header("💡 Áreas de Atención: Identificando Desafíos y Oportunidades Específicas")
        st.markdown("""
        Más allá de las grandes tendencias, existen situaciones particulares en carreras y universidades
        que merecen una lupa especial. Algunas carreras pueden estar emergiendo con vigor, otras podrían
        haber concluido su ciclo de oferta, y un tercer grupo quizás lucha por atraer un número suficiente
        de estudiantes. Identificar estos casos no es señalar problemas, sino descubrir oportunidades
        para una gestión académica más precisa, ágil y adaptada a las realidades cambiantes.
        """)
        
        resultados_a8, msg_a8 = analisis_A8(df_main)
        
        if msg_a8: # Mostrar cualquier mensaje general de la función
             st.caption(f"ℹ️ {msg_a8}")

        if resultados_a8:
            # --- Subsección: Nuevas Ofertas o Reactivaciones ---
            st.subheader("🌱 Sembrando el Futuro: Posibles Nuevas Ofertas o Reactivaciones")
            st.markdown("""
            Aquí listamos carreras que no registraban matrícula en los primeros años del período analizado (2015-16),
            pero que sí la tienen en cursos más recientes y en el último año registrado. Esto podría indicar
            el lanzamiento de nuevas carreras o la reactivación de algunas que estuvieron en pausa.
            """)
            df_nuevas = resultados_a8.get("nuevas_ofertas")
            if df_nuevas is not None and not df_nuevas.empty:
                st.dataframe(df_nuevas) # Mostrar todas las detectadas
                st.markdown(f"*Se detectaron **{len(df_nuevas)}** casos que cumplen este criterio.*")
            else:
                st.info("No se identificaron carreras que cumplan claramente con el criterio de 'nueva oferta reciente' en el período analizado.")
            st.markdown("---")

            # --- Subsección: Posibles Ceses de Oferta ---
            st.subheader("🍂 Ciclos que Concluyen: Posibles Casos de Oferta")
            st.markdown("""
            Presentamos carreras que contaban con matrícula al inicio del período de análisis pero que
            no registran estudiantes en los últimos cursos. Esto podría sugerir una discontinuación
            planificada o una interrupción que requiere verificación.
            """)
            df_cesadas = resultados_a8.get("cesadas_ofertas")
            if df_cesadas is not None and not df_cesadas.empty:
                st.dataframe(df_cesadas) # Mostrar todas las detectadas
                st.markdown(f"*Se detectaron **{len(df_cesadas)}** casos que cumplen este criterio.*")
            else:
                st.info("No se identificaron carreras que cumplan claramente con el criterio de 'cese de oferta reciente'.")
            st.markdown("---")
            
            # --- Subsección: Matrícula Reducida ---
            df_baja = resultados_a8.get("baja_matricula")
            umbral = resultados_a8.get("umbral_bajo", 10) # Obtener umbral usado en A8
            st.subheader(f"📉 Focos de Atención: Carreras con Matrícula Reducida (Inferior a {umbral} Estudiantes)")
            st.markdown(f"""
            Finalmente, listamos aquellas carreras que, en el último curso académico registrado
            ({df_main['Ano_Inicio_Curso'].max()}-{df_main['Ano_Inicio_Curso'].max()+1}), tuvieron una matrícula activa (mayor que cero)
            pero inferior a **{umbral} estudiantes**. Estas situaciones pueden tener diversas explicaciones
            y ameritan un análisis particularizado.
            """)
            if df_baja is not None and not df_baja.empty:
                st.dataframe(df_baja) # Mostrar todas las detectadas
                st.markdown(f"*Se detectaron **{len(df_baja)}** casos con matrícula inferior a {umbral} (y >0) en el último año.*")
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

# --- SECCIÓN DE CONCLUSIONES FINALES (DENTRO DEL BLOQUE if/elif DE STREAMLIT) ---

    elif seccion_actual == "Conclusiones Finales":
        st.header("🏁 Conclusiones y Horizontes Futuros: Forjando la Universidad del Mañana")
        st.markdown("""
        Hemos viajado a través de una década de datos, explorando el vibrante y complejo ecosistema
        de la educación superior en Cuba. Donde cada gráfico nos ha contado
        una parte de una historia más grande: la historia de miles de aspiraciones, de esfuerzos institucionales
        y de la incesante búsqueda del conocimiento que define a nuestra nación.

        Este análisis no es un punto final, sino un faro que ilumina el camino recorrido y nos ayuda
        a discernir los senderos que se abren ante nosotros.
        """)
        st.success(
            "**La información es poder, y el poder de estos datos reside en nuestra capacidad para transformarlos en acción sabia y visión estratégica.**"
        )
        st.markdown("---")

        st.subheader("🌟 Destellos del Viaje: Principales Hallazgos que Resuenan")
        st.markdown("""
        Al mirar atrás en nuestro análisis, emergen varios faros que guían nuestra comprensión:

        1.  **El Pulso Dinámico de la Nación:** La matrícula universitaria nacional ha mostrado una notable capacidad de expansión, alcanzando picos significativos a principios de la década de 2020, seguida de una fase de ajuste más reciente. Esta fluctuación nos recuerda la sensibilidad del sistema a factores contextuales y la necesidad de una planificación flexible. *(Ref. Sección 1)*

        2.  **El Corazón Médico y el Alma Pedagógica:** Las **Ciencias Médicas** se consolidan como la columna vertebral en términos de volumen estudiantil, un testimonio de su importancia estratégica. Las **Ciencias Pedagógicas**, por su parte, han demostrado un dinamismo extraordinario, con un crecimiento masivo seguido de una contracción, reflejando posibles cambios en la demanda o en las políticas de formación docente. *(Ref. Sección 2)*

        3.  **El Ascenso de Nuevas Vocaciones:** El análisis de crecimiento (CAGR) ha revelado el despegue impresionante de carreras como **Servicios Estomatológicos** y el vigor de varias **Ingenierías** (Artística, Procesos Agroindustriales, Informática), señalando posibles nuevas fronteras de interés y demanda laboral. *(Ref. Sección 3)*

        4.  **Avances y Desafíos en la Equidad de Género:** Si bien Cuba exhibe una alta participación femenina en la educación superior, con muchas ramas y carreras mostrando una mayoría de mujeres, persisten desafíos significativos. La subrepresentación femenina en las **Ciencias Técnicas** e **Ingenierías específicas**, así como en **Ciencias de la Cultura Física y el Deporte**, nos llama a redoblar esfuerzos para construir un panorama verdaderamente equitativo. *(Ref. Sección 4)*

        5.  **La Riqueza de la Diversidad Institucional:** Cada universidad aporta su matiz único al sistema. Hemos visto desde grandes centros multidisciplinarios hasta instituciones con una marcada especialización (como las Universidades de Ciencias Médicas). La identificación de carreras con oferta limitada subraya la importancia de una red universitaria coordinada y estratégicamente distribuida. *(Ref. Sección 5)*

        6.  **Una Mirada Prudente al Mañana:** Las proyecciones, aunque sujetas a la incertidumbre inherente al futuro, sugieren una posible continuación de la fase de ajuste en la matrícula general y en varias ramas y carreras clave. Esto no es un augurio, sino una invitación a la preparación y a la acción proactiva. *(Ref. Sección 6)*

        7.  **La Importancia de los Detalles:** El análisis de "Áreas de Atención" nos ha recordado que la salud del sistema también reside en la vitalidad de cada uno de sus componentes, incluyendo las carreras emergentes, aquellas con matrícula reducida o las que podrían estar concluyendo su ciclo. *(Ref. Sección 7)*
        """)
        st.markdown("---")

        st.subheader("🧭 Trazando la Carta de Navegación: Recomendaciones Estratégicas")
        st.markdown("""
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
        """)
        st.markdown("---")
        
        st.header("✨ Un Legado Continuo, Un Futuro Brillante")
        st.markdown("""
        El análisis de estos datos no es meramente un ejercicio académico; es un acto de responsabilidad
        y un compromiso con el futuro. La Universidad Cubana, con su rica historia y su papel trascendental
        en la sociedad, tiene ante sí el desafío y la oportunidad de seguir evolucionando, adaptándose
        e innovando.

        Que la luz que emana de estos datos nos inspire a todos a trabajar juntos por una educación
        superior que no solo responda a las necesidades del presente, sino que activamente modele
        un mañana más próspero, justo y lleno de conocimiento para Cuba.
        """)
        st.balloons()

    # --- Botones de Navegación Siguiente/Anterior ---
    col_nav_1, col_nav_2, col_nav_3 = st.columns([1,1,1])

    with col_nav_1:
        if st.session_state.current_section_index > 0:
            if st.button("⬅️ Sección Anterior", key="btn_anterior"):
                st.session_state.current_section_index -= 1
                st.rerun()
    
    with col_nav_3:
        if st.session_state.current_section_index < len(opciones_sidebar) - 1:
            if st.button("Siguiente Sección ➡️", key="btn_siguiente"):
                st.session_state.current_section_index += 1
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado como parte de un proyecto de análisis de datos.")