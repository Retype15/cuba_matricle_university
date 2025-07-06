import streamlit as st
import pandas as pd
import plotly.express as px
from .game_engine import Minigame, RowBasedMinigame
from streamlit_sortables import sort_items
from typing import Callable, Any

# --- Funciones Complementarias ---
def trend_comparison(y_series: list | pd.Series) -> str:
    if len(y_series) < 2: return 'stable'
    change = y_series[-1] - y_series[-2]
    percent_change = (change / y_series[-2]) * 100 if y_series[-2] != 0 else 0
    if percent_change > 2: return 'up'
    if percent_change < -2: return 'down'
    return 'stable'

# --- Clases de Minijuegos ---  

class SimpleQuestionMinigame(RowBasedMinigame):
    """Un minijuego simple de pregunta con opciones."""
    POINTS_FOR_CORRECT = 10

    #def prepare_round_data(self, round_index: int) -> pd.Series: return self.data.iloc[round_index] #type:ignore

    def display_instructions(self):
        st.info(f"{self.t.get('minigame_prefix', 'Minijuego:')} {self.game_title}", icon="🎮")

    def display_game_body(self, round_data: pd.Series) -> str:
        st.write(round_data['question'])
        return st.radio(self.t.get('choose_your_answer', "Elige tu respuesta:"),
                        options=round_data['options'], key=f"radio_{self.game_id}_{round_data.name}",
                        label_visibility="collapsed")

    def calculate_score(self, user_answer, round_data: pd.Series) -> tuple[int, bool]:
        is_correct = (user_answer == round_data['correct_answer'])
        return self.POINTS_FOR_CORRECT if is_correct else 0, is_correct

    def display_round_feedback(self, round_result: dict, round_number: int):
        data = round_result['round_data']
        if round_result['was_correct']:
            st.success(f"¡Correcto! La respuesta era **{data['correct_answer']}**.", icon="✅")
        else:
            st.error(f"Tu respuesta fue **{round_result['user_answer']}**, pero la correcta era **{data['correct_answer']}**.", icon="❌")

