from .ai_functions import ask_ai_component
from .plot_functions import *
from .Gamification import *

def show_info(msg):
    if msg: st.caption(f"ℹ️ {msg}")

### Testeando las funciones del motor de juego, si algo falla es culpa tuya por andar tocando xd (es broma, nada va a fallar aquí : ) )
### Introduccion del miembro
@st.fragment
def introduction(df_main, game_controller: GameController, ts:Translator, **kwargs):
    if 'initial_mode_selected' not in st.session_state:
        st.session_state.initial_mode_selected = False
    #st.table(df_main.head(10))
    st.header(ts.translate('introduction_header', "🎯 Bienvenidos al Corazón de la Educación Superior Cubana"))
    st.markdown(ts.translate('introduction_markdown_1', """
        La universidad no es solo un edificio; es un crisol de sueños, un motor de progreso y un reflejo de las aspiraciones de una sociedad. En este espacio, nos embarcaremos en un viaje analítico, explorando las corrientes que moldean la matrícula universitaria en Cuba.

        Desde las tendencias generales hasta el detalle de cada carrera y universidad, desentrañaremos las historias ocultas detrás de las distintas universidades del país. ¿El objetivo? Proveer una brújula basada en evidencia para la toma de decisiones estratégicas, fomentando un sistema de educación superior más fuerte, equitativo y alineado con el futuro de la nación.
    """))
    st.markdown("---")

    if not st.session_state.initial_mode_selected:
        st.subheader(ts.translate('intro_choose_your_path_header', "🛣️ Elige tu Camino: ¿Cómo Quieres Explorar?"))
        st.markdown(ts.translate('intro_choose_your_path_text', """
            Este viaje a través de los datos puede tomar dos rutas. Elige la que mejor se adapte a tu estilo.
        """))

        col1, col2 = st.columns(2, gap="large")

        with col1:
            with st.container(border=True):
                st.markdown(f"### {ts.translate('intro_analyst_path_title', '👨‍🏫 La Ruta del Analista')}")
                st.markdown(ts.translate('intro_analyst_path_desc', """
                    Ideal si buscas ir directo al grano. Accede a todos los gráficos y análisis de forma
                    directa, sin interrupciones. Perfecto para una exploración rápida y enfocada.
                """))
                if st.button(ts.translate('intro_analyst_path_button', "Activar Modo Análisis"), use_container_width=True):
                    game_controller.switch_off()
                    st.session_state.initial_mode_selected = True

                    st.rerun()

        with col2:
            with st.container(border=True):
                st.markdown(f"### {ts.translate('intro_explorer_path_title', '🎮 La Senda del Explorador')}")
                st.markdown(ts.translate('intro_explorer_path_desc', """
                    Convierte el análisis en un desafío. En cada sección, te enfrentarás a minijuegos para
                    poner a prueba tu intuición sobre los datos antes de verlos. ¡Gana puntos y compite!
                """))
                #st.warning("WARNING: Work in progress... Not finished yet.") # TODO: REVISAR Y QUITAR CUANDO SE TERMINE DE PROGRAMAR LOS MINIJUEGOS A CADA ANALISIS...
                if st.button(ts.translate('intro_explorer_path_button', "Activar Modo Juego"), use_container_width=True, type="primary"):
                    game_controller.switch_on()
                    st.session_state.initial_mode_selected = True
                    st.rerun()

    else:
        if game_controller.game_mode:
            st.info(ts.translate('intro_game_mode_active_info', "🕹️ ¡**Modo Juego Activado!** Prepárate para los desafíos. Puedes ver tu progreso si presionas el botón '🏆' que aparece en la esquina inferior derecha."), icon="🏆")
        else:
            st.info(ts.translate('intro_analysis_mode_active_info', "📊 **Modo Análisis Activado.** Estás listo para una exploración directa de los datos. Puedes cambiar de modo en cualquier momento en la barra lateral."), icon="📈")

    st.markdown("---")
    st.success(ts.translate('introduction_sucess', "¡Tu viaje comienza aquí! Selecciona una sección en el menú lateral o usa el botón 'Siguiente'."))

### Pulso Nacional
@st.fragment
def A1(df_main, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('A1_header', "🌍 El Pulso Nacional: ¿Cómo Late la Matrícula Universitaria?"))
    st.markdown(
        ts.translate(
            key='A1_markdown_1',
            default=
            """
            Imagina que podemos tomarle el pulso a todo el sistema universitario cubano a lo largo de una década.
            ¿Cómo ha sido su ritmo? ¿Ha experimentado momentos de vigoroso crecimiento, períodos de estabilidad,
            o quizás fases donde el latido se ha vuelto más pausado?

            Esta primera sección nos ofrece una vista panorámica de la matrícula total a nivel nacional,
            permitiéndonos identificar las grandes tendencias que han marcado el sistema de educación superior
            en los últimos años. Es nuestro punto de partida para entender el contexto general antes de
            sumergirnos en análisis más específicos.
            """
        )
    )

    def render_analysis_content():
        with st.spinner(ts.translate('A1_spinner_1', "Construyendo la gráfica A1, por favor espere...")):
            df_historico, _, msg_code, _ = analisis_A1(df_main)

        if msg_code != "success_historical_only" or df_historico is None:
            st.warning(ts.translate('generic_warn_figs', "No se pudo generar el gráfico del panorama nacional (A1)."))
            return
        
        fig_a1 = graficate_A1(df_historico, ts)
        st.plotly_chart(fig_a1, use_container_width=True, key="fig_a1_pulso_nacional")
        
        st.subheader(ts.translate('A1_fig_1_subheader',"Descifrando el Ritmo de la Década (2015-2025):"))
        st.markdown(ts.translate(
            key='A1_fig_1_markdown_1',
            default="""
            Observando la trayectoria de la matrícula nacional total en el gráfico superior, podemos identificar varias fases clave:

            *   **Impulso Inicial (2015-16 a 2016-17):** El viaje comienza en el curso 2015-2016 con una cifra que ronda los **165,000 estudiantes**. El año siguiente muestra un ligero aumento, estableciendo una base sólida para el crecimiento que vendrá.

            *   **Crecimiento Sostenido hacia la Cima (2017-18 a 2020-21):** A partir del curso 2017-18, y a pesar de la falta de datos para 2018-19, la tendencia ascendente se retoma con fuerza hasta alcanzar su **punto más álgido en el curso 2020-2021, superando los 285,000 estudiantes**. Este período representa la fase de mayor expansión de la matrícula en la década.

            *   **Meseta y Comienzo del Declive (2021-22 a 2022-23):** El curso 2021-2022 muestra una ligera contracción respecto al pico, marcando el inicio de una nueva fase. La matrícula se mantiene alta pero ya no crece, y para 2022-23, el descenso se hace más evidente.

            *   **Ajuste Reciente (2023-24 a 2024-25):** Los dos últimos cursos registrados muestran una **continuación de la tendencia descendente**, con la matrícula total situándose en torno a los **205,000 estudiantes** en el período más reciente. Esto sugiere un reajuste del sistema tras el pico de expansión.
            """
        ))
        
        context_ai_text = ts.translate(
            'A1_ai_context',
            "The current analysis is about the evolution of total national enrollment, male and female, in Cuba from 2015 to 2025. The data, presented in the chart, shows a significant peak around 2020-2021 followed by a decline."
        )
        ask_ai_component(
            analysis_context=context_ai_text,
            key="a1_nacional",
            extra_data=[fig_a1],
            translation=ts.translate('ask_ai_component', {})
        )

    if game_controller.game_mode:
        df_historico_juego, _, _, _ = analisis_A1(df_main)
        
        if df_historico_juego is not None and not df_historico_juego.empty:
            pico_data = df_historico_juego.loc[df_historico_juego['matricula_total'].idxmax()]
            pico_matricula = pico_data['matricula_total']
            pico_curso = pico_data['curso_academico']

            game_data_A1_estimator = pd.DataFrame([{
                "name": ts.translate('A1_peak_enrollment_label', "Matrícula Nacional en el Año Pico ({curso})").format(curso=pico_curso),
                "value": pico_matricula
            }])

            st.markdown("---")
            st.subheader(ts.translate('A1_game_subheader', "A Prueba: La Magnitud del Pico"))
            st.markdown(ts.translate(
                'A1_game_intro',
                "El sistema universitario cubano alcanzó un número máximo de estudiantes en un punto de la última década. Antes de ver el gráfico, ¿qué tan buena es tu intuición? Intenta estimar cuál fue esa cifra máxima."
            ))

            estimator_game_A1 = EstimatorMinigame(
                game_id="A1_EstimatorPicoNacional",
                game_title=ts.translate('A1_game_title', "El Estimador del Pico Nacional"),
                data=game_data_A1_estimator,
                content_callback=render_analysis_content,
                num_rounds=1,
                min_score_for_victory=75,
                translation={
                    'estimator_question': ts.translate(
                        'A1_estimator_question', 
                        "¿Cuántos estudiantes crees que había en todo el país durante el curso de máxima matrícula ({curso})?"
                    ).format(curso=pico_curso)
                }
            )
            estimator_game_A1.render()
        else:
            render_analysis_content()
    else:
        render_analysis_content()

