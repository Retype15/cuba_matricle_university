# --- START OF FILE game_engine.py ---

import streamlit as st
from abc import ABC, abstractmethod
from typing import Callable, Any, Dict
import pandas as pd

# ----------------- Controller de Gamificación -----------------

class GameController:
    """
    Gestiona el estado global de la gamificación en la aplicación.
    """
    def __init__(self, translation: Dict[str, str] | None = None):
        self.t = translation or {}
        if 'gamification' not in st.session_state:
            st.session_state.gamification = {
                "global_score": 0,
                "game_mode": True,
                "history": [],
                "registered_games": set()
            }
        if 'game_mode_toggle_state' not in st.session_state:
            st.session_state.game_mode_toggle_state = True
        st.session_state.GameController = self
        self.update_states()
        


    def _full_reset(self):
        """Resetea la puntuación, el historial y el estado de todos los juegos registrados."""
        st.session_state.gamification['global_score'] = 0
        st.session_state.gamification['history'] = []
        for id in st.session_state.gamification.get('registered_games', set()):
            state_key = f"game_{id}_state"
            if state_key in st.session_state:
                del st.session_state[state_key]

    def _handle_mode_change(self):
        """Callback para el widget toggle que actualiza el estado del widget."""
        st.session_state.game_mode_toggle_state = st.session_state.get('game_mode_toggle_widget', True)

    def update_states(self):
        """
        Sincroniza el estado lógico del modo juego con el estado del widget,
        mostrando un diálogo de confirmación si es necesario.
        """
        logical_mode = st.session_state.gamification['game_mode']
        widget_mode = st.session_state.game_mode_toggle_state
        if logical_mode == widget_mode:
            return

        if widget_mode is True:  # Reactivando el modo juego
            st.session_state.gamification['game_mode'] = True
            self._full_reset()
            st.rerun()
        else:  # Desactivando el modo juego
            @st.dialog(self.t.get('confirm_deactivation_title', "Confirmar Desactivación"))
            def show_confirmation_dialog():
                st.warning(self.t.get('confirm_deactivation_warning', "¿Seguro que quieres desactivar el Modo Juego?"), icon="🤔")
                st.write(self.t.get('confirm_deactivation_text', "Dejarás de ver los minijuegos interactivos y perderás tu progreso actual."))
                c1, c2 = st.columns(2)
                if c1.button(self.t.get('confirm_button', "Confirmar"), use_container_width=True, type="primary"):
                    self._deactivate_game_mode()
                if c2.button(self.t.get('cancel_button', "Cancelar"), use_container_width=True):
                    st.session_state.game_mode_toggle_state = True # Revertir visualmente
                    st.rerun()

            show_confirmation_dialog()

    def _deactivate_game_mode(self):
        """Pone el modo juego en False y fuerza un rerun."""
        st.session_state.gamification['game_mode'] = False
        st.session_state.game_mode_toggle_state = False
        st.rerun()

    def display_mode_toggle(self, *, where: Callable = st.sidebar):
        """Muestra el toggle para activar/desactivar el modo juego."""
        where.toggle(
            self.t.get('game_mode_label', '**Modo Juego**'),
            key="game_mode_toggle_widget",
            value=st.session_state.game_mode_toggle_state,
            on_change=self._handle_mode_change,
            help=self.t.get('toggle_help', "Activa/desactiva los minijuegos interactivos.")
        )

    def display_score_panel(self, where: Callable = st.sidebar):
        """Muestra el panel de puntuación y el historial si el modo juego está activo."""
        if not st.session_state.gamification.get('game_mode', False):
            return
        where.header(self.t.get('progress_header', "🏆 Tu Progreso"))
        if where.button(self.t.get('reset_progress_button', "Reiniciar Progreso"), use_container_width=True, type="secondary"):
            self._full_reset()
            st.rerun()
        score = st.session_state.gamification['global_score']
        games_played = len(st.session_state.gamification['history'])
        c1, c2 = where.columns(2)
        c1.metric(self.t.get('points_metric_label', "Puntos"), score)
        c2.metric(self.t.get('games_metric_label', "Juegos"), games_played)
        with where.expander(self.t.get('history_expander_label', "Ver Historial de Partidas")):
            history = st.session_state.gamification['history']
            if not history:
                st.caption(self.t.get('history_empty', "Aún no has jugado. ¡Anímate!"))
            else:
                for item in reversed(history):
                    icon = "✅" if item['was_correct'] else "❌"
                    text = self.t.get(
                        'history_item_text',
                        "{icon} **{game_title}**: *+{points_earned} pts*"
                    ).format(icon=icon, game_title=item['game_title'], points_earned=item['points_earned'])
                    st.markdown(text)

    def register_game(self, id: str):
        st.session_state.gamification['registered_games'].add(id)

    def record_game_result(self, game_title: str, points_earned: int, was_correct: bool):
        st.session_state.gamification['global_score'] += points_earned
        st.session_state.gamification['history'].append({
            "game_title": game_title,
            "points_earned": points_earned,
            "was_correct": was_correct
        })