class DataDuelMinigame(Minigame):
    """Compara entre dos opciones."""
    POINTS_FOR_CORRECT = 10

    def __init__(self, *, comparison_func: Callable[[Any, Any], bool] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.comparison_func = comparison_func

    def display_instructions(self): st.subheader(f"⚔️ {self.t.get('data_duel_title', 'Duelo de Datos')}")
    
    def prepare_round_data(self, round_index: int) -> dict:
        if self.data is None: raise ValueError("DataDuelMinigame requiere un DataFrame.")
        sample = self.data.sample(2, replace=False)
        item1, item2 = sample.iloc[0], sample.iloc[1]
        winner_is_item1 = self.comparison_func(item1, item2) if self.comparison_func else item1['value'] > item2['value']
        correct_option = item1['name'] if winner_is_item1 else item2['name']
        return {"option1": item1['name'], "value1": item1['value'], "option2": item2['name'], "value2": item2['value'], "correct_option": correct_option, "question_text": self.t.get('duel_question', "¿Cuál tiene un valor mayor?")}

    def display_game_body(self, round_data: dict) -> None:
        st.markdown(f"##### {round_data['question_text']}"); return None

    def _render_submission_ui(self, round_data: dict):
        self.display_game_body(round_data)
        col1, col2 = st.columns(2)
        user_choice = None
        key_prefix = f"btn_{self.game_id}_{self.current_round}"
        if col1.button(f"**{round_data['option1']}**", key=f"{key_prefix}_1", use_container_width=True): user_choice = round_data['option1']
        if col2.button(f"**{round_data['option2']}**", key=f"{key_prefix}_2", use_container_width=True): user_choice = round_data['option2']
        if user_choice: self._process_submission(user_choice, round_data)

    def calculate_score(self, user_answer, round_data: dict) -> tuple[int, bool]:
        is_correct = (user_answer == round_data['correct_option'])
        return (self.POINTS_FOR_CORRECT, True) if is_correct else (0, False)

    def display_round_feedback(self, round_result: dict, round_number: int):
        with st.container(border=True):
            data = round_result['round_data']
            icon = "✅" if round_result['was_correct'] else "❌"
            st.markdown(f"**Ronda {round_number}:** {data['question_text']} {icon}")
            if not round_result['was_correct']: st.write(f"Tu elección: `{round_result['user_answer']}`")
            st.info(f"**Respuesta correcta: `{data['correct_option']}`**\n\n`{data['option1']}`: **{data['value1']}**\n\n`{data['option2']}`: **{data['value2']}**")

class ClassifierMinigame(Minigame):
    """Ordena una lista de ítems."""
    POINTS_PER_CORRECT_POSITION = 15
    POINTS_PER_ADJACENT = 5
    PERFECT_BONUS = 25
    
    def __init__(self, *, difficulty: int = 5, sorting_func: Callable[[pd.DataFrame], pd.DataFrame] | None = None, **kwargs):
        super().__init__(num_rounds=1, **kwargs)
        if self.data is None: raise ValueError("ClassifierMinigame requiere un DataFrame.")
        self.difficulty = min(difficulty, len(self.data))
        self.sorter = sorting_func if sorting_func else lambda df: df.sort_values(by='value', ascending=False)
        self.value_map = pd.Series(self.data.value.values, index=self.data.name).to_dict()

    def display_instructions(self):
        st.subheader(f"📊 {self.t.get('classifier_title', 'El Clasificador')}")
        st.info(self.t.get('classifier_drag_info', "💡 Arrastra los elementos para ordenarlos de mayor a menor."), icon="ℹ️")

    def prepare_round_data(self, round_index: int) -> dict:
        if self.data is None: raise ValueError("ClassifierMinigame requiere un DataFrame.")
        sample_df = self.data.sample(n=self.difficulty, replace=False)
        return {'items_to_sort': sample_df['name'].tolist(), 'correct_order': self.sorter(sample_df)['name'].tolist()}

    def display_game_body(self, round_data: dict) -> list:
        return sort_items(round_data['items_to_sort'], direction='vertical')
    
    def calculate_score(self, user_answer: list, round_data: dict) -> tuple[int, bool]:
        correct_order, score = round_data['correct_order'], 0
        perfect = (user_answer == correct_order)
        for i, item in enumerate(user_answer):
            if item == correct_order[i]: score += self.POINTS_PER_CORRECT_POSITION
            elif item in correct_order and abs(i - correct_order.index(item)) == 1: score += self.POINTS_PER_ADJACENT
        if perfect: score += self.PERFECT_BONUS
        return score, perfect

    def display_round_feedback(self, round_result: dict, round_number: int):
        with st.container(border=True):
            user_order, correct_order = round_result['user_answer'], round_result['round_data']['correct_order']
            st.markdown(f"**Resultados del Clasificador**")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Tu Orden**")
                for i, item in enumerate(user_order):
                    mark = "✅" if item == correct_order[i] else "➖"
                    st.markdown(f"`{i+1}.` {mark} {item} *({self.value_map.get(item, 'N/A')})*")
            with col2:
                st.write("**Orden Correcto**")
                for i, item in enumerate(correct_order):
                    st.markdown(f"`{i+1}.` ✅ {item} *({self.value_map.get(item, 'N/A')})*")

class OracleMinigame(RowBasedMinigame):
    """Predice la tendencia futura."""
    POINTS_FOR_CORRECT_PREDICTION = 25
    
    def __init__(self, *, comparison_func: Callable[[list], str] = trend_comparison, **kwargs):
        super().__init__(**kwargs)
        self.comparison_func = comparison_func

    #def prepare_round_data(self, round_index: int) -> pd.Series: return self.data.iloc[round_index] #type:ignore
    
    def display_instructions(self): st.subheader(f"🔮 {self.t.get('oracle_title', 'El Oráculo')}")

    def display_game_body(self, round_data: pd.Series) -> None:
        st.markdown(f"**{round_data['name']}:** {self.t.get('oracle_question', 'Observa la evolución y predice la tendencia.')}")
        chart_df = pd.DataFrame({'x': round_data['x'][:-1], 'y': round_data['y'][:-1]})
        fig = px.line(chart_df, x='x', y='y', markers=True, template="plotly_dark")
        fig.update_layout(title="Evolución... ¿Qué pasará después?", xaxis_title="Año", yaxis_title="Matrícula")
        st.plotly_chart(fig, use_container_width=True)
        return None

    def _render_submission_ui(self, round_data: pd.Series):
        self.display_game_body(round_data)
        st.write("Elige tu predicción:")
        cols, user_prediction = st.columns(3), None
        button_map = {'up': {'label': 'Subirá', 'icon': '📈'}, 'stable': {'label': 'Estable', 'icon': '➖'}, 'down': {'label': 'Bajará', 'icon': '📉'}}
        key_prefix = f"btn_{self.game_id}_{self.current_round}"
        if cols[0].button(f"{button_map['up']['label']} {button_map['up']['icon']}", key=f"{key_prefix}_up", use_container_width=True): user_prediction = 'up'
        if cols[1].button(f"{button_map['stable']['label']} {button_map['stable']['icon']}", key=f"{key_prefix}_stable", use_container_width=True): user_prediction = 'stable'
        if cols[2].button(f"{button_map['down']['label']} {button_map['down']['icon']}", key=f"{key_prefix}_down", use_container_width=True): user_prediction = 'down'
        if user_prediction: self._process_submission(user_prediction, round_data)

    def calculate_score(self, user_answer, round_data: pd.Series) -> tuple[int, bool]:
        actual_trend = self.comparison_func(round_data['y'])
        return self.POINTS_FOR_CORRECT_PREDICTION if (user_answer == actual_trend) else 0, user_answer == actual_trend

    def display_round_feedback(self, round_result: dict, round_number: int):
        with st.container(border=True):
            user_prediction, data = round_result['user_answer'], round_result['round_data']
            actual_trend, icon = self.comparison_func(data['y']), "✅" if round_result['was_correct'] else "❌"
            st.markdown(f"**Ronda {round_number} ({data['name']}):** {icon}")
            map_pred_text = {'up': "Subirá 📈", 'stable': "Estable ➖", 'down': "Bajará 📉"}
            st.write(f"Tu predicción: **{map_pred_text[user_prediction]}**")
            st.write(f"Resultado real: **{map_pred_text[actual_trend]}**")
            chart_df = pd.DataFrame({'x': data['x'], 'y': data['y']})
            fig = px.line(chart_df, x='x', y='y', markers=True, template="plotly_dark")
            fig.add_shape(type="line", x0=chart_df['x'].iloc[-2], y0=chart_df['y'].iloc[-2], x1=chart_df['x'].iloc[-1], y1=chart_df['y'].iloc[-1], line=dict(color="yellow", width=4, dash="dot"))
            fig.update_layout(title="Resultado Completo Revelado", xaxis_title="Año", yaxis_title="Matrícula")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    from game_engine import GameController 

    st.set_page_config(layout="wide")
    st.title("Test de Minijuegos (Prueba Completa)")
    
    mock_translations = {
        'progress_header': '🚀 Tu Aventura',
        'DataDuelMinigame': {
            'data_duel_title': 'Duelo de Titanes',
            'duel_question': '¿Qué entidad tiene el mayor valor?',
        },
        'OracleMinigame': {
            'oracle_title': 'El Oráculo Financiero',
            'oracle_question': 'Observa la tendencia de la acción y predice su movimiento para el próximo trimestre.',
            'oracle_choice_up': 'Sube',
            'oracle_choice_stable': 'Se Mantiene',
            'oracle_choice_down': 'Baja',
        },
        'classifier_title': 'El Gran Clasificador', # Esta se sobreescribirá si se pasa en la instancia.
        'feedback_victory': "¡Éxito! Lograste {total_score} puntos, ¡eres un experto!",
        'feedback_defeat': "¡No te rindas! Obtuviste {total_score} puntos. ¡Puedes mejorar!",
    }
    
    game_controller = GameController(translation=mock_translations)
    
    with st.sidebar:
        game_controller.display_mode_toggle()
        game_controller.display_score_panel()
    st.subheader("🛠️ Panel de Depuración")
    game_controller.display_debug_panel()
        
    def cb():
        """Una función de callback simple para demostrar contenido post-juego."""
        st.success("¡Contenido del análisis detallado revelado! Aquí podrías mostrar gráficos complejos o insights.")


    quiz_data = pd.DataFrame([
        {'question': '¿Cuál es la capital de España?', 'options': ['Barcelona', 'Madrid', 'Valencia'], 'correct_answer': 'Madrid'},
        {'question': '¿Cuál es el río más largo de Sudamérica?', 'options': ['Paraná', 'Orinoco', 'Amazonas'], 'correct_answer': 'Amazonas'},
        {'question': '¿Cuántos lados tiene un hexágono?', 'options': ['5', '6', '7'], 'correct_answer': '6'},
        {'question': '¿Qué planeta es conocido como el Planeta Rojo?', 'options': ['Tierra', 'Marte', 'Júpiter'], 'correct_answer': 'Marte'},
        {'question': '¿Cuál es el océano más grande del mundo?', 'options': ['Atlántico', 'Índico', 'Pacífico'], 'correct_answer': 'Pacífico'},
    ])

    duel_df = pd.DataFrame({
        'name': ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa D', 'Empresa E'],
        'value': [1200000, 850000, 1500000, 980000, 700000]
    })

    classifier_data = {
        'name': ['Python', 'Java', 'C++', 'JavaScript', 'Go', 'Rust', 'Ruby', 'Swift'],
        'value': [100, 90, 85, 95, 70, 60, 50, 75]
    }
    classifier_df = pd.DataFrame(classifier_data)

    oracle_df = pd.DataFrame({
        'name': ['Acción X', 'Acción Y', 'Acción Z'],
        'x': [
            [2020, 2021, 2022, 2023, 2024, 2025],
            [2020, 2021, 2022, 2023, 2024, 2025],
            [2020, 2021, 2022, 2023, 2024, 2025]
        ],
        'y': [
            [50, 55, 65, 60, 70, 100],  # Tendencia ascendente
            [100, 95, 90, 85, 80, 10], # Tendencia descendente
            [120, 122, 118, 120, 121, 122] # Tendencia estable
        ]
    })

    # --- Pestañas para cada Minijuego ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Simple Pregunta", "Duelo de Datos", "El Clasificador", "El Oráculo", "Quiz de Victoria"])

    with tab1:
        st.header("1. Minijuego de Pregunta Simple")
        SimpleQuestionMinigame(
            game_id="simple_question_test",
            game_title="Cuestionario Básico",
            data=quiz_data,
            num_rounds=2, # 2/5
            content_callback=cb
        ).render()

    with tab2:
        st.header("2. Duelo de Datos")
        DataDuelMinigame(
            game_id="duel_test",
            game_title="Duelo de Inversiones", # Este título sobrescribe el general por clase
            data=duel_df,
            num_rounds=3,
            content_callback=cb
        ).render()

    with tab3:
        st.header("3. El Clasificador")
        ClassifierMinigame(
            game_id="classifier_test",
            game_title="Ranking de Tecnologías",
            data=classifier_df,
            content_callback=cb,
            difficulty=5,
            translation={'classifier_title': 'El Clasificador de Lenguajes (Personalizado!)'}
        ).render()

    with tab4:
        st.header("4. El Oráculo")
        OracleMinigame(
            game_id="oracle_test",
            game_title="Predicciones de Mercado",
            data=oracle_df,
            num_rounds=2, #2/3
            content_callback=cb
        ).render()

    with tab5:
        st.header("5. Quiz con Condición de Victoria/Derrota")
        SimpleQuestionMinigame(
            game_id="victory_test",
            game_title="El Reto del Saber",
            data=quiz_data.sample(n=3, random_state=42), # 3 preguntas fijas para la prueba
            num_rounds=3,
            min_score_for_victory=25
        ).render()