### Mosaico de Saberes
@st.fragment
def A2(df_main, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('A2_header',"📚 Un Mosaico de Saberes: ¿Hacia Dónde se Inclinan los Futuros Profesionales?"))
    st.markdown(ts.translate('A2_markdown_1',"""
    La universidad es un vasto jardín donde florecen diversas disciplinas. Cada rama del conocimiento,
    desde las Ciencias Médicas o Matemáticas hasta las Artes, representa un camino único de formación y contribución
    a la sociedad. En esta sección, desglosamos la matrícula total para ver cómo se distribuyen
    los estudiantes entre estas grandes áreas, con el objetivo de responder preguntascomo:
    - ¿Hay protagonistas claros?
    - ¿Cómo ha danzado el interés estudiantil a lo largo de la última década?
    """))
    st.markdown("---")

    # --- ANÁLISIS 1: POPULARIDAD DE LAS RAMAS ---

    def render_analysis_content_A2_part1():
        st.subheader(ts.translate('A2_fig_a2_abs_subheader',"La Fuerza de Cada Rama: Evolución Histórica de la Matrícula"))
        with st.spinner(ts.translate('A2_spinner_1',"Analizando la evolución de las ramas de ciencias...")):
            df_hist, df_pct, _, _ = analisis_A2(df_main)

        if df_hist is not None:
            fig_a2_abs = graficate_A2_evolucion(df_hist, ts)
            st.plotly_chart(fig_a2_abs, use_container_width=True, key="fig_a2_abs_mosaico")
            st.markdown(ts.translate('A2_fig_a2_abs_markdown_1',"""
            **Cada Línea, una Corriente del Conocimiento:**
            Este gráfico traza el viaje de la matrícula absoluta (número total de estudiantes) para cada rama de ciencias a lo largo de los años.

            *   **Liderazgo Destacado:** Las **Ciencias Médicas** (línea verde agua) se erigen como la rama con la matrícula más numerosa de forma consistente durante todo el período, partiendo de unos 70,000 estudiantes en 2015-16, alcanzando un pico impresionante cercano a los **95,000 estudiantes en 2020-2021**, y aunque experimentan un descenso posterior, se mantienen como la principal fuerza, cerrando en 2024-2025 con más de 70,000 estudiantes.

            *   **Persecución y Dinamismo:** Las **Ciencias Pedagógicas** (línea naranja) muestran una trayectoria muy dinámica. Comienzan con una matrícula significativa (alrededor de 30,000), experimentan un crecimiento notable hasta superar los **65,000 estudiantes en 2020-2021 y 2021-2022**, convirtiéndose en la segunda rama más grande durante esos años. Sin embargo, sufren un declive pronunciado en los últimos cursos, finalizando cerca de los 40,000 estudiantes.

            *   **Bloque Intermedio Consistente:** Un grupo de ramas mantiene una presencia estable aunque con fluctuaciones:
                *   Las **Ciencias Técnicas** (línea rosa) y las **Ciencias Sociales y Humanísticas** (línea celeste) muestran trayectorias paralelas, creciendo desde aproximadamente 20,000 estudiantes hasta un pico alrededor de los **30,000-32,000** entre 2020-21 y 2021-22, para luego descender y situarse en torno a los 23,000-25,000 estudiantes al final del período.
                *   Las **Ciencias Económicas** (línea roja) presentan un crecimiento más moderado pero constante hasta 2021-22 (alcanzando unos 24,000 estudiantes), seguido de un descenso similar a otras ramas, terminando cerca de los 15,000.
                *   Las **Ciencias Agropecuarias** (línea azul oscuro) y las **Ciencias de la Cultura Física y el Deporte** (línea verde oscuro/marrón) se mantienen en un rango más bajo, generalmente entre 5,000 y 15,000 estudiantes, con picos alrededor de 2020-2021 y descensos posteriores.

            *   **Nicho Especializado:** Las **Ciencias Naturales y Matemáticas** (línea morada) y las **Ciencias de las Artes** (línea violeta) representan las ramas con menor volumen de matrícula, manteniéndose consistentemente por debajo de los 5,000 estudiantes a lo largo de toda la década. Esto sugiere una alta especialización o una demanda más acotada.
            """))
            ask_ai_component(
                analysis_context="The current analysis is about the evolution of absolute enrollment (number of students) by branch of science in Cuba. The data is shown in the attached chart.",
                key="a2_mosaico_abs",
                extra_data=[fig_a2_abs],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.warning(ts.translate('generic_warn_figs',"No se pudo generar el gráfico de evolución absoluta por rama."))

        if df_pct is not None:
            st.subheader(ts.translate('A2_fig_a2_pct_subheader',"El Reparto del Pastel Académico: Distribución Porcentual Histórica"))
            fig_a2_pct = graficate_A2_distribucion(df_pct, ts)
            st.plotly_chart(fig_a2_pct, use_container_width=True, key="fig_a2_pct_mosaico")
            st.markdown(ts.translate('A2_fig_a2_pct_markdown_1',"""
            **Proporciones en el Lienzo Universitario:**
            Este gráfico de área apilada nos muestra qué "porción del pastel" ha representado cada rama de ciencias dentro del total de la matrícula universitaria en cada curso académico.

            *   **Dominio Persistente de las Ciencias Médicas:** La ancha banda verde agua en la parte superior confirma que las Ciencias Médicas han representado consistentemente la mayor proporción de estudiantes, ocupando cerca del **40-50% del total** en su punto más alto (alrededor de 2016-17 y nuevamente hacia 2024-2025, tras una ligera reducción porcentual a mediados del período).

            *   **Ascenso y Descenso de las Ciencias Pedagógicas:** La banda naranja de las Ciencias Pedagógicas muestra un interesante cambio en su peso relativo. Comienza siendo una porción importante, se expande significativamente hasta representar la segunda mayor proporción (llegando a casi un **25-30%** del total alrededor de 2019-2021), pero luego reduce su participación porcentual en los últimos años.

            *   **Estabilidad Relativa en el Medio:** Las Ciencias Técnicas (banda marrón/ocre), Sociales y Humanísticas (banda celeste) y Económicas (banda azul oscuro) mantienen proporciones más estables a lo largo del tiempo, aunque con ligeras variaciones. Juntas, suelen conformar una porción significativa del estudiantado. Por ejemplo, las Ciencias Sociales y Humanísticas parecen ocupar consistentemente alrededor del 10-15%.

            *   **Menor Peso Porcentual:** Las demás ramas (Agropecuarias, Cultura Física, Naturales y Matemáticas, Artes) representan individualmente porcentajes menores del total de la matrícula, lo que es coherente con su menor volumen absoluto de estudiantes.

            Este análisis porcentual es crucial porque nos permite entender no solo cuántos estudiantes hay en cada rama, sino también cómo se distribuye el interés o la capacidad de admisión en relación con el conjunto del sistema universitario.
            """))
            ask_ai_component(
                analysis_context="The current analysis is about the percentage distribution of enrollment by branch of science in Cuba. The data is shown in the attached stacked area chart.",
                key="a2_mosaico_pct",
                extra_data=[fig_a2_pct],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.warning(ts.translate('generic_warn_figs',"No se pudo generar el gráfico de distribución porcentual por rama."))

    if game_controller.game_mode:
        st.subheader(ts.translate('A2_subhead_popularity', "Ranking de Popularidad: ¿Qué áreas del saber lideran?"))
        st.markdown(ts.translate('A2_intro_game1', """
        Antes de sumergirnos en los gráficos, pongamos a prueba tu percepción. A lo largo de Cuba, miles de estudiantes eligen su camino profesional cada año. ¿Cuáles crees que son las ramas del conocimiento que atraen a la mayor cantidad de universitarios? ¿Podrías ordenar las principales áreas según su popularidad?
        """))
        
        ano_reciente = df_main['ano_inicio_curso'].max()
        df_ramas_reciente = df_main[df_main['ano_inicio_curso'] == ano_reciente]\
            .groupby('rama_ciencias')['matricula_total'].sum().reset_index()

        if not df_ramas_reciente.empty:
            game_data_A2_classifier = df_ramas_reciente.rename(columns={'rama_ciencias': 'name', 'matricula_total': 'value'})
            
            classifier_game_A2 = ClassifierMinigame(
                game_id="A2_ClassifierSaber",
                game_title=ts.translate('A2_game_title', "El Clasificador del Saber"),
                data=game_data_A2_classifier,
                content_callback=render_analysis_content_A2_part1,
                difficulty=4,
                min_score_for_victory=30
            )
            classifier_game_A2.render()
        else:
            render_analysis_content_A2_part1()
    else:
        render_analysis_content_A2_part1()

    st.markdown("---")

    # --- ANAISIS 2: CORRELACIÓN ENTRE RAMAS ---
    
    def render_analysis_content_A2_part2():
        st.subheader(ts.translate('A2_subheader_2',"🔗 Interconexiones en el Crecimiento: ¿Cómo se Relacionan las Ramas?"))
        st.markdown(ts.translate('A2_markdown_2',"""
            No todas las ramas de ciencias crecen o decrecen de forma aislada. Algunas pueden mostrar
            tendencias de matrícula similares a lo largo del tiempo, mientras que otras pueden tener
            dinámicas más independientes. El siguiente mapa de calor (heatmap) visualiza la
            **correlación del cambio porcentual anual de la matrícula** entre las diferentes ramas de ciencias.
            
            *   Un **valor cercano a 1 (azul oscuro/morado intenso)** indica una fuerte correlación positiva: cuando una rama crece, la otra tiende a crecer también en ese mismo período.
            *   Un **valor cercano a -1 (no visible en este ejemplo, sería el otro extremo del color)** indicaría una fuerte correlación negativa: cuando una crece, la otra tiende a decrecer.
            *   Un **valor cercano a 0 (colores más claros/neutros)** sugiere poca o ninguna relación lineal en sus patrones de crecimiento anual.
        """))
        
        fig_corr_ramas, df_corr_ramas, msg_code = graficate_A2_correlacion(df_main, ts)

        if msg_code == "success" and fig_corr_ramas is not None:
            st.plotly_chart(fig_corr_ramas, use_container_width=True, key="fig_a2_corr_heatmap")
            with st.expander(ts.translate('A2_fig_corr_expander',"🔍 Análisis Detallado de las Correlaciones Observadas"), expanded=True):
                st.markdown(ts.translate('A2_fig_corr_markdown_1',"""
                **Observaciones Clave del Mapa de Correlación:**

                *   **Sincronización Fuerte:** Se observa una **alta correlación positiva (valores > 0.9)** en las tendencias de crecimiento anual entre:
                    *   **Ciencias Agropecuarias y Ciencias Económicas** (aprox. 0.98)
                    *   **Ciencias Agropecuarias y Ciencias Pedagógicas** (aprox. 0.98)
                    *   **Ciencias Agropecuarias y Ciencias de la Cultura Física y el Deporte** (aprox. 0.96)
                    *   Así como entre **Ciencias Económicas, Pedagógicas y de la Cultura Física**, todas mostrando coeficientes muy elevados entre sí.
                    Esto sugiere que estas ramas a menudo experimentan impulsos de crecimiento (o contracción) de manera muy similar y simultánea, posiblemente debido a factores macroeconómicos, políticas educativas integrales o ciclos de demanda estudiantil que las afectan conjuntamente.

                *   **Correlaciones Positivas Moderadas:**
                    *   Las **Ciencias Médicas** muestran una correlación positiva moderada (generalmente entre 0.5 y 0.7) con varias otras ramas como Económicas, Sociales y Humanísticas, y Técnicas. Esto podría indicar que el sector médico, si bien tiene sus propias dinámicas, también se beneficia o participa de tendencias expansivas más amplias en la educación superior.
                    *   Las **Ciencias Técnicas** también se correlacionan moderadamente con la mayoría de las otras ramas, sugiriendo una conexión con el ciclo general del sistema.

                *   **Independencia Relativa Notoria:**
                    *   Las **Ciencias Naturales y Matemáticas** destacan por tener las **correlaciones más bajas** con casi todas las demás ramas (coeficientes frecuentemente entre 0.2 y 0.4). Esto indica que su patrón de crecimiento de matrícula parece ser bastante independiente de las fluctuaciones que afectan a otras grandes áreas del conocimiento. Esta rama podría estar influenciada por factores muy específicos, como programas de fomento científico particulares o una demanda más especializada y menos sensible a tendencias generales.
                    *   Las **Ciencias de las Artes** también muestran correlaciones más débiles con algunas de las ramas más grandes como Pedagógicas, aunque tiene una correlación moderada interesante con Ciencias Médicas.

                *   **Implicaciones Estratégicas:**
                    *   La fuerte sincronización entre ciertas ramas sugiere que las estrategias de planificación y asignación de recursos podrían considerar estos "clusters" de comportamiento.
                    *   La independencia de Ciencias Naturales y Matemáticas podría requerir un enfoque y monitoreo diferenciado para asegurar su vitalidad y alineación con las necesidades de desarrollo científico-técnico del país.
                    *   La ausencia de correlaciones fuertemente negativas (en este gráfico) sugiere que, a nivel agregado de cambio anual, no hay una "canibalización" evidente donde el crecimiento de una rama sea directamente a costa de otra, aunque no se descartan dinámicas competitivas a niveles más específicos.
                """))
            ask_ai_component(
                analysis_context="The current analysis is about the correlation matrix of annual enrollment growth among the different branches of science. The data is provided in the attached correlation table.",
                key="a2_corr_ramas",
                extra_data=[df_corr_ramas],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.warning(ts.translate('A2_corr_warn_1',"No se pudo generar el mapa de correlación entre ramas."))

    if game_controller.game_mode:
        st.subheader(ts.translate('A2_subhead_correlation', "Sinergias Ocultas: ¿Qué ramas crecen juntas?"))
        st.markdown(ts.translate('A2_intro_game2', """
        Las ramas del saber no son islas. Sus tendencias de crecimiento a menudo están conectadas. Algunas se mueven en perfecta sincronía, mientras que otras bailan a su propio ritmo. Cuando el interés en las Ciencias Pedagógicas crece, ¿qué otra área crees que se beneficia de un impulso similar? ¡Acepta el duelo y descúbrelo!
        """))

        _, df_corr_juego, _ = graficate_A2_correlacion(df_main, ts)
        
        if df_corr_juego is not None and not df_corr_juego.empty:
            df_corr_juego.index.name = "Rama_A"
            df_corr_juego.columns.name = "Rama_B"
            df_corr_long = df_corr_juego.stack().reset_index()
            df_corr_long.columns = ['Rama_A', 'Rama_B', 'Correlacion']
            df_corr_long = df_corr_long[df_corr_long['Rama_A'] != df_corr_long['Rama_B']]

            rama_pivote = "Ciencias Pedagógicas"
            if rama_pivote in df_corr_long['Rama_A'].values:
                df_juego_duelo = df_corr_long[df_corr_long['Rama_A'] == rama_pivote].copy()
                
                game_data_A2_duel = pd.DataFrame({
                    "name": df_juego_duelo['Rama_B'],
                    "value": df_juego_duelo['Correlacion']
                })

                if len(game_data_A2_duel) >= 2:
                    duel_game_A2 = DataDuelMinigame(
                        game_id="A2_DuelCorrelacion",
                        game_title=ts.translate('A2_game_title_corr', "Duelo de Sinergias"),
                        data=game_data_A2_duel,
                        content_callback=render_analysis_content_A2_part2,
                        num_rounds=3,
                        min_score_for_victory=20,
                        translation={
                            'duel_question': ts.translate(
                                'A2_duel_question_corr', 
                                "Crecimiento de las **Ciencias Pedagógicas** es MÁS similar al de:"
                            )
                        }
                    )
                    duel_game_A2.render()
                else:
                    render_analysis_content_A2_part2()
            else:
                render_analysis_content_A2_part2()
        else:
            render_analysis_content_A2_part2()
    else:
        render_analysis_content_A2_part2()

### Carreras Bajo la Lupa
@st.fragment
def A3(df_main, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('A3_header',"🔍 Carreras Bajo la Lupa: Popularidad, Tendencias y Dinamismo"))
    st.markdown(ts.translate('A3_markdown_1',"""
    Tras explorar las grandes ramas del saber, es momento de enfocar nuestra lente en las unidades
    fundamentales: las carreras universitarias. ¿Cuáles son las que capturan el mayor interés estudiantil?
    ¿Cómo ha sido su evolución individual? Y, muy importante, ¿cuáles muestran un crecimiento
    acelerado y cuáles parecen estar perdiendo impulso?
    """))
    st.markdown("---")

    top_n = 10

    def render_analysis_content_part1():
        st.subheader(ts.translate('A3_subheader_2',"🏆 El Podio de las Carreras: ¿Cuáles Lideran la Matrícula Actual?"))
        
        with st.spinner(ts.translate('A3_spinner_1',"Analizando el ranking y evolución de las carreras top...")):
            df_ranking, df_evolucion, curso_reciente, status = analisis_A3(df_main, top_n=top_n)

        if status != "success" or df_ranking is None:
            st.warning(ts.translate('A3_warning_analysis_failed', "No se pudo realizar el análisis de popularidad de carreras. Estado: {status}").format(status=status))
            return

        st.markdown(ts.translate('A3_markdown_2',"""
        A la izquierda observamos el ranking de todas las carreras según su matrícula total en el curso más reciente
        ({year_range}). A la derecha, vemos la evolución histórica de la matrícula
        para las {top_n} carreras que actualmente se encuentran en la cima de este ranking.
        """).format(year_range=curso_reciente, top_n=top_n))

        col_ranking, col_evolucion_top = st.columns([1, 2], gap="large")

        with col_ranking:
            st.dataframe(
                df_ranking, 
                use_container_width=True,
                hide_index=True,
                height=500
            )

        with col_evolucion_top:
            if df_evolucion is not None and not df_evolucion.empty:
                fig_evolucion = graficate_A3_evolucion(df_evolucion, ts, top_n)
                st.plotly_chart(fig_evolucion, use_container_width=True, key="fig_a3_lupa_evolution")
            else:
                st.info(ts.translate('A3_col_evo_top_info',"No se generó gráfico de evolución para las carreras top actuales."))

        st.markdown(ts.translate('A3_markdown_3',"""
        **Puntos Clave del Podio:**
        *   **Liderazgo Indiscutible:** **Medicina** se posiciona firmemente como la carrera con la mayor matrícula (35,889 estudiantes), una constante que ya habíamos vislumbrado al analizar las ramas del saber.
        *   **Fuerzas Significativas:** Le siguen **Cultura Física** (14,695) y **Educación Primaria** (12,867), demostrando una demanda considerable en estas áreas.
        *   **Top 5 Robusto:** **Enfermería** (9,999) y **Contabilidad y Finanzas** (9,883) completan el top 5, ambas con una matrícula muy cercana a los 10,000 estudiantes.
        *   **Evolución de las Líderes:** El gráfico de la derecha nos permite ver cómo estas carreras (y otras del top 10) han llegado a su posición actual. Observa cómo algunas han tenido un crecimiento más sostenido, mientras otras muestran picos y valles más pronunciados.
        """))

        ask_ai_component(
            analysis_context="Analysis of the degree program rankings and the evolution of the top.",
            key="a3_carreras_top",
            extra_data=[df_ranking, df_evolucion],
            translation=ts.translate('ask_ai_component',{})
        )

    if game_controller.game_mode:
        st.subheader(ts.translate('A3_game1_subheader', "A Prueba: El Ranking de Popularidad"))
        st.markdown(ts.translate('A3_game1_intro', """
        Antes de ver el ranking completo, ¿qué tan buena es tu intuición sobre la demanda estudiantil? Te presentamos una selección de carreras. ¡Ordénalas de la más popular a la menos popular según la matrícula del último año!
        """))
        
        df_ranking_game, _, _, _ = analisis_A3(df_main, top_n=top_n)
        if df_ranking_game is not None and not df_ranking_game.empty:
            game_data_classifier = df_ranking_game.rename(columns={'carrera': 'name', 'matricula_total': 'value'})
            
            classifier_game_A3 = ClassifierMinigame(
                game_id="A3_ClassifierPopularidad",
                game_title=ts.translate('A3_game1_title', "El Clasificador de Carreras"),
                data=game_data_classifier,
                content_callback=render_analysis_content_part1,
                difficulty=4,
                min_score_for_victory=30
            )
            classifier_game_A3.render()
        else:
            render_analysis_content_part1()
    else:
        render_analysis_content_part1()

    st.markdown("---")

    def render_analysis_content_part2():
        st.subheader(ts.translate('A3_subheader_4', "🚀 El Ritmo del Cambio: ¿Qué Carreras Despegan o Aterrizan?"))
        st.markdown(ts.translate('A3_markdown_4', """
        La **Tasa de Crecimiento Anual Compuesto (CAGR)** nos ofrece una perspectiva del dinamismo.
        Calcula el crecimiento (o decrecimiento) porcentual promedio de la matrícula de una carrera cada año,
        considerando todo el período analizado. Un CAGR alto sugiere una expansión rápida.
        """))
        
        with st.spinner(ts.translate('A3_spinner_4',"Calculando el dinamismo de las carreras (CAGR)...")):
            df_cagr, periodo_str, status_cagr = analisis_A3_cagr(df_main)

        if status_cagr != "success" or df_cagr is None:
            st.warning(ts.translate('A3_warning_cagr_failed', "No se pudo realizar el análisis de crecimiento (CAGR). Estado: {status}").format(status=status_cagr))
            return
            
        fig_top_cagr, fig_bottom_cagr = graficate_A3_cagr(df_cagr, periodo_str, ts) #type:ignore

        col_cagr_top, col_cagr_bottom = st.columns(2, gap="large")

        with col_cagr_top:
            st.markdown(f"**{ts.translate('A3_cagr_top_title', '📈 Top 15 con Mayor Crecimiento')}**")
            st.plotly_chart(fig_top_cagr, use_container_width=True, key="fig_a6_top_lupa_cagr")
            st.markdown(ts.translate('A3_col_cagr_top_markdown_2', """
            Estas carreras han experimentado la expansión más notable en su matrícula promedio anual.
            *   **Sorprendente Despegue:** **Servicios Estomatológicos** lidera con un CAGR superior al 100%, lo que indica una duplicación (o más) de su matrícula promedio año tras año.
            *   **Ingenierías en Auge:** Varias ingenierías como **Artística**, **Procesos Agroindustriales** e **Informática** muestran un crecimiento muy saludable.
            *   **Educación con Impulso:** Ramas de la educación como **Preescolar**, **Agropecuaria** y **Primaria** también figuran con un CAGR positivo y significativo.
            """))

        with col_cagr_bottom:
            st.markdown(f"**{ts.translate('A3_cagr_bottom_title', '📉 Top 15 con Mayor Decrecimiento')}**")
            st.plotly_chart(fig_bottom_cagr, use_container_width=True, key="fig_a6_bottom_lupa_cagr")
            st.markdown(ts.translate('A3_col_cagr_bottom_markdown_2', """
            En el otro extremo, estas carreras han visto su matrícula promedio anual disminuir o crecer a un ritmo mucho menor.
            *   **Ajustes Notables:** **Estudios Socioculturales** y **Estomatología** (no confundir con Servicios Estomatológicos) presentan los mayores decrecimientos promedio.
            *   **Desafíos Diversos:** Carreras como **Ingeniería Agrícola**, **Artes Visuales**, **Matemática**, **Música** y varias **Ingenierías** (Hidráulica, Civil, Telecomunicaciones, Industrial) también aparecen en esta lista, sugiriendo una revisión de sus tendencias.
            """))

        st.markdown(ts.translate('A3_markdown_5', """
        **Reflexiones Estratégicas a partir de estos Ritmos:**
        *   Un **alto CAGR** no siempre significa una matrícula total masiva (podría ser una carrera pequeña creciendo rápido), pero sí indica una **tendencia positiva fuerte** que merece atención, ya sea para fomentar o para asegurar recursos.
        *   Un **CAGR bajo o negativo** en carreras importantes podría ser una señal para investigar las causas: ¿cambios en el mercado laboral, preferencias estudiantiles, oferta académica?
        *   Es crucial cruzar esta información de CAGR con la matrícula absoluta (del ranking) para obtener una imagen completa.
        """))

        ask_ai_component(
            analysis_context="Analysis of the Compound Annual Growth Rate (CAGR) of degree programs.",
            key="a3_carreras_cagr",
            extra_data=[df_cagr],
            translation=ts.translate('ask_ai_component',{})
        )

    if game_controller.game_mode:
        st.subheader(ts.translate('A3_game2_subheader', "Duelo del Crecimiento"))
        st.markdown(ts.translate('A3_game2_intro', """
        Algunas carreras crecen a un ritmo vertiginoso mientras otras se contraen. ¿Podrás identificar cuál de las dos opciones ha tenido una mayor tasa de crecimiento promedio anual? ¡Acepta el duelo!
        """))
        
        df_cagr_game, _, _ = analisis_A3_cagr(df_main)
        if df_cagr_game is not None and not df_cagr_game.empty:
            game_data_duel = df_cagr_game.rename(columns={'carrera': 'name', 'CAGR': 'value'})

            duel_game_A3 = DataDuelMinigame(
                game_id="A3_DuelCrecimiento",
                game_title=ts.translate('A3_game2_title', "Duelo de Crecimiento"),
                data=game_data_duel,
                content_callback=render_analysis_content_part2,
                num_rounds=3,
                min_score_for_victory=20,
                translation={
                    'duel_question': ts.translate('A3_duel_question', "Esta carrera tuvo un **MAYOR** crecimiento promedio que la otra.")
                }
            )
            duel_game_A3.render()
        else:
            render_analysis_content_part2()
    else:
        render_analysis_content_part2()

### Perspectiva de Género
@st.fragment
def A4(df_main, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('A4_header', "♀️♂️ Equilibrando la Balanza: Una Mirada a la Perspectiva de Género"))
    st.markdown(ts.translate('A4_markdown_1', """
    La universidad no solo forma profesionales, sino que también moldea una sociedad más justa y equitativa.
    En esta sección, nos adentramos en la composición de género de la matrícula universitaria.
    ¿Existe un equilibrio entre hombres y mujeres en las aulas? ¿Hay áreas del conocimiento
    tradicionalmente asociadas a un género que mantienen esos patrones, o estamos presenciando
    una transformación hacia una mayor paridad? Acompáñanos a descubrirlo.
    """))
    st.markdown("---")

    with st.spinner(ts.translate('A4_spinner_1', "Analizando la perspectiva de género...")):
        df_ramas, df_fem, df_masc, curso_reciente, status = analisis_A4(df_main)

    if status != "success":
        st.warning(ts.translate('A4_warning_analysis_failed', "No se pudo realizar el análisis de género. Estado: {status}").format(status=status))
        return

    def render_part1():
        if df_ramas is not None and not df_ramas.empty:
            st.subheader(ts.translate('A4_fig_ramas_subheader', "Participación Femenina por Rama de Ciencias ({curso})").format(curso=curso_reciente))
            fig = graficate_A4_ramas(df_ramas, ts, curso_reciente) #type:ignore
            st.plotly_chart(fig, use_container_width=True, key="fig_a4_ramas_genero")
            st.markdown(ts.translate('A4_fig_ramas_markdown_1', """
            **El Panorama General por Áreas del Saber:**
            Este gráfico de barras nos muestra el porcentaje de mujeres matriculadas en cada gran rama de ciencias. La línea roja punteada en el 50% representa la paridad perfecta.

            *   **Liderazgo Femenino Pronunciado:** Las **Ciencias Pedagógicas** destacan con más del **80%** de matrícula femenina, seguidas de cerca por las **Ciencias Sociales y Humanísticas** y las **Ciencias Médicas**, ambas superando el **70%**. Esto indica una fuerte presencia y preferencia femenina en estas importantes áreas.
            *   **Mayoría Femenina Sostenida:** Las **Ciencias Económicas**, **Ciencias de las Artes** y **Ciencias Naturales y Matemáticas** también muestran una mayoría de mujeres, con porcentajes que oscilan entre el **55% y el 65%**, situándose por encima de la línea de paridad.
            *   **Cerca de la Paridad o Ligera Mayoría Masculina:** Las **Ciencias Agropecuarias** se encuentran más cerca del equilibrio, aunque aún con una ligera mayoría femenina (casi el 50%).
            *   **Desafíos en Áreas Técnicas y Deportivas:** En contraste, las **Ciencias Técnicas** (aproximadamente 35% mujeres) y, de manera más marcada, las **Ciencias de la Cultura Física y el Deporte** (alrededor del 32% mujeres) son las ramas con la menor representación femenina, indicando una persistente brecha de género en estos campos.
            """))
            
            ask_ai_component(
                analysis_context="Analysis of the percentage of female participation by field of science.",
                key="a4_ramas_genero",
                extra_data=[df_ramas],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.info(ts.translate('A4_info_no_branch_data', "No hay datos de género por ramas para mostrar."))

    def render_part2():
        st.markdown("---")
        if df_fem is not None and not df_fem.empty and df_masc is not None and not df_masc.empty:
            st.subheader(ts.translate('A4_fig_carreras_subheader', "Zoom a las Carreras: Extremos del Espectro de Género ({curso}, Matrícula >= 30)").format(curso=curso_reciente))
            fig = graficate_A4_carreras(df_fem, df_masc, ts, curso_reciente) #type:ignore
            st.plotly_chart(fig, use_container_width=True, key="fig_a4_carreras_genero")
            st.markdown(ts.translate('A4_fig_carreras_markdown_1', """
            **Casos Destacados de Mayoría y Minoría Femenina:**
            Estos gráficos nos llevan al detalle de las carreras, mostrando las 10 con mayor porcentaje de mujeres y las 10 con menor porcentaje (es decir, mayor presencia masculina), siempre que tengan una matrícula de al menos 30 estudiantes para asegurar la representatividad.

            *   **Feminización Extrema en Algunas Áreas:** Carreras como **Educación Preescolar** se acercan al 100% de matrícula femenina. Otras, como **Técnico Superior en Logofonoaudiología**, **Educación Logopedia** y **Educación Español-Literatura**, también muestran una abrumadora mayoría de mujeres, superando el 90%. Esto es consistente con la alta feminización de las Ciencias Pedagógicas. **Servicios Estomatológicos** y **Estudios Socioculturales** también destacan en este grupo.

            *   **Dominio Masculino en Ingenierías y Áreas Técnicas:** En el otro extremo, carreras como **Ingeniería Informática**, **Ingeniería en Automática**, **Ciencias de la Computación**, **Gestión del Proceso Inversionista** y varias **Ingenierías Mecánica, Eléctrica y en Técnicos Superior en Entrenamiento Deportivo** presentan porcentajes de mujeres muy bajos, algunos por debajo del 10% y la mayoría por debajo del 25%. Esto refleja la brecha observada en las Ciencias Técnicas y deportivas a nivel de rama.

            *   **Matices Importantes:** Es crucial observar que incluso dentro de las "Top 10 con Menor % de Mujeres", los porcentajes varían. Mientras algunas ingenierías apenas superan el 5-10% de presencia femenina, otras pueden estar más cerca del 20-25%.
            """))

            ask_ai_component(
                analysis_context="Analysis of degree programs with the highest and lowest female participation.",
                key="a4_carreras_genero",
                extra_data=[df_fem, df_masc],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.info(ts.translate('A4_info_no_career_data', "No hay suficientes datos de carreras para mostrar el análisis de extremos de género."))

        st.markdown(ts.translate('A4_markdown_2', """
        ---
        **Reflexiones para la Acción:**
        *   La alta feminización en ciertas ramas y carreras es un fenómeno consolidado. Si bien refleja vocaciones, también es importante asegurar que no existan barreras implícitas o desincentivos para la participación masculina en ellas.
        *   El mayor desafío para la equidad de género se encuentra claramente en las **Ciencias Técnicas** y en varias ingenierías específicas, así como en **Ciencias de la Cultura Física y el Deporte**. Se requieren estrategias continuas y efectivas para atraer y retener a más mujeres en estos campos cruciales para el desarrollo tecnológico y social.
        *   Estos datos son una invitación a profundizar: ¿Cuáles son las causas de estos desbalances? ¿Cómo podemos inspirar a las nuevas generaciones a explorar todas las áreas del conocimiento sin sesgos de género?
        """))

    if game_controller.game_mode:
        st.subheader(ts.translate('A4_game1_subheader', "Duelo de Género por Rama"))
        st.markdown(ts.translate('A4_game1_intro', "Algunas áreas del conocimiento atraen a más mujeres que otras. ¿Sabrías decir en cuál de las siguientes ramas hay un mayor porcentaje de matrícula femenina?"))
        
        if df_ramas is not None and not df_ramas.empty:
            game_data_duel = df_ramas.rename(columns={'rama_ciencias': 'name', 'Porcentaje_Mujeres': 'value'})
            
            duel_game_A4 = DataDuelMinigame(
                game_id="A4_DuelGeneroRama",
                game_title=ts.translate('A4_game1_title', "Duelo de Ramas"),
                data=game_data_duel,
                content_callback=render_part1,
                num_rounds=3,
                min_score_for_victory=20,
                translation={
                    'duel_question': ts.translate('A4_duel_question', "¿Qué rama tiene un porcentaje MÁS ALTO de mujeres?")
                }
            )
            duel_game_A4.render()
        else:
            render_part1()

        if 'A4_DuelGeneroRama' in game_controller.registered_games and game_controller.registered_games['A4_DuelGeneroRama'].is_finished():
            st.markdown("---")
            st.subheader(ts.translate('A4_game2_subheader', "Espera! Hay un intruso entre las carreras!"))
            st.markdown(ts.translate('A4_game2_intro', "Tres de las siguientes carreras tienen una abrumadora mayoría de mujeres en sus aulas. Una de ellas, sin embargo, es un campo predominantemente masculino. ¡Identifica al intruso!"))
            
            if df_fem is not None and not df_fem.empty and df_masc is not None and not df_masc.empty:
                items_fem = df_fem.sample(3)[['carrera']].copy()
                items_fem['category'] = 'Feminized'
                
                item_masc = df_masc.sample(1)[['carrera']].copy()
                item_masc['category'] = 'Masculinized'
                
                game_data_impostor = pd.concat([items_fem, item_masc]).rename(columns={'carrera': 'item'})
                
                impostor_game_A4 = ImpostorMinigame(
                    game_id="A4_ImpostorGeneroCarrera",
                    game_title=ts.translate('A4_game2_title', "El Intruso de Género"),
                    data=game_data_impostor,
                    item_col='item',
                    category_col='category',
                    exclude_if_contains=False,
                    content_callback=render_part2,
                    min_score_for_victory=25
                )
                impostor_game_A4.render()
            else:
                render_part2()
    else:
        render_part1()
        render_part2()

### Universidades: Fortalezas y Focos
@st.fragment
def A5(df_main, df_ins, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('A5_header', "🏛️ Universidades en Perspectiva: Descubriendo Fortalezas y Focos de Especialización"))
    st.markdown(ts.translate('A5_markdown_1', """
    Cada universidad es un ecosistema único con su propia historia, vocación y áreas de excelencia.
    En esta sección, cambiamos nuestra perspectiva para analizar cómo se distribuye el talento estudiantil
    a nivel institucional. ¿Qué universidades concentran la mayor cantidad de estudiantes?
    ¿Existen centros altamente especializados en ciertas ramas o carreras? ¿Y qué carreras
    son joyas raras, ofrecidas solo por unas pocas instituciones?
    """))
    st.markdown("---")
    
    with st.spinner(ts.translate('A5_spinner_1', "Analizando la distribución institucional de la matrícula...")):
        df_treemap, df_oferta, curso, status = analisis_A5(df_main)

    if status != "success":
        st.warning(ts.translate('A5_warning_analysis_failed', "No se pudo realizar el análisis institucional. Estado: {status}").format(status=status))
        return

    def render_part1():
        st.subheader(ts.translate('A5_fig_treemap_subheader', "Mapa Interactivo de la Matrícula Universitaria ({curso})").format(curso=curso))
        if df_treemap is not None and not df_treemap.empty:
            fig = graficate_A5_treemap(df_treemap, ts, curso)
            st.plotly_chart(fig, use_container_width=True, key="fig_a5_treemap_unis")
            st.markdown(ts.translate('A5_fig_treemap_markdown_1', """
            **Navegando el Universo Institucional:**
            Este "mapa de árbol" (treemap) es una representación visual de la matrícula total.
            *   **El Tamaño Importa:** El área de cada rectángulo es proporcional al número de estudiantes. Comienza con "Todas las Universidades"; haz clic en una universidad (ej. `UCLV`, `UH`, `CUJAE`) para ver cómo se desglosa su matrícula por ramas de ciencias. Un nuevo clic en una rama te mostrará las carreras dentro de ella y su peso en esa institución.
            *   **Identifica los Gigantes:** A simple vista, puedes identificar las universidades con mayor volumen de estudiantes. Por ejemplo, la **UO (Universidad de Oriente)**, **UH (Universidad de La Habana)** y **UCMLH (Universidad de Ciencias Médicas de La Habana)**, entre otras, muestran rectángulos considerablemente grandes, indicando una matrícula importante.
            *   **Focos de Especialización:** Observa cómo algunas universidades tienen casi toda su "área" concentrada en una o dos ramas (ej. las Universidades de Ciencias Médicas predominantemente en "Ciencias Médicas"), mientras otras muestran una mayor diversificación, como se observa, Ciencias Médicas sobresale en todas las universidades que la ofertan.
            """))
        else:
            st.info(ts.translate('A5_info_no_treemap_data', "No hay datos disponibles para generar el mapa interactivo."))
        
        st.markdown("---")
        st.subheader(ts.translate('A5_df_carreras_unicas_subheader', "Joyas Académicas: Carreras por Nivel de Exclusividad"))
        
        if game_controller.game_mode:
            st.markdown("---")
            st.subheader(ts.translate('A5_game2_subheader', "Adivina la Exclusividad"))
            st.markdown(ts.translate('A5_game2_intro', "Algunas carreras se imparten en todo el país, mientras que otras son verdaderas rarezas. ¿Qué tan exclusiva crees que es la siguiente carrera?"))
            
            if df_oferta is not None and not df_oferta.empty:
                game_data_estimator = df_oferta.rename(columns={'carrera': 'name', 'Num_Universidades_Ofertan': 'value'})
                
                estimator_game_A5 = EstimatorMinigame(
                    game_id="A5_EstimatorExclusividad",
                    game_title=ts.translate('A5_game2_title', "El Estimador de Exclusividad"),
                    data=game_data_estimator,
                    content_callback=render_part1_ext,
                    num_rounds=4,
                    min_score_for_victory=200
                )
                estimator_game_A5.render()
            else:
                render_part1_ext()
        else:
            render_part1_ext()

    def render_part1_ext():
        if df_oferta is not None and not df_oferta.empty:
            st.markdown(ts.translate('A5_df_carreras_unicas_markdown_new', """
            Este gráfico agrupa las carreras según el número de universidades que las imparten en el curso {curso}.
            Cada punto representa una carrera. Pasa el ratón sobre un punto para ver su nombre. Las anotaciones en la parte superior
            indican cuántas carreras existen en cada grupo de exclusividad.
            """).format(curso=curso))
            
            fig = grouped_dot_plot(
                df_oferta,
                x='Num_Universidades_Ofertan',
                y='carrera',
                title=ts.translate('A5_chart_title_grouped_offer', 'Distribución de Carreras por Exclusividad de Oferta'),
                yaxis_title=ts.translate('A5_chart_yaxis_num_unis', 'Nº de Universidades que la Ofertan'),
                annotation_text=ts.translate('_carrers', 'carreras'),
                color_scale='Viridis_r'
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander(ts.translate('A5_expander_show_all_data', "Ver la tabla completa con todas las carreras")):
                st.dataframe(df_oferta, use_container_width=True, hide_index=True)

            ask_ai_component(
                analysis_context="List of degree programs with limited availability across universities.",
                key="a5_carreras_unicas",
                extra_data=[df_oferta],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.info(ts.translate('A5_info_no_limited_offer_data', "No se encontraron datos sobre carreras con oferta limitada."))

    def render_part2():
        st.markdown("---")
        st.subheader(ts.translate('A5_subheader_2', "Lupa en Carreras Clave: ¿Quién es Quién en la Formación Específica?"))
        st.markdown(ts.translate('A5_markdown_2', """
        Selecciona hasta 3 carreras de tu interés. El gráfico mostrará la evolución histórica de la matrícula
        para esas carreras, desglosada por cada universidad que las imparte. Esto nos permite comparar
        el peso y la trayectoria de diferentes instituciones en la formación de profesionales en campos específicos.
            
        *Si el gráfico parece muy denso, intenta seleccionar menos carreras o concéntrate en las tendencias generales de las universidades más grandes para cada carrera.*
        """))

        todas_carreras_sorted = sorted(df_main['carrera'].unique())
        default_carreras = []
        if todas_carreras_sorted:
            top_carreras_df = df_main.groupby('carrera')['matricula_total'].sum().nlargest(2)
            if not top_carreras_df.empty:
                default_carreras = top_carreras_df.index.tolist()
            else:
                default_carreras = todas_carreras_sorted[:min(2, len(todas_carreras_sorted))]

        carreras_seleccionadas = st.multiselect(
            ts.translate('A5_multiselect_carreras', "Carreras para comparar evoluciones por universidad:"),
            options=todas_carreras_sorted,
            default=default_carreras,
            max_selections=3,
            key="select_carreras_a5_uni_comparison"
        )

        if carreras_seleccionadas:
            with st.spinner(ts.translate('A5_spinner_2', "Generando gráfico comparativo por universidad...")):
                df_comparativa, status_comp = analisis_A5_comparativa(df_main, carreras_a_comparar=carreras_seleccionadas)

            if status_comp == "success" and df_comparativa is not None:
                fig = graficate_A5_comparativa(df_comparativa, ts)
                st.plotly_chart(fig, use_container_width=True, key="fig_a9_comparativa_unis")
                
                ask_ai_component(
                    analysis_context="Historical trends by university for the selected academic programs.",
                    key="a5_comparativa_unis_" + "_".join(sorted([c.replace(' ','_') for c in carreras_seleccionadas])),
                    extra_data=[df_comparativa],
                    translation=ts.translate('ask_ai_component')
                )
            else:
                st.warning(ts.translate('A5_warning_comparison_failed', "No se pudo generar el gráfico comparativo. Causa: {status}").format(status=status_comp))
        else:
            st.info(ts.translate('A5_no_carreras_selected', "Por favor, elige al menos una carrera para ver la comparativa."))
        
        st.markdown(ts.translate('A5_markdown_3', """
        ---
        **Visiones Estratégicas para la Red de Universidades:**
        *   **Potenciar la Excelencia:** Identificar universidades líderes en carreras clave puede guiar la inversión para convertirlas en centros de referencia nacional o internacional.
        *   **Optimizar Recursos:** El treemap y el análisis de ofertas únicas pueden revelar duplicidades innecesarias o, por el contrario, la necesidad de expandir la oferta de ciertas carreras en más regiones.
        *   **Colaboración Interinstitucional:** Conocer las fortalezas de cada una puede fomentar sinergias, programas conjuntos y movilidad estudiantil y profesoral.
        """))

    if game_controller.game_mode:
        st.subheader(ts.translate('A5_game1_subheader', "GeoGuesser Universitario"))
        st.markdown(ts.translate('A5_game1_intro', "Antes de analizar las universidades en detalle, ¿conoces su ubicación? ¡Demuéstralo!"))
        
        if df_ins is not None and not df_ins.empty:
            game_data_geo = df_ins[['nombre_institucion', 'provincia']].dropna()
            
            GeoGuesserMinigame(
                game_id="A5_GeoGuesserUbicacion",
                game_title=ts.translate('A5_game1_title', "Adivina la Provincia"),
                data=game_data_geo,
                content_callback=render_part1,
                num_rounds=2,
                min_score_for_victory=40
            ).render()
        else:
            render_part1()

        game1_finished = 'A5_GeoGuesserUbicacion' in game_controller.registered_games and game_controller.registered_games['A5_GeoGuesserUbicacion'].is_finished()
        game2_finished = 'A5_EstimatorExclusividad' in game_controller.registered_games and game_controller.registered_games['A5_EstimatorExclusividad'].is_finished()
        
        if game1_finished and game2_finished:
            render_part2()

    else:
        render_part1()
        render_part2()

### Mirando al Mañana (Proyecciones)
@st.fragment
def A6(df_main, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('A6_header_1', "🔭 Mirando al Mañana: ¿Qué Podríamos Esperar? (Proyecciones Futuras)"))
    st.markdown(ts.translate('A6_markdown_1', """
    Anticipar el futuro es un desafío, pero analizar las tendencias recientes nos permite trazar
    escenarios posibles. En esta sección, volveremos a examinar nuestros indicadores clave de matrícula,
    pero esta vez extendiendo nuestra mirada dos cursos académicos hacia adelante mediante proyecciones.

    ⚠️ **Una Brújula, no un Oráculo:** Es fundamental recordar que estas son **proyecciones**, no predicciones
    infalibles. Se basan en modelos de **Regresión Lineal simple aplicados a los últimos 6 años de datos históricos**
    (o menos, si los datos son insuficientes para una rama o carrera específica). Múltiples factores no contemplados
    en estos modelos (cambios de políticas, crisis económicas, nuevas demandas sociales, etc.) podrían
    alterar significativamente estas trayectorias. Utilicémoslas como una herramienta para la reflexión
    estratégica y la planificación proactiva, no como un destino escrito en piedra.
    """))
    st.markdown("---")

    def render_content():
        st.subheader(ts.translate('A6_subheader_1', "Horizonte Nacional: Proyección de la Matrícula Total"))
        with st.spinner(ts.translate('A6_spinner_1', "Calculando la proyección de matrícula nacional...")):
            df_hist_nac, df_proy_nac, status_nac, n_anos_reg_nac = analisis_A1(df_main, projection=True)

        if status_nac == "success_with_projection" and df_hist_nac is not None and df_proy_nac is not None and n_anos_reg_nac is not None:
            st.info(ts.translate('A6_info_1', "Las líneas discontinuas y los puntos en forma de diamante más allá del curso 2024-2025 representan las proyecciones."))
            fig_proy_nacional = graficate_A1(df_hist_nac, ts, df_proy_nac, n_anos_reg_nac)
            st.plotly_chart(fig_proy_nacional, use_container_width=True, key="fig_a6_proy_nacional")
            
            st.markdown(ts.translate('A6_markdown_national_explanation', """
            **Interpretando la Tendencia Nacional Proyectada:**

            El gráfico superior combina la evolución histórica de la matrícula (barras y línea sólida hasta el curso 2024-25) con una proyección para los dos cursos siguientes (línea discontinua con diamantes).

            *   **Punto de Partida:** La proyección comienza desde el último dato histórico registrado, que muestra una matrícula nacional de aproximadamente **205,000 estudiantes**.
            *   **Trayectoria Proyectada:** El modelo de regresión lineal, basado en la tendencia de los últimos años, sugiere una **continuación de la fase de ajuste o declive moderado** que se observa en el período más reciente.
            *   **Estimaciones Futuras:**
                *   Para el curso **2025-2026**, el modelo estima una matrícula que podría situarse en el rango de **195,000 a 215,000 estudiantes**.
                *   Hacia **2026-2027**, esta cifra podría descender hasta el entorno de los **185,000 a 190,000 estudiantes**.
            *   **Implicación Estratégica:** Si esta tendencia se materializa, plantea preguntas importantes para la planificación: ¿Cómo afectaría esto a la capacidad instalada en las universidades? ¿Requeriría una reevaluación de la asignación de recursos o nuevas estrategias de captación y retención de estudiantes a nivel nacional?
            """))
            
            ask_ai_component(
                analysis_context="Forecast of overall national enrollment figures.",
                key="a6_proy_nacional", extra_data=[df_hist_nac, df_proy_nac],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.warning(ts.translate('A6_warning_national_proj_failed', "No se pudo generar la proyección nacional. Estado: {status}").format(status=status_nac))
        
        st.markdown("---")

        st.subheader(ts.translate('A6_fig_A2_subheader', "Saberes del Mañana: Proyección por Rama de Ciencias"))
        with st.spinner(ts.translate('A6_fig_A2_spinner', "Calculando la proyección por ramas de ciencias...")):
            df_hist_ramas, _, df_proy_ramas, n_anos_reg_ramas = analisis_A2(df_main, projection=True)
        
        if df_proy_ramas is not None and df_hist_ramas is not None:
            fig_proy_ramas = graficate_A2_evolucion(df_hist_ramas, ts, df_proy_ramas, n_anos_reg_ramas) #type:ignore
            st.plotly_chart(fig_proy_ramas, use_container_width=True, key="fig_a6_proy_ramas")
            ask_ai_component(
                analysis_context="Forecast of student enrollment by scientific discipline.",
                key="a6_proy_ramas", extra_data=[df_hist_ramas, df_proy_ramas],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.warning(ts.translate('A6_warning_branches_proj_failed', "No se pudo generar la proyección por ramas."))

        st.markdown("---")

        st.subheader(ts.translate('A6_fig_A7_subheader_1', "Carreras Clave en el Horizonte: Proyección Interactiva"))
        st.markdown(ts.translate('A6_fig_A7_markdown_1', "Selecciona hasta 3 carreras de tu interés para visualizar su proyección de matrícula individual."))

        todas_carreras_sorted = sorted(df_main['carrera'].unique())
        default_carreras = []
        if todas_carreras_sorted:
            try:
                default_carreras = df_main.groupby('carrera')['matricula_total'].sum().nlargest(3).index.tolist()
            except Exception:
                default_carreras = todas_carreras_sorted[:min(3, len(todas_carreras_sorted))]

        carreras_seleccionadas = st.multiselect(
            ts.translate('A6_fig_A7_multiselect_1', "Selecciona carreras para proyectar:"),
            options=todas_carreras_sorted,
            default=default_carreras,
            max_selections=3,
            key="select_carreras_a6_proy"
        )

        if carreras_seleccionadas:
            with st.spinner(ts.translate('A6_fig_A7_spinner_1', "Calculando la proyección para las carreras seleccionadas...")):
                df_proy_carreras, msg_proy = analisis_A6(df_main, carreras_seleccionadas=carreras_seleccionadas)
            
            show_info(msg_proy)

            if df_proy_carreras is not None and not df_proy_carreras.empty:
                fig_proy_carreras = graficate_A6_proyeccion_carreras(df_proy_carreras, ts)
                st.plotly_chart(fig_proy_carreras, use_container_width=True, key="fig_a6_proy_carreras_dinamica")
                
                ask_ai_component(
                    analysis_context=f"Projection for the degree programs: {', '.join(carreras_seleccionadas)}.",
                    key="a6_proy_carreras_" + "_".join(sorted([c.replace(' ', '_') for c in carreras_seleccionadas])),
                    extra_data=[df_proy_carreras],
                    translation=ts.translate('ask_ai_component',{})
                )
            else:
                st.warning(ts.translate('a7_proy_warning', "No se pudieron generar datos para la proyección de: {careers}.").format(careers=', '.join(carreras_seleccionadas)))
        else:
            st.info(ts.translate('a7_void_info', "Selecciona al menos una carrera para ver su proyección."))

        st.markdown(ts.translate('a7_end_markdown', """
        ---
        **Planificando con Visión de Futuro:**
        Estas proyecciones, con todas sus limitaciones, son un insumo valioso para:
        *   Anticipar necesidades de **infraestructura y profesorado**.
        *   Debatir sobre la **asignación de plazas y recursos** entre diferentes áreas y carreras.
        *   Identificar áreas que podrían requerir **estrategias proactivas** para revertir tendencias negativas o para gestionar un crecimiento sostenible.
        *   Fomentar un diálogo informado sobre el **futuro de la oferta académica** en Cuba.
        """))

    if game_controller.game_mode:
        st.subheader(ts.translate('A6_game_subheader', "🔮 El Oráculo de la Matrícula"))
        st.markdown(ts.translate('A6_game_intro', """
        Antes de revelar las proyecciones del modelo, pongamos a prueba tu intuición como analista.
        Observa la trayectoria histórica de la matrícula nacional. Basado en esta tendencia,
        ¿qué crees que ocurrió en el último año registrado? ¿Continuó la tendencia, se estabilizó o se revirtió?
        """))
        
        df_hist_juego, _, _, _ = analisis_A1(df_main)
        if df_hist_juego is not None and len(df_hist_juego) >= 2:
            game_data_oracle = pd.DataFrame([{
                "name": ts.translate('A6_game_item_name', "Matrícula Nacional"),
                "x": df_hist_juego['ano_inicio_curso'].tolist(),
                "y": df_hist_juego['matricula_total'].tolist()
            }])

            OracleMinigame(
                game_id="A6_OracleNacional",
                game_title=ts.translate('A6_game_title', "Predice la Tendencia Nacional"),
                data=game_data_oracle,
                content_callback=render_content,
                min_score_for_victory=20
            ).render()
        else:
            render_content()
    else:
        render_content()

### Areas de Atención
@st.fragment
def A7(df_main, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('A7_header_1', "💡 Áreas de Atención: Desafíos y Oportunidades Específicas"))
    st.markdown(ts.translate('A7_markdown_1', """
    Más allá de las grandes tendencias, existen situaciones particulares en carreras y universidades
    que merecen una lupa especial. Algunas carreras pueden estar emergiendo con vigor, otras podrían
    haber concluido su ciclo de oferta, y un tercer grupo quizás lucha por atraer un número suficiente
    de estudiantes. Identificar estos casos no es señalar problemas, sino descubrir oportunidades
    para una gestión académica más precisa, ágil y adaptada a las realidades cambiantes.
    """))
    st.markdown("---")

    def render_content():
        with st.spinner(ts.translate('A7_spinner_1', "Identificando casos de atención específica...")):
            df_nuevas, df_cesadas, df_baja, umbral, status = analisis_A7(df_main)
        
        if status != "success":
            st.warning(ts.translate('A7_error_a8_analysis', "No se pudo completar el análisis de áreas de atención."))
            return

        st.subheader(ts.translate('A7_a8_subheader_1', "🌱 Sembrando el Futuro: Posibles Nuevas Ofertas o Reactivaciones"))
        if df_nuevas is not None and not df_nuevas.empty:
            st.markdown(ts.translate('A7_a8_markdown_1', """
            El siguiente gráfico muestra cuántas carreras nuevas o reactivadas se detectaron cada año. 
            Esto revela los períodos de mayor expansión o renovación de la oferta académica.
            """))
            fig_nuevas = graficate_A7_nuevas_ofertas(df_nuevas.copy(), ts)
            st.plotly_chart(fig_nuevas, use_container_width=True)
            
            with st.expander(ts.translate('A7_expander_new_offers', "Ver la lista completa de las {count} nuevas ofertas detectadas").format(count=len(df_nuevas))):
                df_nuevas_display = df_nuevas.rename(columns={
                    'university': ts.translate('_university', 'Universidad'),
                    'career': ts.translate('_career', 'Carrera'),
                    'detected_start_year': ts.translate('A7_col_detected_start_year', 'Año Inicio Detectado'),
                    'current_enrollment': ts.translate('A7_col_current_enrollment', 'Matrícula Actual')
                })
                st.dataframe(df_nuevas_display, use_container_width=True)

            ask_ai_component(
                analysis_context="Analysis of degree programs that appear to be new offerings or reactivations.",
                key="a7_nuevas_ofertas",
                extra_data=[df_nuevas],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.info(ts.translate('A7_info_no_new_offers', "No se identificaron carreras que cumplan claramente con el criterio de nueva oferta o reactivación."))
        
        st.markdown("---")

        st.subheader(ts.translate('A7_a8_subheader_2', "🍂 Ciclos que Concluyen: Posibles Ceses de Oferta"))
        if df_cesadas is not None and not df_cesadas.empty:
            st.markdown(ts.translate('A7_a8_markdown_2_revised', """
            Este gráfico resume cuántas carreras dejaron de tener matrícula por año, dándonos una idea 
            de los períodos con mayores ajustes o discontinuaciones en la oferta académica.
            """))
            fig_cesadas = graficate_A7_cesadas_ofertas(df_cesadas.copy(), ts)
            st.plotly_chart(fig_cesadas, use_container_width=True)

            with st.expander(ts.translate('A7_expander_ceased_offers', "Ver la lista completa de las {count} ofertas posiblemente cesadas").format(count=len(df_cesadas))):
                df_cesadas_display = df_cesadas.rename(columns={
                    'university': ts.translate('_university', 'Universidad'),
                    'career': ts.translate('_career', 'Carrera'),
                    'last_enrollment_year': ts.translate('A7_col_last_enrollment_year', 'Último Año con Matrícula')
                })

                st.dataframe(df_cesadas_display, use_container_width=True)

            ask_ai_component(
                analysis_context="Analysis of degree programs that seem to have been discontinued.",
                key="a7_cese_oferta",
                extra_data=[df_cesadas],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.info(ts.translate('A7_info_no_ceased_offers', "No se identificaron carreras que cumplan claramente con el criterio de cese de oferta."))
        
        st.markdown("---")
            
        curso_reciente = f"{int(df_main['ano_inicio_curso'].max())}-{int(df_main['ano_inicio_curso'].max()+1)}"
        
        st.subheader(ts.translate('A7_a8_subheader_3', "📉 Focos de Atención: Matrícula Reducida (Inferior a {umbral})").format(umbral=umbral))
        if df_baja is not None and not df_baja.empty:
            st.markdown(ts.translate('A7_a8_markdown_3_revised', """
            El siguiente gráfico agrupa las carreras según su nivel de matrícula en el curso {curso}. Cada punto representa
            una carrera en una universidad específica. Pasa el cursor sobre un punto para ver los detalles. 
            Esto nos ayuda a ver dónde se concentran los casos de matrícula más crítica (ej. 1 o 2 estudiantes).
            """).format(curso=curso_reciente))
            
            fig_baja = graficate_A7_baja_matricula(df_baja.copy(), ts, curso_reciente, umbral)
            st.plotly_chart(fig_baja, use_container_width=True)

            with st.expander(ts.translate('A7_expander_low_enrollment', "Ver la lista completa de las {count} carreras con matrícula baja").format(count=len(df_baja))):
                df_baja_display = df_baja.rename(columns={
                    'university': ts.translate('_university', 'Universidad'),
                    'career': ts.translate('_career', 'Carrera'),
                    'enrollment': ts.translate('A7_col_enrollment_last_year', 'Matrícula ({curso})').format(curso=curso_reciente)
                })
                st.dataframe(df_baja_display, use_container_width=True)

            ask_ai_component(
                analysis_context=f"Analysis of degree programs with minimal enrollment in the most recent year (under {umbral} students).",
                key="a7_baja_matricula",
                extra_data=[df_baja],
                translation=ts.translate('ask_ai_component',{})
            )
        else:
            st.info(ts.translate('A7_info_no_low_enrollment', "No se identificaron carreras con matrícula inferior a {umbral} (y >0) en el último año.").format(umbral=umbral))

        st.markdown(ts.translate('A7_conclusion_markdown_1', """
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
            *   **Estrategias Diferenciadas:** Dependiendo del diagnóstico, las acciones podrían ir desde la promoción focalizada, rediseño curricular, hasta la consideración de fusión con otras carreras o, en últi ma instancia, una discontinuación planificada si no se justifica su mantenimiento.

        Una gestión atenta a estos detalles permite optimizar recursos, responder mejor a las necesidades
        del país y asegurar la vitalidad y pertinencia de la oferta académica universitaria.
        """))

    if game_controller.game_mode:
        st.subheader(ts.translate('A7_game_subheader', "🕵️‍♂️ Encuentra el Foco de Atención"))
        st.markdown(ts.translate('A7_game_intro', """
        Entre las múltiples ofertas académicas de las universidades, algunas prosperan con cientos de estudiantes, mientras que otras luchan por mantenerse a flote. A continuación, te presentamos cuatro ofertas universitarias. Tres de ellas tienen una matrícula saludable, pero una es un "foco de atención" con una matrícula críticamente baja. ¿Puedes identificar al intruso?
        """))

        _, _, df_baja_game, umbral_game, status_game = analisis_A7(df_main)
        
        if status_game == 'success' and df_baja_game is not None and not df_baja_game.empty:
            ano_reciente = int(df_main['ano_inicio_curso'].max())
            df_reciente_game = df_main[df_main['ano_inicio_curso'] == ano_reciente]
            
            impostor = df_baja_game.sample(1).copy()
            impostor['category'] = 'Baja Matrícula'
            impostor['item'] = impostor['university'] + ' - ' + impostor['career']
            
            df_saludable = df_reciente_game[df_reciente_game['matricula_total'] >= 50].sample(3)
            df_saludable['category'] = 'Matrícula Saludable'
            df_saludable['item'] = df_saludable['entidad'] + ' - ' + df_saludable['carrera']
            
            game_data = pd.concat([
                impostor[['item', 'category']],
                df_saludable[['item', 'category']]
            ])
            
            impostor_game_A7 = ImpostorMinigame(
                game_id="A7_ImpostorMatriculaBaja",
                game_title=ts.translate('A7_game_title', "El Intruso de Matrícula Baja"),
                data=game_data,
                item_col='item',
                category_col='category',
                exclude_if_contains=False,
                content_callback=render_content,
                min_score_for_victory=25
            )
            impostor_game_A7.render()
        else:
            render_content()
    else:
        render_content()

### A6: Perfil Detallado de Carreras
@st.fragment
def B1(df_main, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('B1_header_1', "🔬 Playground: Perfil Detallado de Carrera"))
    st.markdown(ts.translate('B1_markdown_1', """
    Sumérgete en los detalles de la carrera que elijas. Descubre su evolución histórica,
    su tasa de crecimiento, y un panorama anual de las universidades y la composición de género.
    """))

    todas_carreras = sorted(df_main['carrera'].unique())
    carrera_sel = st.selectbox(
        ts.translate('B1_selectbox_label_1', "Selecciona una Carrera para analizar su perfil:"),
        options=todas_carreras,
        index=todas_carreras.index("MEDICINA") if "MEDICINA" in todas_carreras else 0,
        key="sel_carrera_b1_perfil"
    )

    if not carrera_sel:
        st.info(ts.translate('b1_info_select_career', "Por favor, selecciona una Carrera para continuar."))
        return

    st.markdown("---")
    
    with st.spinner(ts.translate('B1_spinner_1_hist', "Generando perfil histórico para {career}...").format(career=carrera_sel)):
        df_evol_genero, rama, status_hist = analisis_perfil_carrera_historico(df_main, carrera_sel)

    if status_hist != "success" or df_evol_genero is None:
        st.warning(f"No se pudo generar el perfil para {carrera_sel}. Estado: {status_hist}")
        return

    st.subheader(ts.translate('B1_subheader_1_hist', "Evolución y Crecimiento de: {career}").format(career=carrera_sel))
    st.markdown(f"**{ts.translate('B1_markdown_1_rama', 'Rama de Ciencias')}:** `{rama or 'N/D'}`")

    if not df_evol_genero.empty:
        fig_evol = graficate_B1_evolucion_genero(df_evol_genero, ts, carrera_sel)
        st.plotly_chart(fig_evol, use_container_width=True)
        
        df_cagr_data = df_evol_genero[['ano_inicio_curso', 'matricula_total']]
        anos_disponibles = sorted(df_cagr_data['ano_inicio_curso'].unique())
        if len(anos_disponibles) >= 2:
            start_year_cagr, end_year_cagr = st.select_slider(
                ts.translate('B1_slider_label_cagr', "Selecciona el rango de años para el cálculo del CAGR:"),
                options=anos_disponibles, value=(anos_disponibles[0], anos_disponibles[-1])
            )
            cagr_info = calcular_cagr(df_cagr_data, start_year_cagr, end_year_cagr)
            if cagr_info.get("status") == "SUCCESS":
                st.metric(label=f"CAGR ({start_year_cagr}-{end_year_cagr})", value=f"{cagr_info.get('cagr_value', 0.0) * 100:.2f}%")
    else:
        st.info(ts.translate('B1_info_no_evolution_data', "No hay datos de evolución disponibles para esta carrera."))

    st.markdown("---")

    st.subheader(ts.translate('B1_subheader_2_snapshot', "Análisis Anual Detallado"))
    
    anos_disponibles_snapshot = sorted(df_evol_genero['ano_inicio_curso'].unique())
    anio_sel = st.select_slider(
        ts.translate('B1_slider_label_snapshot', "Selecciona un año para ver los detalles:"),
        options=anos_disponibles_snapshot,
        value=anos_disponibles_snapshot[-1] if anos_disponibles_snapshot else None
    )

    if anio_sel:
        with st.spinner(ts.translate('B1_spinner_2_snapshot', "Cargando datos para el año {year}...").format(year=anio_sel)):
            df_unis, datos_genero, status_snap = analisis_perfil_carrera_snapshot(df_main, carrera_sel, anio_sel)
        
        if status_snap == "success":
            col_genero, col_unis = st.columns(2, gap="large")
            with col_genero:
                if datos_genero and datos_genero.get('Total', 0) > 0:
                    fig_pie_genero = graficate_B1_distribucion_genero(datos_genero, ts, carrera_sel, anio_sel)
                    st.plotly_chart(fig_pie_genero, use_container_width=True)
                else:
                    st.info(ts.translate('B1_info_no_gender_data_pie', "Sin datos de género para este año."))
            with col_unis:
                if df_unis is not None and not df_unis.empty:
                    fig_bar_unis = graficate_B1_distribucion_unis(df_unis, ts, carrera_sel)
                    st.plotly_chart(fig_bar_unis, use_container_width=True)
                else:
                    st.info(ts.translate('b1_info_no_universities_data_year', "Ninguna universidad registró matrícula en este año."))
        else:
            st.warning(ts.translate('b1_warning_no_data_for_year', "No se encontraron datos para la carrera '{career}' en el año {year}.").format(career=carrera_sel, year=anio_sel))

    st.markdown("---")
    ask_ai_component(
        analysis_context=f"Detailed profile of the degree program: {carrera_sel}. Snapshot year: {anio_sel or 'N/A'}.",
        key=f"b1_perfil_carrera_{carrera_sel.replace(' ','_')}",
        extra_data=[df_evol_genero, df_unis, datos_genero],
        translation=ts.translate('ask_ai_component', {})
    )

### A6: Guía Instituciones
@st.fragment
def B2(df_main, df_ins, game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('b2_header', "🗺️ Guía de Instituciones: Explora la Oferta Académica por Localidad"))
    st.markdown(ts.translate('b2_intro', """
    Descubre las instituciones de educación superior en Cuba, filtrando por provincia y municipio.
    Para cada universidad, encontrarás información general y la oferta académica por ramas y carreras
    en el año que selecciones.
    """))

    if df_ins.empty:
        st.error(ts.translate('b2_error_no_institutions_data', "Los datos de instituciones no están disponibles. Esta sección no puede mostrarse."))
        return
    if df_main.empty:
        st.error(ts.translate('b2_error_no_enrollment_data', "Los datos de matrícula no están disponibles. La información de oferta será limitada."))
        
    st.subheader(ts.translate('b2_subheader_filters', "Filtros de Búsqueda:"))
    col_filtro1, col_filtro2 = st.columns(2)

    all_provinces_text = ts.translate('_all_provinces', "TODAS LAS PROVINCIAS")
    all_municipalities_text = ts.translate('_all_municipalities', "TODOS LOS MUNICIPIOS")

    with col_filtro1:
        provincias_disponibles = [all_provinces_text] + sorted(df_ins['provincia'].unique().tolist())
        provincia_sel = st.selectbox(
            ts.translate('b2_label_province', "Provincia:"),
            options=provincias_disponibles,
            key="sel_prov_b2_guia"
        )

    with col_filtro2:
        municipios_disponibles = [all_municipalities_text]
        if provincia_sel != all_provinces_text:
            municipios_de_provincia = sorted(df_ins[df_ins['provincia'] == provincia_sel]['municipio'].unique().tolist())
            municipios_disponibles.extend(municipios_de_provincia)

        municipio_sel = st.selectbox(
            ts.translate('b2_label_municipality', "Municipio:"),
            options=municipios_disponibles,
            key="sel_mun_b2_guia",
            disabled=(provincia_sel == all_provinces_text)
        )

    pattern_sel = st.text_input(
        ts.translate('b2_label_search_pattern', "Buscar por nombre o sigla de institución (filtro visual):"),
        key="sel_patron_b2"
    )
    st.markdown("---")

    provincia_para_filtrar = None if provincia_sel == all_provinces_text else provincia_sel
    municipio_para_filtrar = None if municipio_sel == all_municipalities_text else municipio_sel

    with st.spinner(ts.translate('b2_spinner_loading', "Cargando guía de instituciones...")):
        df_guia_basic, curso_reciente_str_basic, status_basic = analisis_guia_universidades_basic(
            df_instituciones=df_ins,
            df_matricula=df_main,
            provincia_seleccionada=provincia_para_filtrar,
            municipio_seleccionado=municipio_para_filtrar
        )
    
    if status_basic != "success" or df_guia_basic is None:
        st.warning(ts.translate('b2_warning_basic_analysis_failed', "No se pudo cargar la lista básica de instituciones. Estado: {status}").format(status=status_basic))
        return

    df_guia_filtrado_nombre = df_guia_basic
    if pattern_sel:
        df_guia_filtrado_nombre = df_guia_basic[
            df_guia_basic['nombre_institucion'].str.contains(pattern_sel, case=False, na=False) |
            df_guia_basic['sigla_institucion'].str.contains(pattern_sel, case=False, na=False)
        ]
    
    n_mostradas = df_guia_filtrado_nombre['nombre_institucion'].nunique()
    n_totales = df_guia_basic['nombre_institucion'].nunique()
    
    st.info(ts.translate(
        'b2_info_showing_unis',
        "Mostrando {shown} de {total} institución(es) ({last_year})."
    ).format(shown=n_mostradas, total=n_totales, last_year=curso_reciente_str_basic))

    anos_disponibles_matricula = sorted(df_main['ano_inicio_curso'].unique().tolist())
    if not anos_disponibles_matricula:
        st.warning(ts.translate('b2_warning_no_years_for_detail', "No hay años de matrícula disponibles para ver detalles."))
        return
        
    ano_seleccionado_detalle = st.select_slider(
        ts.translate('b2_slider_year_detail', "Selecciona el año para ver la oferta académica detallada:"),
        options=anos_disponibles_matricula,
        value=anos_disponibles_matricula[-1],
        key="slider_uni_detail_year"
    )
    curso_seleccionado_detalle_str = f"{ano_seleccionado_detalle}-{ano_seleccionado_detalle+1}" #type:ignore
    
    if df_guia_filtrado_nombre.empty:
        st.info(ts.translate('b2_info_no_unis_matched_filters', "No se encontraron instituciones que coincidan con los filtros aplicados."))
    else:

        for nombre_uni, df_uni_row in df_guia_filtrado_nombre.iterrows():
            title_expander = f"🏛️ {df_uni_row['nombre_institucion']} ({df_uni_row['sigla_institucion']})"
            detalles_loc_exp = [d for d in [df_uni_row.get('municipio'), df_uni_row.get('provincia')] if d]
            if detalles_loc_exp:
                title_expander += f" | {', '.join(detalles_loc_exp)}"
            if pd.notna(df_uni_row.get('ano_creacion')):
                title_expander += f" ({ts.translate('_founded_in', 'Fundada en')} {int(df_uni_row['ano_creacion'])})"
            
            with st.expander(title_expander):
                col_info_basica, col_genero_pastel_uni = st.columns([2, 1])
                #st.markdown(datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S'))
                with col_info_basica:
                    st.markdown(f"**{ts.translate('_organism', 'Organismo')}:** `{df_uni_row.get('organismo', 'N/D')}`")
                    st.markdown(f"**{ts.translate('_address', 'Dirección')}:** *{df_uni_row.get('direccion_fisica', 'N/D')}*")
                    st.markdown(f"**{ts.translate('_main_modality', 'Modalidad Principal')}:** `{df_uni_row.get('modalidad_estudio', 'N/D')}`")
                
                df_oferta_uni, datos_genero_uni, status_offer = get_uni_academic_offer(
                    df_main, df_uni_row['sigla_institucion'], ano_seleccionado_detalle #type:ignore
                )

                with col_genero_pastel_uni:
                    if status_offer == "success" and datos_genero_uni and datos_genero_uni.get('Total', 0) > 0:
                        fig_pie_genero_uni = graficate_B2_distribucion_genero_uni(datos_genero_uni, ts, curso_seleccionado_detalle_str)
                        st.plotly_chart(fig_pie_genero_uni, use_container_width=True)
                    else:
                        st.caption(ts.translate('b2_caption_no_gender_data_for_year', "Sin datos de género disponibles para {curso}.").format(curso=curso_seleccionado_detalle_str))
                
                st.markdown("---")
                st.markdown(ts.translate('b2_markdown_academic_offering', "**Oferta Académica ({curso}, ramas y carreras con matrícula):**").format(curso=curso_seleccionado_detalle_str))

                if status_offer == "success" and df_oferta_uni is not None and not df_oferta_uni.empty:
                    for nombre_rama, df_rama_group in df_oferta_uni.groupby('rama_ciencias', sort=False):
                        st.markdown(f"##### <span style='color: #1E90FF;'>►</span> {nombre_rama}", unsafe_allow_html=True)
                        
                        df_display = df_rama_group[['carrera', 'Matricula_Carrera_Anio']].rename(columns={
                            'carrera': ts.translate('_career', 'Carrera'),
                            'Matricula_Carrera_Anio': ts.translate('_enrollment', 'Matrícula')
                        }).set_index(ts.translate('_career', 'Carrera'))
                        
                        st.dataframe(df_display, use_container_width=True)
                else:
                    st.info(ts.translate('b2_info_no_branches_for_year', "Esta institución no tiene ramas de ciencias con oferta activa o carreras con matrícula reportada para {curso}.").format(curso=curso_seleccionado_detalle_str))
    
    st.markdown('---')
    ask_ai_component(
        analysis_context=f"Analysis of the institutions guide. Applied filters — Province: {provincia_sel}, Municipality: {municipio_sel}, Year: {ano_seleccionado_detalle}.",
        key="b2_guia_instituciones",
        extra_data=[df_guia_filtrado_nombre],
        translation=ts.translate('ask_ai_component', {})
    )

### Conclusiones
@st.fragment
def conclusion(game_controller: GameController, ts:Translator, **kwargs):
    st.header(ts.translate('conclusion_header', "🏁 Conclusiones y Horizontes Futuros: Forjando la Universidad del Mañana"))
    st.markdown(ts.translate('conclusion_intro', """
    Hemos viajado a través de una década de datos, explorando el complejo ecosistema
    de la educación superior en Cuba. Ya sea como analista o como explorador, cada gráfico desbloqueado y cada desafío superado 
    ha sido una pieza de un rompecabezas más grande: la historia de miles de aspiraciones, de esfuerzos institucionales
    y de la incesante búsqueda del conocimiento que define a nuestra nación.

    Este análisis no es un punto final, sino un faro que ilumina el camino recorrido y nos ayuda
    a discernir los senderos que se abren ante nosotros.
    """))
    st.success(ts.translate(
        'conclusion_success_message',
        "**La información es poder, y el poder de estos datos reside en nuestra capacidad para transformarlos en acción sabia y visión estratégica.**"
    ))
    st.markdown("---")

    st.subheader(ts.translate('conclusion_findings_subheader', "🌟 Destellos del Viaje: Principales Hallazgos"))
    hallazgos_text = ts.translate('conclusion_findings_text', """
    Al mirar atrás en nuestro análisis, emergen varios faros que guían nuestra comprensión:

    1.  **El Pulso Dinámico de la Nación:** La matrícula universitaria nacional ha mostrado una notable capacidad de expansión, alcanzando picos significativos a principios de la década de 2020, seguida de una fase de ajuste más reciente. Esta fluctuación nos recuerda la sensibilidad del sistema a factores contextuales y la necesidad de una planificación flexible. *(Ref. Sección 1)*

    2.  **El Corazón Médico y el Alma Pedagógica:** Las **Ciencias Médicas** se consolidan como la columna vertebral en términos de volumen estudiantil, un testimonio de su importancia estratégica. Las **Ciencias Pedagógicas**, por su parte, han demostrado un dinamismo extraordinario, con un crecimiento masivo seguido de una contracción, reflejando posibles cambios en la demanda o en las políticas de formación docente. *(Ref. Sección 2)*

    3.  **El Ascenso de Nuevas Vocaciones:** El análisis de crecimiento (CAGR) ha revelado el despegue impresionante de carreras como **Servicios Estomatológicos** y el vigor de varias **Ingenierías** (Artística, Procesos Agroindustriales, Informática), señalando posibles nuevas fronteras de interés y demanda laboral. *(Ref. Sección 3)*

    4.  **Avances y Desafíos en la Equidad de Género:** Si bien Cuba exhibe una alta participación femenina en la educación superior, con muchas ramas y carreras mostrando una mayoría de mujeres, persisten desafíos significativos. La subrepresentación femenina en las **Ciencias Técnicas** e **Ingenierías específicas**, así como en **Ciencias de la Cultura Física y el Deporte**, nos llama a redoblar esfuerzos para construir un panorama verdaderamente equitativo. *(Ref. Sección 4)*

    5.  **La Riqueza de la Diversidad Institucional:** Cada universidad aporta su matiz único al sistema. Hemos visto desde grandes centros multidisciplinarios hasta instituciones con una marcada especialización (como las Universidades de Ciencias Médicas). La identificación de carreras con oferta limitada subraya la importancia de una red universitaria coordinada y estratégicamente distribuida. *(Ref. Sección 5)*

    6.  **Una Mirada Prudente al Mañana:** Las proyecciones, aunque sujetas a la incertidumbre inherente al futuro, sugieren una posible continuación de la fase de ajuste en la matrícula general y en varias ramas y carreras clave. Esto no es un augurio, sino una invitación a la preparación y a la acción proactiva. *(Ref. Sección 6)*

    7.  **La Importancia de los Detalles:** El análisis de "Áreas de Atención" nos ha recordado que la salud del sistema también reside en la vitalidad de cada uno de sus componentes, incluyendo las carreras emergentes, aquellas con matrícula reducida o las que podrían estar concluyendo su ciclo. *(Ref. Sección 7)*
    """)
    st.markdown(hallazgos_text)
    st.markdown("---")

    st.subheader(ts.translate(
        'conclusion_recommendations_subheader',
        "🧭 Trazando la Carta de Navegación: Recomendaciones Estratégicas"
    ))

    recomendaciones_text = ts.translate('conclusion_recommendations_text', """
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
    st.markdown(recomendaciones_text)
    st.markdown("---")
        
    st.header(ts.translate('conclusion_final_header', "✨ Un Legado Continuo, Un Futuro Brillante"))
    st.markdown(ts.translate('conclusion_final_paragraph', """
    El análisis de estos datos no es meramente un ejercicio académico; es un acto de responsabilidad
    y un compromiso con el futuro. Las Universidades Cubanas, cada una con su rica historia y su papel trascendental
    en la sociedad, tiene ante sí el desafío y la oportunidad de seguir evolucionando, adaptándose
    e innovando.
    
    Esperamos que estos datos los inspire a todos a trabajar juntos por una educación
    superior que no solo responda a las necesidades del presente, sino que activamente modele
    un mañana más próspero, justo y lleno de conocimiento para todos los jóvenes Cubanos.
    """))

    if 'balloons_shown' not in st.session_state:
        st.session_state.balloons_shown = True
        st.balloons()
    
    context_conclusion_ia = (
        "This is the conclusions and final recommendations section of the analysis on higher education in Cuba. "
        "Below are the main findings and the strategic recommendations derived from the data. "
        "Your role is to discuss these points, offer additional perspectives, or respond to questions about these conclusions."
        "\n\n--- MAIN FINDINGS ---\n"
        f"{hallazgos_text}"
        "\n\n--- STRATEGIC RECOMMENDATIONS ---\n"
        f"{recomendaciones_text}"
    )

    ask_ai_component(
        analysis_context=context_conclusion_ia,
        key="final_conclusions",
        translation=ts.translate('ask_ai_component',{})
    )