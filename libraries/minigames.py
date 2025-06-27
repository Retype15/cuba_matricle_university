# --- START OF FILE minigames.py ---

import streamlit as st
import pandas as pd
import plotly.express as px
from game_engine import Minigame
from streamlit_sortables import sort_items
from typing import Callable, Any

# --- Funciones de Ayuda ---

def trend_comparison(y_series: list | pd.Series) -> str:
    """Determina si la tendencia es 'up', 'down', o 'stable'."""
    if len(y_series) < 2: return 'stable'
    change = y_series[-1] - y_series[-2]
    percent_change = (change / y_series[-2]) * 100 if y_series[-2] != 0 else 0
    if percent_change > 2: return 'up'
    if percent_change < -2: return 'down'
    return 'stable'

# --- Implementaciones de Minijuegos ---

class SimpleQuestionMinigame(Minigame):
    """Un minijuego simple de pregunta con opciones."""
    POINTS_FOR_CORRECT = 10

    def prepare_round_data(self, round_index: int) -> pd.Series:
        return self.data.iloc[round_index]

    def display_instructions(self):
        st.info(f"{self.t.get('minigame_prefix', 'Minijuego:')} {self.game_title}", icon="🎮")

    def display_game_body(self, round_data: pd.Series):
        st.write(round_data['question'])
        return st.radio(
            self.t.get('choose_your_answer', "Elige tu respuesta:"),
            options=round_data['options'],
            key=f"radio_{self.id}_{round_data.name}",
            label_visibility="collapsed"
        )

    def calculate_score(self, user_answer, round_data: pd.Series) -> tuple[int, bool]:
        is_correct = (user_answer == round_data['correct_answer'])
        points = self.POINTS_FOR_CORRECT if is_correct else 0
        return points, is_correct

    def display_round_feedback(self, round_result: dict, round_number: int):
        data = round_result['round_data']
        if round_result['was_correct']:
            st.success(f"¡Correcto! La respuesta era **{data['correct_answer']}**.", icon="✅")
        else:
            st.error(f"Tu respuesta fue **{round_result['user_answer']}**, pero la correcta era **{data['correct_answer']}**.", icon="❌")