# ----------------- Clase Base para Minijuegos -----------------

class Minigame(ABC):
    """Clase base abstracta para todos los minijuegos."""
    def __init__(self, id: str, game_title: str, data: pd.DataFrame, content_callback: Callable, num_rounds: int = 1, translation:dict={}):
        self.id = id
        self.game_title = game_title
        if 'GameController' in st.session_state: self.controller = st.session_state.GameController
        else: raise Exception('Must define GameController first!')
        self.t = translation
        self.data = data
        self.content_callback = content_callback
        self.num_rounds = min(num_rounds, len(data)) if num_rounds > 0 else 1
        self.state_key = f"game_{self.id}_state"

        self.controller.register_game(self.id)
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {
                "current_round": 0,
                "game_over": False,
                "round_results": [],
                "total_score": 0,
                "current_round_context": None
            }

    @abstractmethod
    def display_instructions(self):
        """Muestra las instrucciones del juego."""
        pass

    @abstractmethod
    def display_game_body(self, round_data: Any):
        """
        Muestra la interfaz principal del juego para una ronda.
        Debe devolver la respuesta del usuario.
        """
        pass

    @abstractmethod
    def calculate_score(self, user_answer, round_data: Any) -> tuple[int, bool]:
        """Calcula la puntuación y si la respuesta fue correcta."""
        pass

    @abstractmethod
    def display_round_feedback(self, round_result: dict, round_number: int):
        """Muestra el feedback para una ronda específica."""
        pass
    
    @abstractmethod
    def prepare_round_data(self, round_index: int) -> Any:
        """Prepara los datos necesarios para una ronda específica."""
        pass

    def display_feedback(self):
        """Muestra el feedback final cuando el juego termina."""
        state = st.session_state[self.state_key]
        st.subheader(self.t.get('feedback_game_over_title', "🏁 ¡Desafío Completado!"))
        st.success(self.t.get('feedback_game_over_text', "Has obtenido un total de **{total_score}** puntos.").format(total_score=state['total_score']), icon="🎉")
        if self.num_rounds > 1:
            with st.expander(self.t.get('see_round_summary', "Ver resumen detallado de rondas")):
                for i, result in enumerate(state['round_results']):
                    self.display_round_feedback(result, i + 1)

    def _process_submission(self, user_answer, round_data):
        """Procesa la respuesta del usuario, actualiza el estado y avanza el juego."""
        state = st.session_state[self.state_key]
        score, was_correct = self.calculate_score(user_answer, round_data)
        state['round_results'].append({"score": score, "was_correct": was_correct, "user_answer": user_answer, "round_data": round_data})
        state['total_score'] += score
        state['current_round'] += 1
        state['current_round_context'] = None # Limpiar para la siguiente ronda

        if state['current_round'] >= self.num_rounds:
            state['game_over'] = True
            self.controller.record_game_result(game_title=self.game_title, points_earned=state['total_score'], was_correct=any(r['was_correct'] for r in state['round_results']))
        
        st.rerun()

    def _render_submission_ui(self, round_data: Any):
        """
        Método 'virtual' para renderizar el cuerpo y el mecanismo de envío.
        La implementación por defecto usa st.form, ideal para widgets como radio o sortables.
        Las subclases pueden sobrescribirlo para usar otros mecanismos como botones directos.
        """
        with st.form(key=f"form_{self.id}_{st.session_state[self.state_key]['current_round']}"):
            user_answer = self.display_game_body(round_data)
            submit_label = self.t.get('submit_button_label', "¡Comprobar!")
            if st.form_submit_button(submit_label, use_container_width=True):
                self._process_submission(user_answer, round_data)

    def render(self):
        """Método principal para renderizar el minijuego completo."""
        if not st.session_state.gamification.get('game_mode', False):
            self.content_callback()
            return

        state = st.session_state[self.state_key]
        if state["game_over"]:
            self.display_feedback()
            st.markdown("---")
            st.subheader(self.t.get('detailed_analysis_revealed', "Análisis Detallado Revelado"))
            self.content_callback()
            return

        self.display_instructions()

        if self.num_rounds > 1:
            current_round_index = state['current_round']
            st.info(f"{self.t.get('round', 'Ronda')} {current_round_index + 1} / {self.num_rounds}", icon="🚩")

        # --- REFACTOR: Lógica de caché de ronda centralizada ---
        # Prepara los datos para la ronda actual y los guarda en el estado para
        # evitar que cambien si la app se rerenderiza por otra razón.
        if state.get('current_round_context') is None:
            state['current_round_context'] = self.prepare_round_data(state['current_round'])
            st.rerun()

        round_data = state['current_round_context']
        
        # --- REFACTOR: Delegación del renderizado de la UI de envío ---
        self._render_submission_ui(round_data)