class DataDuelMinigame(Minigame):
    """Compara dos ítems y el jugador debe adivinar cuál es mayor."""
    POINTS_FOR_CORRECT = 10

    def __init__(self, *, comparison_func: Callable[[Any, Any], bool] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.comparison_func = comparison_func

    def display_instructions(self):
        st.subheader(f"⚔️ {self.t.get('data_duel_title', 'Duelo de Datos')}")

    def prepare_round_data(self, round_index: int) -> dict:
        sample = self.data.sample(2, replace=False)
        item1, item2 = sample.iloc[0], sample.iloc[1]
        
        if self.comparison_func:
            winner_is_item1 = self.comparison_func(item1['Valor'], item2['Valor'])
        else:
            winner_is_item1 = item1['Valor'] > item2['Valor']
        
        correct_option = item1['Nombre'] if winner_is_item1 else item2['Nombre']
        
        return {
            "option1": item1['Nombre'], "value1": item1['Valor'],
            "option2": item2['Nombre'], "value2": item2['Valor'],
            "correct_option": correct_option,
            "question_text": self.t.get('duel_question', "¿Cuál tiene un valor mayor?")
        }

    # REFACTOR: Ya no es necesario, este juego no usa un `st.form`.
    def display_game_body(self, round_data: dict): pass

    # REFACTOR: Se sobreescribe solo la UI de envío para usar botones.
    def _render_submission_ui(self, round_data: dict):
        st.markdown(f"##### {round_data['question_text']}")
        
        col1, col2 = st.columns(2)
        user_choice = None
        
        with col1:
            if st.button(f"**{round_data['option1']}**", key=f"btn_{self.id}_{round_data['option1']}", use_container_width=True):
                user_choice = round_data['option1']
        with col2:
            if st.button(f"**{round_data['option2']}**", key=f"btn_{self.id}_{round_data['option2']}", use_container_width=True):
                user_choice = round_data['option2']

        if user_choice:
            self._process_submission(user_choice, round_data)

    def calculate_score(self, user_answer, round_data: dict) -> tuple[int, bool]:
        is_correct = (user_answer == round_data['correct_option'])
        return (self.POINTS_FOR_CORRECT, True) if is_correct else (0, False)

    def display_round_feedback(self, round_result: dict, round_number: int):
        with st.container(border=True):
            data = round_result['round_data']
            icon = "✅" if round_result['was_correct'] else "❌"
            st.markdown(f"**{self.t.get('round', 'Ronda')} {round_number}:** {data['question_text']} {icon}")
            
            if not round_result['was_correct']:
                st.write(f"{self.t.get('your_choice', 'Tu elección')}: `{round_result['user_answer']}`")
            
            st.info(
                f"**{self.t.get('correct_answer', 'Respuesta correcta')}: `{data['correct_option']}`**\n\n"
                f"`{data['option1']}`: **{data['value1']}**\n\n"
                f"`{data['option2']}`: **{data['value2']}**"
            )

class ClassifierMinigame(Minigame):
    """Ordena una lista de ítems de forma perfecta y gana puntos extra."""
    POINTS_PER_CORRECT_POSITION = 15
    POINTS_PER_ADJACENT = 5
    PERFECT_BONUS = 25
    
    def __init__(self, *, difficulty: int = 5, sorting_func: Callable[[pd.DataFrame], pd.DataFrame] | None = None, **kwargs):
        super().__init__(num_rounds=1, **kwargs)
        self.difficulty = min(difficulty, len(self.data))
        self.sorter = sorting_func if sorting_func else lambda df: df.sort_values(by='value', ascending=False)
        self.value_map = pd.Series(self.data.value.values, index=self.data.name).to_dict()

    def display_instructions(self):
        st.subheader(f"📊 {self.t.get('classifier_title', 'El Clasificador')}")
        st.info(self.t.get('classifier_drag_info', "💡 Arrastra los elementos para ordenarlos de mayor a menor."), icon="ℹ️")

    def prepare_round_data(self, round_index: int) -> dict:
        sample_df = self.data.sample(n=self.difficulty, replace=False)
        sorted_sample_df = self.sorter(sample_df)
        return {
            'items_to_sort': sample_df['name'].tolist(),
            'correct_order': sorted_sample_df['name'].tolist()
        }

    def display_game_body(self, round_data: dict):
        return sort_items(round_data['items_to_sort'], direction='vertical')
    
    def calculate_score(self, user_answer: list, round_data: dict) -> tuple[int, bool]:
        correct_order = round_data['correct_order']
        score = 0
        perfect = (user_answer == correct_order)
        
        for i, item in enumerate(user_answer):
            if item == correct_order[i]:
                score += self.POINTS_PER_CORRECT_POSITION
            elif item in correct_order and abs(i - correct_order.index(item)) == 1:
                score += self.POINTS_PER_ADJACENT
        
        if perfect:
            score += self.PERFECT_BONUS
            
        return score, perfect

    def display_round_feedback(self, round_result: dict, round_number: int):
        with st.container(border=True):
            user_order = round_result['user_answer']
            correct_order = round_result['round_data']['correct_order']
            
            st.markdown(f"**{self.t.get('results_title', 'Resultados del Clasificador')}**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{self.t.get('your_order', 'Tu Orden')}**")
                for i, item in enumerate(user_order):
                    mark = "✅" if item == correct_order[i] else "➖"
                    value_str = f"({self.value_map.get(item, 'N/A')})"
                    st.markdown(f"`{i+1}.` {mark} {item} *{value_str}*")
            with col2:
                st.write(f"**{self.t.get('correct_order_label', 'Orden Correcto')}**")
                for i, item in enumerate(correct_order):
                    value_str = f"({self.value_map.get(item, 'N/A')})"
                    st.markdown(f"`{i+1}.` ✅ {item} *{value_str}*")

class OracleMinigame(Minigame):
    """Predice la tendencia futura de una serie temporal."""
    POINTS_FOR_CORRECT_PREDICTION = 25
    
    def __init__(self, *, comparison_func: Callable[[list], str] = trend_comparison, **kwargs):
        super().__init__(**kwargs)
        self.comparison_func = comparison_func

    def display_instructions(self):
        st.subheader(f"🔮 {self.t.get('oracle_title', 'El Oráculo de la Matrícula')}")

    def prepare_round_data(self, round_index: int) -> pd.Series:
        return self.data.iloc[round_index]

    def display_game_body(self, round_data: pd.Series):
        st.markdown(f"**{round_data['Nombre']}:** {self.t.get('oracle_question', 'Observa la evolución y predice la tendencia para el próximo año.')}")
        chart_df = pd.DataFrame({'x': round_data['Eje_x'][:-1], 'y': round_data['Eje_y'][:-1]})
        fig = px.line(chart_df, x='x', y='y', markers=True, template="plotly_dark")
        fig.update_layout(
            title=self.t.get('oracle_chart_title', "Evolución... ¿Qué pasará después?"),
            xaxis_title=self.t.get('year', "Año"),
            yaxis_title=self.t.get('enrollment', "Matrícula")
        )
        st.plotly_chart(fig, use_container_width=True)

    # REFACTOR: UI de envío con botones en lugar de radio.
    def _render_submission_ui(self, round_data: pd.Series):
        self.display_game_body(round_data) # Primero muestra el gráfico
        
        st.write(self.t.get('predict_trend_prompt', "Elige tu predicción:"))
        cols = st.columns(3)
        user_prediction = None
        
        button_map = {
            'up': {'label': self.t.get('oracle_choice_up', 'Subirá'), 'icon': '📈'},
            'stable': {'label': self.t.get('oracle_choice_stable', 'Estable'), 'icon': '➖'},
            'down': {'label': self.t.get('oracle_choice_down', 'Bajará'), 'icon': '📉'}
        }
        
        if cols[0].button(f"{button_map['up']['label']} {button_map['up']['icon']}", use_container_width=True): user_prediction = 'up'
        if cols[1].button(f"{button_map['stable']['label']} {button_map['stable']['icon']}", use_container_width=True): user_prediction = 'stable'
        if cols[2].button(f"{button_map['down']['label']} {button_map['down']['icon']}", use_container_width=True): user_prediction = 'down'

        if user_prediction:
            self._process_submission(user_prediction, round_data)

    def calculate_score(self, user_answer, round_data: pd.Series) -> tuple[int, bool]:
        actual_trend = self.comparison_func(round_data['Eje_y'])
        is_correct = (user_answer == actual_trend)
        return self.POINTS_FOR_CORRECT_PREDICTION if is_correct else 0, is_correct

    def display_round_feedback(self, round_result: dict, round_number: int):
        with st.container(border=True):
            user_prediction, data = round_result['user_answer'], round_result['round_data']
            actual_trend = self.comparison_func(data['Eje_y'])
            icon = "✅" if round_result['was_correct'] else "❌"
            
            st.markdown(f"**{self.t.get('round', 'Ronda')} {round_number} ({data['Nombre']}):** {icon}")
            
            map_pred_text = {
                'up': f"{self.t.get('oracle_choice_up', 'Subirá')} 📈",
                'stable': f"{self.t.get('oracle_choice_stable', 'Estable')} ➖",
                'down': f"{self.t.get('oracle_choice_down', 'Bajará')} 📉"
            }
            
            st.write(f"{self.t.get('your_prediction', 'Tu predicción')}: **{map_pred_text[user_prediction]}**")
            st.write(f"{self.t.get('actual_result', 'Resultado real')}: **{map_pred_text[actual_trend]}**")
            
            # Gráfico de feedback mejorado
            chart_df = pd.DataFrame({'x': data['Eje_x'], 'y': data['Eje_y']})
            fig = px.line(chart_df, x='x', y='y', markers=True, template="plotly_dark")
            fig.add_shape(type="line",
                x0=chart_df['x'].iloc[-2], y0=chart_df['y'].iloc[-2],
                x1=chart_df['x'].iloc[-1], y1=chart_df['y'].iloc[-1],
                line=dict(color="yellow", width=4, dash="dot"))
            fig.update_layout(
                title=self.t.get('oracle_feedback_chart_title', "Resultado Completo Revelado"),
                xaxis_title=self.t.get('year', "Año"),
                yaxis_title=self.t.get('enrollment', "Matrícula")
            )
            st.plotly_chart(fig, use_container_width=True)

# Testeo
if __name__ == "__main__":
    from game_engine import GameController
    st.set_page_config(layout="wide"); st.title("Test de Minijuegos (Final)")
    game_controller = GameController(translation={'history_item_text': "{icon} **{game_title}**: *+{points_earned} pts*"})
    #game_controller.update_states()
    game_controller.display_mode_toggle()
    with st.sidebar: game_controller.display_score_panel()
    def cb(): st.success("Contenido del análisis.")

    tab1, tab2, tab3 = st.tabs(["Duelo de Datos", "El Clasificador", "El Oráculo"])

    with tab1:
        st.header("1. Duelo de Datos")
        duel_df = pd.DataFrame({'Nombre': ['UCLV', 'UO', 'Medicina', 'Derecho'], 'Valor': [20000, 18000, 35000, 8000]})
        DataDuelMinigame(id="duel_test", game_title="Duelos", data=duel_df, num_rounds=3, content_callback=cb).render()

    with tab2:
        st.header("2. El Clasificador (Con Aleatoriedad y Dificultad)")
        # DataFrame con más datos de los que se usarán
        classifier_data = {
            'name': ['Medicina', 'Derecho', 'Ing. Informática', 'Psicología', 'Arquitectura', 'Contabilidad', 'Periodismo', 'Biología'],
            'value': [35889, 8500, 25000, 15000, 7500, 18000, 6000, 9500]
        }
        classifier_df = pd.DataFrame(classifier_data)

        # Ejemplo de función de ordenamiento personalizada (ascendente)
        custom_sorter = lambda df: df.sort_values(by='value', ascending=True)

        ClassifierMinigame(
            id="classifier_test", 
            game_title="El Ranking Aleatorio",
            data=classifier_df, 
            content_callback=cb,
            difficulty=3
        ).render()

    with tab3:
        st.header("3. El Oráculo")
        oracle_df = pd.DataFrame({
            'Nombre': ['Carrera A', 'Carrera B'],
            'Eje_x': [[20, 21, 22, 23, 24], [20, 21, 22, 23, 24]],
            'Eje_y': [[100, 150, 130, 110, 90], [50, 55, 65, 80, 110]]
        })
        st.dataframe(oracle_df)
        OracleMinigame(id="oracle_test", game_title="Predicciones", data=oracle_df, num_rounds=2, content_callback=cb).render()